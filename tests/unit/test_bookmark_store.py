"""Unit coverage for Week 21 bookmark persistence."""

from __future__ import annotations

import sqlite3

import pytest

from sourcetrail_remake.core.bookmarks import BookmarkStore


@pytest.mark.unit
def test_bookmark_store_creates_sqlite_table_and_filters(tmp_path) -> None:
    store = BookmarkStore(tmp_path / "project-bookmarks.sqlite")

    first_id = store.add("src/app.py", 10, "TODO", "check branch")
    second_id = store.add("src/app.py", 3, "REVIEW", "")
    third_id = store.add("src/other.py", 7, "TODO", "follow up")

    with sqlite3.connect(tmp_path / "project-bookmarks.sqlite") as connection:
        columns = [
            row[1]
            for row in connection.execute("PRAGMA table_info(bookmarks);").fetchall()
        ]
    assert columns == ["id", "file", "line", "tag", "note", "created_at"]
    assert [bookmark.id for bookmark in store.list_by_tag("TODO")] == [third_id, first_id]
    assert [bookmark.line for bookmark in store.list_by_file("src/app.py")] == [3, 10]
    assert store.tags() == ("REVIEW", "TODO")

    store.remove(second_id)

    assert [bookmark.line for bookmark in store.list_by_file("src/app.py")] == [10]


@pytest.mark.unit
def test_bookmark_store_rejects_non_positive_lines(tmp_path) -> None:
    store = BookmarkStore(tmp_path / "project-bookmarks.sqlite")

    with pytest.raises(ValueError, match="one-based"):
        store.add("src/app.py", 0, "TODO", "")
