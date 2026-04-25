"""Unit tests for unresolved symbol tracking."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from sourcetrail_remake.core.types import EdgeType, NodeType, SourceLocation
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.indexer.unsolved import UnsolvedSymbolTracker


@pytest.mark.unit
def test_unsolved_tracker_deduplicates_context_and_name() -> None:
    fixture_path = Path("tests/fixtures/sample-minimal/session_manager.py").resolve()
    source = fixture_path.read_text(encoding="utf-8")
    location = SourceLocation.from_name(line=47, column=12, name="missing_cleanup_handler")
    temp_root = Path(".tmp-test-artifacts").resolve()
    temp_root.mkdir(parents=True, exist_ok=True)
    db_path = temp_root / f"unsolved-{uuid4().hex}.srctrldb"
    try:
        with DatabaseWriter(db_path) as writer:
            writer.initialize_schema()
            file_id = writer.record_file(fixture_path, source)
            context_node = writer.record_symbol(
                "SessionManager",
                NodeType.NODE_CLASS,
                file_id,
                SourceLocation.from_name(line=24, column=6, name="SessionManager"),
                qualified_name="session_manager.SessionManager",
            )
            tracker = UnsolvedSymbolTracker()

            first = tracker.register(
                writer,
                context_node=context_node,
                name="missing_cleanup_handler",
                file=file_id,
                location=location,
                edge_type=EdgeType.EDGE_CALL,
            )
            second = tracker.register(
                writer,
                context_node=context_node,
                name="missing_cleanup_handler",
                file=file_id,
                location=location,
                edge_type=EdgeType.EDGE_CALL,
            )

            assert first == second
            assert tracker.count == 1
            assert writer.summary().unsolved == 1
    finally:
        try:
            db_path.unlink(missing_ok=True)
        except PermissionError:
            pass
