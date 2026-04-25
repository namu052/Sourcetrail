"""Schema compatibility smoke tests."""

from __future__ import annotations

import sqlite3

import pytest

from sourcetrail_remake.db.schema import REQUIRED_TABLES, create_schema, ensure_tables


@pytest.mark.compatibility
def test_core_schema_creates_required_tables() -> None:
    connection = sqlite3.connect(":memory:")
    try:
        create_schema(connection)
        assert ensure_tables(connection, REQUIRED_TABLES) == []
    finally:
        connection.close()
