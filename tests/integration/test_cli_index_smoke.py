"""Smoke tests for the CLI indexer entrypoint."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from sourcetrail_remake.cli.index import main
from sourcetrail_remake.db.reader import DatabaseReader


@pytest.mark.integration
@pytest.mark.parametrize(
    ("sample_name", "expected_symbol", "max_unsolved"),
    [
        ("sample-django", "blog.models.UserProfile", 20),
        ("sample-flask", "app.health", 20),
        ("sample-requests", "client.fetch_status", 10),
    ],
)
def test_srm_index_cli_smoke(sample_name: str, expected_symbol: str, max_unsolved: int) -> None:
    project_root = Path("tests/fixtures").resolve() / sample_name
    temp_root = Path(".tmp-test-artifacts").resolve()
    temp_root.mkdir(parents=True, exist_ok=True)
    db_path = temp_root / f"{sample_name}-{uuid4().hex}.srctrldb"
    try:
        exit_code = main([str(project_root), "--db", str(db_path), "--deep"])
        reader = DatabaseReader(db_path)
        summary = reader.summary()

        assert exit_code == 0
        assert summary.files >= 2
        assert summary.symbols >= 5
        assert summary.edges >= 5
        assert summary.unsolved <= max_unsolved
        assert reader.find_symbol_id(expected_symbol) is not None
    finally:
        try:
            db_path.unlink(missing_ok=True)
        except PermissionError:
            pass
