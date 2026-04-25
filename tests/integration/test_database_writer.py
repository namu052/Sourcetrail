"""Integration tests for the Sourcetrail-compatible DB writer."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from sourcetrail_remake.core.types import EdgeType, NodeType, SourceLocation
from sourcetrail_remake.db.writer import DatabaseWriter


@pytest.mark.integration
def test_database_writer_records_files_symbols_and_edges(tmp_path: Path) -> None:
    fixture_path = Path("tests/fixtures/sample-minimal/session_manager.py").resolve()
    source = fixture_path.read_text(encoding="utf-8")
    db_path = tmp_path / "writer-smoke.srctrldb"

    with DatabaseWriter(db_path) as writer:
        writer.initialize_schema()
        file_id = writer.record_file(fixture_path, source)
        location = SourceLocation.from_name(line=24, column=6, name="SessionManager")
        symbol_id = writer.record_symbol(
            "SessionManager",
            NodeType.NODE_CLASS,
            file_id,
            location,
            qualified_name="session_manager.SessionManager",
        )
        writer.record_edge(file_id, symbol_id, EdgeType.EDGE_MEMBER, file=file_id, location=location)
        writer.record_unsolved(
            symbol_id,
            "missing_cleanup_handler",
            file=file_id,
            location=SourceLocation.from_name(line=47, column=12, name="missing_cleanup_handler"),
        )
        summary = writer.summary()

    assert summary.files == 1
    assert summary.symbols == 2
    assert summary.edges == 1
    assert summary.locations == 2
    assert summary.occurrences == 3
    assert summary.unsolved == 1

    with sqlite3.connect(db_path) as connection:
        meta = dict(connection.execute("SELECT key, value FROM meta;").fetchall())
        assert meta["storage_version"] == "25"
