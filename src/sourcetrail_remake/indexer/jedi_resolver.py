"""Jedi wrapper used by the indexer service."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import jedi

from sourcetrail_remake.core.types import NameOccurrence, NodeType, ParsedSymbol, ResolvedTarget, SourceLocation

JEDI_TYPE_TO_NODE_TYPE: dict[str, NodeType] = {
    "class": NodeType.NODE_CLASS,
    "function": NodeType.NODE_FUNCTION,
    "instance": NodeType.NODE_GLOBAL_VARIABLE,
    "module": NodeType.NODE_MODULE,
    "namespace": NodeType.NODE_NAMESPACE,
    "param": NodeType.NODE_GLOBAL_VARIABLE,
    "path": NodeType.NODE_FILE,
    "property": NodeType.NODE_FIELD,
    "statement": NodeType.NODE_GLOBAL_VARIABLE,
}


def map_name_type(name_type: str, *, parent: ParsedSymbol | None = None, is_builtin: bool = False) -> NodeType:
    """Map Jedi's name types onto Sourcetrail-compatible node types."""
    if is_builtin:
        return NodeType.NODE_BUILTIN_TYPE
    if name_type == "function" and parent is not None and parent.node_type == NodeType.NODE_CLASS:
        return NodeType.NODE_METHOD
    if name_type == "statement" and parent is not None and parent.node_type == NodeType.NODE_CLASS:
        return NodeType.NODE_FIELD
    return JEDI_TYPE_TO_NODE_TYPE.get(name_type, NodeType.NODE_SYMBOL)


class JediResolver:
    """Wrap common Jedi calls behind a single module boundary."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        cache_directory = Path(tempfile.gettempdir()) / "sourcetrail_remake" / "jedi-cache"
        cache_directory.mkdir(parents=True, exist_ok=True)
        jedi.settings.cache_directory = str(cache_directory)
        self.project = jedi.Project(
            path=str(self.project_root),
            sys_path=[str(self.project_root), *sys.path],
        )
        self._script_cache: dict[Path, tuple[str, jedi.Script]] = {}

    def collect_names(
        self,
        source: str,
        path: Path,
        *,
        definitions: bool,
        references: bool,
    ) -> list[NameOccurrence]:
        script = self._script(source, path)
        names: list[NameOccurrence] = []
        for name in script.get_names(
            all_scopes=True,
            definitions=definitions,
            references=references,
        ):
            if name.type == "keyword" or name.line is None or name.column is None:
                continue
            module_path = Path(str(name.module_path)).resolve() if name.module_path else None
            if module_path is not None and module_path != Path(path).resolve():
                continue
            names.append(self._convert_name_occurrence(name, Path(path).resolve()))
        return names

    def goto(self, source: str, path: Path, line: int, column: int) -> list[ResolvedTarget]:
        script = self._script(source, path)
        return [self._convert_target(target) for target in script.goto(line=line, column=column)]

    def infer(self, source: str, path: Path, line: int, column: int) -> list[ResolvedTarget]:
        script = self._script(source, path)
        return [self._convert_target(target) for target in script.infer(line=line, column=column)]

    def get_references(
        self,
        source: str,
        path: Path,
        line: int,
        column: int,
        *,
        include_builtins: bool = False,
    ) -> list[NameOccurrence]:
        script = self._script(source, path)
        references: list[NameOccurrence] = []
        for name in script.get_references(line=line, column=column, include_builtins=include_builtins):
            if name.line is None or name.column is None:
                continue
            occurrence_path = Path(str(name.module_path)).resolve() if name.module_path else Path(path).resolve()
            references.append(self._convert_name_occurrence(name, occurrence_path))
        return references

    def _script(self, source: str, path: Path) -> jedi.Script:
        resolved_path = Path(path).resolve()
        cached = self._script_cache.get(resolved_path)
        if cached is not None and cached[0] == source:
            return cached[1]
        script = jedi.Script(code=source, path=str(resolved_path), project=self.project)
        self._script_cache[resolved_path] = (source, script)
        return script

    def _convert_name_occurrence(self, name: jedi.api.classes.Name, path: Path) -> NameOccurrence:
        assert name.line is not None
        assert name.column is not None
        return NameOccurrence(
            path=path,
            name=name.name,
            symbol_type=name.type,
            location=SourceLocation.from_name(line=name.line, column=name.column, name=name.name),
            is_definition=name.is_definition(),
            qualified_name=name.full_name,
        )

    def _convert_target(self, target: jedi.api.classes.Name) -> ResolvedTarget:
        module_path = Path(str(target.module_path)).resolve() if target.module_path else None
        return ResolvedTarget(
            name=target.name,
            symbol_type=target.type,
            qualified_name=target.full_name,
            path=module_path,
            line=target.line,
            column=target.column,
            is_builtin=target.in_builtin_module(),
        )
