"""Qt coverage for the Week 7 history dropdown."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from PyQt6.QtWidgets import QToolButton

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.core.types import EdgeType, NodeType, SourceLocation
from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.ui.main_window import create_main_window


@pytest.mark.ui
def test_history_dropdown_lists_entries_and_jumps_to_selection(qtbot) -> None:
    temp_root = Path(".tmp-test-artifacts").resolve()
    temp_root.mkdir(parents=True, exist_ok=True)
    db_path = temp_root / f"navigation-history-menu-{uuid4().hex}.srctrldb"
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
            function_id = writer.record_symbol(
                "notify",
                NodeType.NODE_FUNCTION,
                None,
                None,
                qualified_name="sample_external.notify",
            )
            writer.record_edge(class_id, method_id, EdgeType.EDGE_MEMBER, file=file_id)
            writer.record_edge(method_id, function_id, EdgeType.EDGE_CALL, file=file_id)

        window = create_main_window(EventBus(), reader=DatabaseReader(db_path), initial_symbol_id=class_id)
        qtbot.addWidget(window)
        window.show()
        window.focus_symbol(method_id)
        window.focus_symbol(function_id)

        history_button = window.findChild(QToolButton, "history-menu-button")
        assert history_button is not None
        actions = history_button.menu().actions()
        assert [action.text() for action in actions] == [
            "session_manager.SessionManager",
            "session_manager.SessionManager.cleanup_expired",
            "sample_external.notify",
        ]

        actions[0].trigger()
        assert window.current_symbol_id == class_id
    finally:
        try:
            db_path.unlink(missing_ok=True)
        except PermissionError:
            pass
