"""Integration coverage for the Phase 1 navigation and control stack."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLineEdit, QPushButton, QSlider, QToolButton

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.core.types import EdgeType, NodeType, SourceLocation
from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.ui.main_window import create_main_window


@pytest.mark.integration
def test_phase1_main_window_integrates_navigation_and_controls(qtbot) -> None:
    temp_root = Path(".tmp-test-artifacts").resolve()
    temp_root.mkdir(parents=True, exist_ok=True)
    db_path = temp_root / f"phase1-gui-flow-{uuid4().hex}.srctrldb"
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

        window = create_main_window(
            EventBus(),
            reader=DatabaseReader(db_path),
            initial_symbol_id=class_id,
        )
        qtbot.addWidget(window)
        window.show()

        search_line = window.findChild(QLineEdit, "fqn-search-line-edit")
        depth_slider = window.findChild(QSlider, "depth-slider")
        zoom_in_button = window.findChild(QPushButton, "zoom-in-button")
        bookmark_button = window.findChild(QToolButton, "bookmark-toggle-button")
        back_button = window.findChild(QToolButton, "history-back-button")

        assert search_line is not None
        assert depth_slider is not None
        assert zoom_in_button is not None
        assert bookmark_button is not None
        assert back_button is not None
        assert window.current_symbol_id == class_id

        search_line.setText("session_manager.SessionManager.cleanup_expired")
        qtbot.keyPress(search_line, Qt.Key.Key_Return)
        assert window.current_symbol_id == method_id

        depth_slider.setValue(2)
        qtbot.wait(50)
        assert len(window.graph_scene._node_items) == 3

        qtbot.mouseClick(zoom_in_button, Qt.MouseButton.LeftButton)
        assert window.graph_view.zoom_percent() > 100

        qtbot.mouseClick(bookmark_button, Qt.MouseButton.LeftButton)
        assert [action.text() for action in bookmark_button.menu().actions()] == [
            "session_manager.SessionManager.cleanup_expired"
        ]

        qtbot.mouseClick(back_button, Qt.MouseButton.LeftButton)
        assert window.current_symbol_id == class_id
    finally:
        try:
            db_path.unlink(missing_ok=True)
        except PermissionError:
            pass
