"""Runtime environment inspection helpers."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class EnvironmentInfo:
    """Describe the currently running Python environment."""

    python_executable: Path
    prefix: Path
    base_prefix: Path
    virtualenv_path: Path | None

    @property
    def is_virtualenv(self) -> bool:
        return self.virtualenv_path is not None


def detect_environment() -> EnvironmentInfo:
    """Inspect the active Python interpreter."""
    prefix = Path(sys.prefix)
    base_prefix = Path(getattr(sys, "base_prefix", sys.prefix))
    virtualenv_path = prefix if prefix != base_prefix else None
    return EnvironmentInfo(
        python_executable=Path(sys.executable),
        prefix=prefix,
        base_prefix=base_prefix,
        virtualenv_path=virtualenv_path,
    )
