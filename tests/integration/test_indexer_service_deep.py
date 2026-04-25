"""Integration tests for the deep indexer mode."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.indexer.service import IndexerService


@pytest.mark.integration
def test_indexer_service_deep_resolves_external_symbols() -> None:
    project_root = Path("tests/fixtures/sample-minimal").resolve()
    temp_root = Path(".tmp-test-artifacts").resolve()
    temp_root.mkdir(parents=True, exist_ok=True)
    db_path = temp_root / f"deep-{uuid4().hex}.srctrldb"
    try:
        service = IndexerService(project_root, "deep")
        with DatabaseWriter(db_path) as writer:
            result = service.index(writer, lambda _current, _total: None)

        reader = DatabaseReader(db_path)
        summary = reader.summary()

        assert result.files_indexed == 1
        assert result.external_symbols >= 1
        assert summary.unsolved < 20
        assert reader.find_symbol_id("dataclasses.dataclass") is not None
        assert any(name.endswith("missing_cleanup_handler") for _, name in reader.list_unsolved())
    finally:
        try:
            db_path.unlink(missing_ok=True)
        except PermissionError:
            pass
