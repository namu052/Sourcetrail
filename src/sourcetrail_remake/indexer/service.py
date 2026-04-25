"""Application service for building Sourcetrail-compatible indexes."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from time import perf_counter

from sourcetrail_remake.core.types import IndexResult, IndexingMode
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.indexer.jedi_resolver import JediResolver

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


class IndexerService:
    """Coordinate index creation for a Python project."""

    def __init__(self, project_root: Path, mode: IndexingMode):
        self.project_root = Path(project_root).resolve()
        self.mode = mode
        self.resolver = JediResolver(self.project_root)

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
        """Initialize the target DB and return an empty indexing summary skeleton."""
        started_at = perf_counter()
        initialize_schema = getattr(writer, "initialize_schema", None)
        if initialize_schema is not None:
            initialize_schema()
        else:
            writer.initialize()
        files = self.discover_python_files()
        total = len(files)
        if total:
            progress_cb(total, total)
        return IndexResult(
            project_root=self.project_root,
            mode=self.mode,
            files_indexed=total,
            symbols_recorded=0,
            edges_recorded=0,
            unsolved_symbols=0,
            external_symbols=0,
            locations_recorded=0,
            duration_seconds=perf_counter() - started_at,
        )
