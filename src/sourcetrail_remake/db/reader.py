"""Minimal read helpers for Smoke/PoC checks."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def read_meta(db_path: Path) -> dict[str, str]:
    """Return the current meta key/value mapping."""
    with sqlite3.connect(db_path) as connection:
        rows = connection.execute("SELECT key, value FROM meta").fetchall()
    return {key: value for key, value in rows}
