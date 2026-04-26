"""Rope-backed smart rename service."""

from __future__ import annotations

import ast
from collections.abc import Callable
from dataclasses import dataclass
import difflib
import keyword
from pathlib import Path
import sqlite3
from typing import Any

from rope.base.change import Change, ChangeContents, ChangeSet
from rope.base.project import Project
from rope.base.resources import File
from rope.refactor.rename import Rename

from sourcetrail_remake.core.types import NodeId
from sourcetrail_remake.refactor.undo import UndoEntry, UndoJournal, UndoRecord


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
    conflicts: tuple[ScopeConflict, ...]
    rope_changes: ChangeSet


@dataclass(frozen=True, slots=True)
class ScopeConflict:
    """A rename warning for a same-scope symbol collision or invalid target name."""

    path: Path
    line: int
    column: int
    message: str


@dataclass(frozen=True, slots=True)
class RenameResult:
    """Result of applying a rename preview."""

    node_id: NodeId
    old_name: str
    new_name: str
    changed_files: tuple[Path, ...]
    undo_record: UndoRecord | None = None


class RopeRenameService:
    """Open a Rope project and resolve Sourcetrail node IDs to rename targets."""

    def __init__(
        self,
        project_root: Path,
        db_path: Path | None = None,
        reindex_callback: Callable[[tuple[Path, ...]], None] | None = None,
    ) -> None:
        self.project_root = Path(project_root).resolve()
        self.db_path = None if db_path is None else Path(db_path).resolve()
        self.reindex_callback = reindex_callback
        self.undo_journal = UndoJournal(self.project_root)

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
        input_conflicts = self._validate_new_name(new_name)

        target = self._load_target(node_id)
        project = self.open_project()
        try:
            resource = self.file_resource(project, target.file_path)
            offset = self._offset_from_line_column(target.file_path, target.line, target.column)
            rope_changes = Rename(project, resource, offset).get_changes(
                new_name,
                docs=True,
                in_hierarchy=True,
            )
            file_changes = tuple(self._file_changes(rope_changes))
            return RenamePreview(
                node_id=node_id,
                old_name=target.old_name,
                new_name=new_name,
                affected_files=tuple(change.path for change in file_changes),
                changes=file_changes,
                conflicts=(*input_conflicts, *self._scope_conflicts(file_changes, new_name)),
                rope_changes=rope_changes,
            )
        finally:
            project.close()

    def apply(self, preview: RenamePreview) -> RenameResult:
        """Write previewed file contents and request index refresh."""
        undo_record = self.undo_journal.backup(
            tuple(UndoEntry(path=change.path, old_text=change.old_text) for change in preview.changes)
        )
        try:
            for change in preview.changes:
                change.path.write_text(change.new_text, encoding="utf-8")

            changed_files = preview.affected_files
            if self.reindex_callback is not None:
                self.reindex_callback(changed_files)
            return RenameResult(
                node_id=preview.node_id,
                old_name=preview.old_name,
                new_name=preview.new_name,
                changed_files=changed_files,
                undo_record=undo_record,
            )
        except Exception:
            self.undo_journal.restore(undo_record)
            raise

    def undo(self, result: RenameResult) -> None:
        """Restore files captured before apply."""
        if result.undo_record is None:
            raise ValueError("rename result has no undo record")
        self.undo_journal.restore(result.undo_record)

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

    def _validate_new_name(self, new_name: str) -> tuple[ScopeConflict, ...]:
        if new_name.isidentifier() and not keyword.iskeyword(new_name):
            return ()
        return (
            ScopeConflict(
                path=self.project_root,
                line=0,
                column=0,
                message=f"{new_name!r} is not a valid Python identifier",
            ),
        )

    def _scope_conflicts(
        self, file_changes: tuple[FileChange, ...], new_name: str
    ) -> tuple[ScopeConflict, ...]:
        conflicts: list[ScopeConflict] = []
        for file_change in file_changes:
            try:
                tree = ast.parse(file_change.new_text, filename=str(file_change.path))
            except SyntaxError as exc:
                conflicts.append(
                    ScopeConflict(
                        path=file_change.path,
                        line=exc.lineno or 0,
                        column=exc.offset or 0,
                        message=f"renamed file no longer parses: {exc.msg}",
                    )
                )
                continue
            conflicts.extend(_find_duplicate_bindings(file_change.path, tree, new_name))
        return tuple(conflicts)


def _as_change_list(changes: Any) -> list[Change]:
    return [change for change in changes if isinstance(change, Change)]


def _find_duplicate_bindings(path: Path, tree: ast.AST, name: str) -> list[ScopeConflict]:
    conflicts: list[ScopeConflict] = []
    for scope in ast.walk(tree):
        names: dict[str, list[ast.AST]] = {}
        if isinstance(scope, ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            body = scope.body
        else:
            continue

        for child in body:
            for bound_name, node in _bound_names(child):
                names.setdefault(bound_name, []).append(node)

        duplicate_nodes = names.get(name, [])
        if len(duplicate_nodes) > 1:
            node = duplicate_nodes[1]
            conflicts.append(
                ScopeConflict(
                    path=path,
                    line=getattr(node, "lineno", 0),
                    column=getattr(node, "col_offset", 0),
                    message=f"name {name!r} already exists in this scope",
                )
            )
    return conflicts


def _bound_names(node: ast.AST) -> list[tuple[str, ast.AST]]:
    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
        return [(node.name, node)]
    if isinstance(node, ast.Assign | ast.AnnAssign):
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        return [
            (target.id, target)
            for target in ast.walk(ast.Module(body=targets, type_ignores=[]))
            if isinstance(target, ast.Name) and isinstance(target.ctx, ast.Store)
        ]
    if isinstance(node, ast.arg):
        return [(node.arg, node)]
    if isinstance(node, ast.Import | ast.ImportFrom):
        return [(alias.asname or alias.name.split(".", maxsplit=1)[0], node) for alias in node.names]
    return []
