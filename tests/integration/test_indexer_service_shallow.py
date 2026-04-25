"""Integration tests for the shallow indexer mode."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.indexer.service import IndexerService


@pytest.mark.integration
def test_indexer_service_shallow_indexes_sample_project() -> None:
    project_root = Path("tests/fixtures/sample-minimal").resolve()
    temp_root = Path(".tmp-test-artifacts").resolve()
    temp_root.mkdir(parents=True, exist_ok=True)
    db_path = temp_root / f"shallow-{uuid4().hex}.srctrldb"
    progress_events: list[tuple[int, int]] = []
    try:
        service = IndexerService(project_root, "shallow")
        with DatabaseWriter(db_path) as writer:
            result = service.index(writer, lambda current, total: progress_events.append((current, total)))

        reader = DatabaseReader(db_path)
        summary = reader.summary()

        assert result.files_indexed == 1
        assert result.symbols_recorded >= 10
        assert summary.files == 1
        assert summary.symbols >= 10
        assert summary.edges >= 10
        assert summary.unsolved >= 1
        assert reader.find_symbol_id("session_manager.SessionManager.cleanup_expired") is not None
        assert any(name.endswith("missing_cleanup_handler") for _, name in reader.list_unsolved())
        assert progress_events == [(1, 1)]
    finally:
        try:
            db_path.unlink(missing_ok=True)
        except PermissionError:
            pass
