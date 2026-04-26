"""Persistent file-line bookmarks for editor workflows."""

from __future__ import annotations

import builtins
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import NewType

BookmarkId = NewType("BookmarkId", int)


@dataclass(frozen=True, slots=True)
class Bookmark:
    """A saved source location with optional tag and note metadata."""

    id: BookmarkId
    file: str
    line: int
    tag: str
    note: str
    created_at: str


class BookmarkStore:
    """SQLite-backed project bookmark storage."""

    def __init__(self, db_path: Path | str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def add(self, file: str, line: int, tag: str, note: str) -> BookmarkId:
        """Add a bookmark and return its generated id."""
        if line <= 0:
            raise ValueError("bookmark line must be one-based")
        created_at = datetime.now(UTC).isoformat(timespec="seconds")
        with self._connect() as connection:
            cursor = connection.execute(
                (
                    "INSERT INTO bookmarks(file, line, tag, note, created_at) "
                    "VALUES (?, ?, ?, ?, ?);"
                ),
                (file, line, tag.strip(), note.strip(), created_at),
            )
            connection.commit()
            row_id = cursor.lastrowid
            if row_id is None:
                raise RuntimeError("bookmark insert did not return a row id")
            return BookmarkId(row_id)

    def list(self) -> builtins.list[Bookmark]:
        """Return all bookmarks sorted by creation order."""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, file, line, tag, note, created_at "
                "FROM bookmarks ORDER BY created_at DESC, id DESC;"
            ).fetchall()
        return [self._row_to_bookmark(row) for row in rows]

    def list_by_tag(self, tag: str) -> builtins.list[Bookmark]:
        """Return bookmarks whose tag exactly matches ``tag``."""
        with self._connect() as connection:
            rows = connection.execute(
                (
                    "SELECT id, file, line, tag, note, created_at "
                    "FROM bookmarks WHERE tag = ? ORDER BY created_at DESC, id DESC;"
                ),
                (tag,),
            ).fetchall()
        return [self._row_to_bookmark(row) for row in rows]

    def list_by_file(self, file: str) -> builtins.list[Bookmark]:
        """Return bookmarks for a source file sorted by line."""
        with self._connect() as connection:
            rows = connection.execute(
                (
                    "SELECT id, file, line, tag, note, created_at "
                    "FROM bookmarks WHERE file = ? ORDER BY line ASC, id ASC;"
                ),
                (file,),
            ).fetchall()
        return [self._row_to_bookmark(row) for row in rows]

    def remove(self, bm_id: BookmarkId) -> None:
        """Remove a bookmark if it exists."""
        with self._connect() as connection:
            connection.execute("DELETE FROM bookmarks WHERE id = ?;", (int(bm_id),))
            connection.commit()

    def tags(self) -> tuple[str, ...]:
        """Return known non-empty tags in display order."""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT DISTINCT tag FROM bookmarks WHERE tag != '' ORDER BY tag ASC;"
            ).fetchall()
        return tuple(str(row[0]) for row in rows)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS bookmarks ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "file TEXT NOT NULL, "
                "line INTEGER NOT NULL, "
                "tag TEXT NOT NULL DEFAULT '', "
                "note TEXT NOT NULL DEFAULT '', "
                "created_at TEXT NOT NULL"
                ");"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_bookmarks_tag ON bookmarks(tag);"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_bookmarks_file_line ON bookmarks(file, line);"
            )
            connection.commit()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _row_to_bookmark(self, row: sqlite3.Row) -> Bookmark:
        return Bookmark(
            id=BookmarkId(int(str(row[0]))),
            file=str(row[1]),
            line=int(str(row[2])),
            tag=str(row[3]),
            note=str(row[4]),
            created_at=str(row[5]),
        )
