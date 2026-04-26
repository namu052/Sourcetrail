"""Rope-backed smart rename service."""

from __future__ import annotations

from dataclasses import dataclass
import difflib
from pathlib import Path
import sqlite3
from typing import Any

from rope.base.change import Change, ChangeContents, ChangeSet
from rope.base.project import Project
from rope.base.resources import File
from rope.refactor.rename import Rename

from sourcetrail_remake.core.types import NodeId


@dataclass(frozen=True, slots=True)
class RenameTarget:
    """Source position that identifies the symbol being renamed."""

    node_id: NodeId
    file_path: Path
    line: int
    column: int
    old_name: str


@dataclass(frozen=True, slots=True)
class FileChange:
    """Preview of one changed file."""

    path: Path
    old_text: str
    new_text: str
    diff: str


@dataclass(frozen=True, slots=True)
class RenamePreview:
    """Computed rename changes before writing to disk."""

    node_id: NodeId
    old_name: str
    new_name: str
    affected_files: tuple[Path, ...]
    changes: tuple[FileChange, ...]
    rope_changes: ChangeSet


class RopeRenameService:
    """Open a Rope project and resolve Sourcetrail node IDs to rename targets."""

    def __init__(self, project_root: Path, db_path: Path | None = None) -> None:
        self.project_root = Path(project_root).resolve()
        self.db_path = None if db_path is None else Path(db_path).resolve()

    def open_project(self) -> Project:
        """Return a Rope project rooted at the indexed project directory."""
        return Project(str(self.project_root), ropefolder=".ropeproject")

    def file_resource(self, project: Project, file_path: Path) -> File:
        """Return the Rope file resource for an absolute or project-relative path."""
        path = Path(file_path)
        relative_path = path if not path.is_absolute() else path.relative_to(self.project_root)
        return project.get_file(relative_path.as_posix())

    def preview(self, node_id: NodeId, new_name: str) -> RenamePreview:
        """Compute affected files and per-file diffs for a node rename."""
        if self.db_path is None:
            raise ValueError("db_path is required for node-based rename preview")

        target = self._load_target(node_id)
        project = self.open_project()
        try:
            resource = self.file_resource(project, target.file_path)
            offset = self._offset_from_line_column(target.file_path, target.line, target.column)
            rope_changes = Rename(project, resource, offset).get_changes(new_name, docs=True)
            file_changes = tuple(self._file_changes(rope_changes))
            return RenamePreview(
                node_id=node_id,
                old_name=target.old_name,
                new_name=new_name,
                affected_files=tuple(change.path for change in file_changes),
                changes=file_changes,
                rope_changes=rope_changes,
            )
        finally:
            project.close()

    def _load_target(self, node_id: NodeId) -> RenameTarget:
        assert self.db_path is not None
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                (
                    "SELECT file.path, source_location.start_line, "
                    "source_location.start_column, node.serialized_name "
                    "FROM occurrence "
                    "INNER JOIN source_location "
                    "ON source_location.id = occurrence.source_location_id "
                    "INNER JOIN file ON file.id = source_location.file_node_id "
                    "INNER JOIN node ON node.id = occurrence.element_id "
                    "WHERE occurrence.element_id = ? "
                    "ORDER BY source_location.start_line, source_location.start_column "
                    "LIMIT 1;"
                ),
                (int(node_id),),
            ).fetchone()
        if row is None:
            raise LookupError(f"node {int(node_id)} has no source occurrence")
        return RenameTarget(
            node_id=node_id,
            file_path=Path(str(row[0])).resolve(),
            line=int(row[1]),
            column=int(row[2]),
            old_name=str(row[3]).rsplit(".", maxsplit=1)[-1],
        )

    def _file_changes(self, changes: ChangeSet) -> list[FileChange]:
        previews: list[FileChange] = []
        for change in self._iter_changes(changes):
            if not isinstance(change, ChangeContents):
                continue
            path = self.project_root / Path(change.resource.path)
            old_text = change.resource.read()
            new_text = str(change.new_contents)
            previews.append(
                FileChange(
                    path=path.resolve(),
                    old_text=old_text,
                    new_text=new_text,
                    diff=self._unified_diff(path, old_text, new_text),
                )
            )
        return previews

    def _iter_changes(self, change: Change) -> list[Change]:
        nested = getattr(change, "changes", None)
        if nested is None:
            return [change]
        result: list[Change] = []
        for child in _as_change_list(nested):
            result.extend(self._iter_changes(child))
        return result

    def _unified_diff(self, path: Path, old_text: str, new_text: str) -> str:
        return "".join(
            difflib.unified_diff(
                old_text.splitlines(keepends=True),
                new_text.splitlines(keepends=True),
                fromfile=f"a/{path.relative_to(self.project_root).as_posix()}",
                tofile=f"b/{path.relative_to(self.project_root).as_posix()}",
            )
        )

    def _offset_from_line_column(self, file_path: Path, line: int, column: int) -> int:
        text = file_path.read_text(encoding="utf-8")
        lines = text.splitlines(keepends=True)
        if line < 1 or line > len(lines):
            raise ValueError(f"line {line} is outside {file_path}")
        return sum(len(item) for item in lines[: line - 1]) + column


def _as_change_list(changes: Any) -> list[Change]:
    return [change for change in changes if isinstance(change, Change)]
