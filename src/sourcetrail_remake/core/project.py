"""Project model types."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class ProjectInfo:
    """Minimal project description used in Phase 0."""

    name: str
    root: Path
    database_path: Path | None = None
