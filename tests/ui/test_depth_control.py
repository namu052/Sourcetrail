"""Qt coverage for the Week 8 depth slider."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from PyQt6.QtWidgets import QSlider

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.core.types import EdgeType, NodeType, SourceLocation
from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.ui.main_window import create_main_window


@pytest.mark.ui
def test_depth_slider_updates_graph_expansion(qtbot) -> None:
    temp_root = Path(".tmp-test-artifacts").resolve()
    temp_root.mkdir(parents=True, exist_ok=True)
    db_path = temp_root / f"depth-control-{uuid4().hex}.srctrldb"
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

        slider = window.findChild(QSlider, "depth-slider")
        assert slider is not None
        assert slider.minimum() == 1
        assert slider.maximum() == 10
        assert len(window.graph_scene._node_items) == 2

        slider.setValue(2)
        qtbot.wait(50)

        assert window.current_depth == 2
        assert len(window.graph_scene._node_items) == 3
    finally:
        try:
            db_path.unlink(missing_ok=True)
        except PermissionError:
            pass
