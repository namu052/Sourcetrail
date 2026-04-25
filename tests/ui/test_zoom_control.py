"""Qt coverage for the Week 8 zoom buttons."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.core.types import EdgeType, NodeType, SourceLocation
from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.ui.main_window import create_main_window


@pytest.mark.ui
def test_zoom_buttons_update_graph_view_scale(qtbot) -> None:
    temp_root = Path(".tmp-test-artifacts").resolve()
    temp_root.mkdir(parents=True, exist_ok=True)
    db_path = temp_root / f"zoom-control-{uuid4().hex}.srctrldb"
    try:
        with DatabaseWriter(db_path) as writer:
            writer.initialize_schema()
            file_id = writer.record_file(
                Path("tests/fixtures/sample-minimal/session_manager.py").resolve(),
                "class SessionManager:\n    pass\n",
            )
            class_id = writer.record_symbol(
                "SessionManager",
                NodeType.NODE_CLASS,
                file_id,
                SourceLocation.from_name(line=1, column=6, name="SessionManager"),
                qualified_name="session_manager.SessionManager",
            )

        window = create_main_window(EventBus(), reader=DatabaseReader(db_path), initial_symbol_id=class_id)
        qtbot.addWidget(window)
        window.show()

        zoom_in_button = window.findChild(QPushButton, "zoom-in-button")
        zoom_out_button = window.findChild(QPushButton, "zoom-out-button")
        assert zoom_in_button is not None
        assert zoom_out_button is not None
        assert window.graph_view.zoom_percent() == 100

        qtbot.mouseClick(zoom_in_button, Qt.MouseButton.LeftButton)
        assert window.graph_view.zoom_percent() > 100

        qtbot.mouseClick(zoom_out_button, Qt.MouseButton.LeftButton)
        assert window.graph_view.zoom_percent() <= 100
    finally:
        try:
            db_path.unlink(missing_ok=True)
        except PermissionError:
            pass
