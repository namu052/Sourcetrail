"""Application service for building Sourcetrail-compatible indexes."""

from __future__ import annotations

import builtins
from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from sourcetrail_remake.core.types import (
    EdgeType,
    FileId,
    IndexResult,
    IndexingMode,
    NameOccurrence,
    NodeId,
    ParsedModule,
    ParsedSymbol,
)
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.indexer.jedi_resolver import JediResolver
from sourcetrail_remake.indexer.mappings import classify_edge_type
from sourcetrail_remake.indexer.parso_walker import ParsoWalker
from sourcetrail_remake.indexer.unsolved import UnsolvedSymbolTracker

IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "site-packages",
    "venv",
}
IGNORED_REFERENCE_NAMES = frozenset(dir(builtins)) | {"self", "cls"}


@dataclass(slots=True, frozen=True)
class _IndexedModule:
    parsed: ParsedModule
    file_id: FileId
    source_lines: tuple[str, ...]


class _ScopeLookup:
    def __init__(
        self,
        *,
        file_id: FileId,
        symbols: tuple[ParsedSymbol, ...],
        symbol_nodes: dict[str, NodeId],
    ) -> None:
        self._file_node_id = NodeId(int(file_id))
        self._symbol_nodes = symbol_nodes
        self._symbols = tuple(
            sorted(
                symbols,
                key=lambda symbol: (
                    symbol.scope_end_line - symbol.location.start_line,
                    symbol.scope_end_column - symbol.location.start_column,
                ),
            )
        )

    def resolve(self, *, line: int, column: int) -> NodeId:
        for symbol in self._symbols:
            if symbol.contains(line=line, column=column):
                return self._symbol_nodes[symbol.qualified_name]
        return self._file_node_id


class IndexerService:
    """Coordinate index creation for a Python project."""

    def __init__(self, project_root: Path, mode: IndexingMode):
        self.project_root = Path(project_root).resolve()
        self.mode = mode
        self.resolver = JediResolver(self.project_root)
        self.walker = ParsoWalker(self.project_root)

    def discover_python_files(self) -> list[Path]:
        files: list[Path] = []
        for path in self.project_root.rglob("*.py"):
            if any(part in IGNORED_DIRECTORIES for part in path.parts):
                continue
            if path.is_file():
                files.append(path.resolve())
        return sorted(files)

    def index(
        self,
        writer: DatabaseWriter,
        progress_cb: Callable[[int, int], None],
    ) -> IndexResult:
        started_at = perf_counter()
        writer.initialize_schema()
        files = self.discover_python_files()
        modules = self.walker.walk_project(files)
        if self.mode == "deep":
            result = self._index_shallow(modules, writer, progress_cb)
        else:
            result = self._index_shallow(modules, writer, progress_cb)
        return IndexResult(
            project_root=self.project_root,
            mode=self.mode,
            files_indexed=result.files_indexed,
            symbols_recorded=result.symbols_recorded,
            edges_recorded=result.edges_recorded,
            unsolved_symbols=result.unsolved_symbols,
            external_symbols=result.external_symbols,
            locations_recorded=result.locations_recorded,
            duration_seconds=perf_counter() - started_at,
        )

    def _index_shallow(
        self,
        modules: Iterable[ParsedModule],
        writer: DatabaseWriter,
        progress_cb: Callable[[int, int], None],
    ) -> IndexResult:
        indexed_modules: list[_IndexedModule] = []
        symbols_by_short_name: dict[str, list[ParsedSymbol]] = defaultdict(list)
        symbol_nodes: dict[str, NodeId] = {}

        for parsed in modules:
            file_id = writer.record_file(parsed.path, parsed.source)
            indexed_modules.append(
                _IndexedModule(
                    parsed=parsed,
                    file_id=file_id,
                    source_lines=tuple(parsed.source.splitlines()),
                )
            )
            for symbol in parsed.symbols:
                node_id = writer.record_symbol(
                    symbol.name,
                    symbol.node_type,
                    file_id,
                    symbol.location,
                    qualified_name=symbol.qualified_name,
                    access_kind=symbol.access,
                )
                symbol_nodes[symbol.qualified_name] = node_id
                symbols_by_short_name[symbol.name].append(symbol)

        for indexed in indexed_modules:
            for symbol in indexed.parsed.symbols:
                parent_node = (
                    symbol_nodes[symbol.parent_qualified_name]
                    if symbol.parent_qualified_name is not None
                    else NodeId(int(indexed.file_id))
                )
                writer.record_edge(
                    parent_node,
                    symbol_nodes[symbol.qualified_name],
                    EdgeType.EDGE_MEMBER,
                    file=indexed.file_id,
                    location=symbol.location,
                )

        unsolved_tracker = UnsolvedSymbolTracker()
        total = len(indexed_modules)
        for current, indexed in enumerate(indexed_modules, start=1):
            scope_lookup = _ScopeLookup(
                file_id=indexed.file_id,
                symbols=indexed.parsed.symbols,
                symbol_nodes=symbol_nodes,
            )
            references = self.resolver.collect_names(
                indexed.parsed.source,
                indexed.parsed.path,
                definitions=False,
                references=True,
            )
            for occurrence in references:
                if occurrence.name in IGNORED_REFERENCE_NAMES:
                    continue
                source_node = scope_lookup.resolve(
                    line=occurrence.location.start_line,
                    column=occurrence.location.start_column,
                )
                edge_type = self._edge_type_for_occurrence(indexed, occurrence)
                target_node = self._resolve_shallow_reference(
                    occurrence,
                    symbols_by_short_name,
                    symbol_nodes,
                )
                if target_node is None:
                    unsolved_tracker.register(
                        writer,
                        context_node=source_node,
                        name=occurrence.name,
                        file=indexed.file_id,
                        location=occurrence.location,
                        edge_type=edge_type,
                        reason="shallow_name_match_failed",
                        metadata={"path": str(indexed.parsed.path)},
                    )
                    continue
                writer.record_edge(
                    source_node,
                    target_node,
                    edge_type,
                    file=indexed.file_id,
                    location=occurrence.location,
                )
            progress_cb(current, total)

        summary = writer.summary()
        return IndexResult(
            project_root=self.project_root,
            mode="shallow",
            files_indexed=summary.files,
            symbols_recorded=summary.symbols,
            edges_recorded=summary.edges,
            unsolved_symbols=summary.unsolved,
            external_symbols=0,
            locations_recorded=summary.locations,
            duration_seconds=0.0,
        )

    def _resolve_shallow_reference(
        self,
        occurrence: NameOccurrence,
        symbols_by_short_name: dict[str, list[ParsedSymbol]],
        symbol_nodes: dict[str, NodeId],
    ) -> NodeId | None:
        candidates = symbols_by_short_name.get(occurrence.name)
        if not candidates:
            return None
        same_file_candidates = [symbol for symbol in candidates if symbol.path == occurrence.path]
        target = same_file_candidates[0] if same_file_candidates else candidates[0]
        return symbol_nodes[target.qualified_name]

    def _edge_type_for_occurrence(self, indexed: _IndexedModule, occurrence: NameOccurrence) -> EdgeType:
        line_number = occurrence.location.start_line - 1
        line_text = indexed.source_lines[line_number] if 0 <= line_number < len(indexed.source_lines) else ""
        return classify_edge_type(
            line_text,
            column=occurrence.location.start_column,
            name=occurrence.name,
        )
