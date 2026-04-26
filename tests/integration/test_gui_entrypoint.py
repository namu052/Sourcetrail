"""Integration coverage for the GUI entrypoint."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from sourcetrail_remake.__main__ import main
from sourcetrail_remake.core.types import NodeType, SourceLocation
from sourcetrail_remake.db.writer import DatabaseWriter


@pytest.mark.integration
def test_gui_entrypoint_opens_database_and_auto_quits() -> None:
    temp_root = Path(".tmp-test-artifacts").resolve()
    temp_root.mkdir(parents=True, exist_ok=True)
    db_path = temp_root / f"gui-entrypoint-{uuid4().hex}.srctrldb"
    try:
        with DatabaseWriter(db_path) as writer:
            writer.initialize_schema()
            file_id = writer.record_file(
                Path("tests/fixtures/sample-minimal/session_manager.py").resolve(),
                "class SessionManager:\n    pass\n",
            )
            writer.record_symbol(
                "SessionManager",
                NodeType.NODE_CLASS,
                file_id,
                SourceLocation.from_name(line=1, column=6, name="SessionManager"),
                qualified_name="session_manager.SessionManager",
            )

        exit_code = main(
            [
                str(db_path),
                "--symbol",
                "session_manager.SessionManager",
                "--auto-quit-ms",
                "1",
            ]
        )

        assert exit_code == 0
    finally:
        try:
            db_path.unlink(missing_ok=True)
        except PermissionError:
            pass
