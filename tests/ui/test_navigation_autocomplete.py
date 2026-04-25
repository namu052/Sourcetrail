"""Qt coverage for the Week 7 fuzzy autocomplete popup."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from PyQt6.QtWidgets import QLineEdit

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.core.types import EdgeType, NodeType, SourceLocation
from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.ui.main_window import create_main_window


@pytest.mark.ui
def test_fuzzy_autocomplete_suggests_symbol_names(qtbot) -> None:
    temp_root = Path(".tmp-test-artifacts").resolve()
    temp_root.mkdir(parents=True, exist_ok=True)
    db_path = temp_root / f"navigation-autocomplete-{uuid4().hex}.srctrldb"
    try:
        with DatabaseWriter(db_path) as writer:
            writer.initialize_schema()
            file_id = writer.record_file(
                Path("tests/fixtures/sample-minimal/session_manager.py").resolve(),
                (
                    "class SessionManager:\n"
                    "    def cleanup_expired(self) -> None:\n"
                    "        notify()\n"
                ),
            )
            class_id = writer.record_symbol(
                "SessionManager",
                NodeType.NODE_CLASS,
                file_id,
                SourceLocation.from_name(line=1, column=6, name="SessionManager"),
                qualified_name="session_manager.SessionManager",
            )
            method_id = writer.record_symbol(
                "cleanup_expired",
                NodeType.NODE_METHOD,
                file_id,
                SourceLocation.from_name(line=2, column=8, name="cleanup_expired"),
                qualified_name="session_manager.SessionManager.cleanup_expired",
            )
            writer.record_edge(class_id, method_id, EdgeType.EDGE_MEMBER, file=file_id)

        window = create_main_window(EventBus(), reader=DatabaseReader(db_path), initial_symbol_id=class_id)
        qtbot.addWidget(window)
        window.show()

        search_line = window.findChild(QLineEdit, "fqn-search-line-edit")
        assert search_line is not None

        search_line.clear()
        qtbot.keyClicks(search_line, "clean exp")
        qtbot.waitUntil(lambda: bool(window.search_bar.suggestions()))

        assert "session_manager.SessionManager.cleanup_expired" in window.search_bar.suggestions()

        window.search_bar._apply_completion("session_manager.SessionManager.cleanup_expired")
        assert window.current_symbol_id == method_id
    finally:
        try:
            db_path.unlink(missing_ok=True)
        except PermissionError:
            pass
