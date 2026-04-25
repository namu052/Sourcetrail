"""Integration tests for the Sourcetrail DB reader."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from sourcetrail_remake.core.types import NodeType, SourceLocation
from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.db.writer import DatabaseWriter


@pytest.mark.integration
def test_database_reader_reports_summary_and_occurrences() -> None:
    fixture_path = Path("tests/fixtures/sample-minimal/session_manager.py").resolve()
    source = fixture_path.read_text(encoding="utf-8")
    temp_root = Path(".tmp-test-artifacts").resolve()
    temp_root.mkdir(parents=True, exist_ok=True)
    db_path = temp_root / f"reader-{uuid4().hex}.srctrldb"
    try:
        with DatabaseWriter(db_path) as writer:
            writer.initialize_schema()
            file_id = writer.record_file(fixture_path, source)
            writer.record_symbol(
                "SessionManager",
                NodeType.NODE_CLASS,
                file_id,
                SourceLocation.from_name(line=24, column=6, name="SessionManager"),
                qualified_name="session_manager.SessionManager",
            )
            writer.record_unsolved(
                writer.record_symbol(
                    "cleanup_expired",
                    NodeType.NODE_METHOD,
                    file_id,
                    SourceLocation.from_name(line=39, column=8, name="cleanup_expired"),
                    qualified_name="session_manager.SessionManager.cleanup_expired",
                ),
                "missing_cleanup_handler",
                file=file_id,
                location=SourceLocation.from_name(
                    line=47,
                    column=12,
                    name="missing_cleanup_handler",
                ),
            )

        reader = DatabaseReader(db_path)
        summary = reader.summary()
        unsolved = reader.list_unsolved()

        assert summary.files == 1
        assert summary.unsolved == 1
        assert unsolved[0][1] == "unsolved.3.missing_cleanup_handler"
        symbol_id = reader.find_symbol_id("session_manager.SessionManager")
        assert symbol_id is not None
        assert reader.get_occurrences(symbol_id)[0].start_line == 24
    finally:
        try:
            db_path.unlink(missing_ok=True)
        except PermissionError:
            pass
