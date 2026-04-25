"""Shared type aliases for the Python rewrite."""

from __future__ import annotations

from pathlib import Path
from typing import NewType

NodeId = NewType("NodeId", int)
EdgeId = NewType("EdgeId", int)
ProjectId = NewType("ProjectId", int)
type PathLike = str | Path
