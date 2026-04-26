"""Rope-backed smart rename service."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rope.base.project import Project
from rope.base.resources import File

from sourcetrail_remake.core.types import NodeId


@dataclass(frozen=True, slots=True)
class RenameTarget:
    """Source position that identifies the symbol being renamed."""

    node_id: NodeId
    file_path: Path
    line: int
    column: int
    old_name: str


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
