"""Schema compatibility helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from sourcetrail_remake.db.schema import REQUIRED_TABLES, ensure_tables


def missing_required_tables(db_path: Path) -> list[str]:
    """Return missing required tables for a generated SourcetrailDB file."""
    with sqlite3.connect(db_path) as connection:
        return ensure_tables(connection, REQUIRED_TABLES)
