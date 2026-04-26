"""Qt coverage for the Week 8 bookmark control."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QToolButton

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.core.types import EdgeType, NodeType, SourceLocation
from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.ui.main_window import create_main_window


@pytest.mark.ui
def test_bookmark_star_adds_removes_and_lists_symbols(qtbot) -> None:
    temp_root = Path(".tmp-test-artifacts").resolve()
    temp_root.mkdir(parents=True, exist_ok=True)
    db_path = temp_root / f"bookmark-control-{uuid4().hex}.srctrldb"
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

        window = create_main_window(
            EventBus(),
            reader=DatabaseReader(db_path),
            initial_symbol_id=class_id,
        )
        qtbot.addWidget(window)
        window.show()

        bookmark_button = window.findChild(QToolButton, "bookmark-toggle-button")
        assert bookmark_button is not None
        assert bookmark_button.text() == "☆"

        qtbot.mouseClick(bookmark_button, Qt.MouseButton.LeftButton)
        assert bookmark_button.text() == "★"
        assert [action.text() for action in bookmark_button.menu().actions()] == [
            "session_manager.SessionManager"
        ]

        window.focus_symbol(method_id)
        qtbot.mouseClick(bookmark_button, Qt.MouseButton.LeftButton)
        assert [action.text() for action in bookmark_button.menu().actions()] == [
            "session_manager.SessionManager",
            "session_manager.SessionManager.cleanup_expired",
        ]

        bookmark_button.menu().actions()[0].trigger()
        assert window.current_symbol_id == class_id
    finally:
        try:
            db_path.unlink(missing_ok=True)
        except PermissionError:
            pass
