"""Qt coverage for graph expand/collapse interactions."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from PyQt6.QtCore import QPoint, Qt

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.core.types import EdgeType, NodeType, SourceLocation
from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.ui.graph.view import GraphView
from sourcetrail_remake.ui.main_window import create_main_window


@pytest.mark.ui
def test_graph_view_supports_click_and_keyboard_expand_collapse(qtbot) -> None:
    temp_root = Path(".tmp-test-artifacts").resolve()
    temp_root.mkdir(parents=True, exist_ok=True)
    db_path = temp_root / f"graph-interaction-{uuid4().hex}.srctrldb"
    try:
        with DatabaseWriter(db_path) as writer:
            writer.initialize_schema()
            file_id = writer.record_file(
                Path("tests/fixtures/sample-minimal/session_manager.py").resolve(),
                "class SessionManager:\n    def cleanup_expired(self) -> None:\n        pass\n",
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

        view = window.findChild(GraphView, "graph-view")
        assert view is not None

        class_item = window.graph_scene.get_node_item(class_id)
        method_item = window.graph_scene.get_node_item(method_id)
        assert class_item is not None
        assert method_item is not None
        assert method_item.isVisible()

        click_point = view.mapFromScene(class_item.sceneBoundingRect().center())
        qtbot.mouseClick(view.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(click_point.x(), click_point.y()))
        qtbot.wait(250)
        assert not method_item.isVisible()

        view.setFocus()
        qtbot.keyClick(view, Qt.Key.Key_Plus)
        qtbot.wait(250)
        assert method_item.isVisible()

        qtbot.keyClick(view, Qt.Key.Key_Minus)
        qtbot.wait(250)
        assert not method_item.isVisible()
    finally:
        try:
            db_path.unlink(missing_ok=True)
        except PermissionError:
            pass
