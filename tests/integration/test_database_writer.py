"""Integration tests for the Sourcetrail-compatible DB writer."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from uuid import uuid4

import pytest

from sourcetrail_remake.core.types import EdgeType, NodeType, SourceLocation
from sourcetrail_remake.db.writer import DatabaseWriter


@pytest.mark.integration
def test_database_writer_records_files_symbols_and_edges() -> None:
    fixture_path = Path("tests/fixtures/sample-minimal/session_manager.py").resolve()
    source = fixture_path.read_text(encoding="utf-8")
    temp_root = Path(".tmp-test-artifacts").resolve()
    temp_root.mkdir(parents=True, exist_ok=True)
    db_path = temp_root / f"writer-{uuid4().hex}.srctrldb"
    try:
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
    finally:
        try:
            db_path.unlink(missing_ok=True)
        except PermissionError:
            pass
