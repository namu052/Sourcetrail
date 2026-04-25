"""Qt coverage for graph expand/collapse animation."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.core.types import EdgeType, NodeType, SourceLocation
from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.ui.graph.scene import GraphScene
from sourcetrail_remake.ui.graph.view import GraphView


@pytest.mark.ui
def test_graph_scene_toggles_member_visibility_with_animation(qtbot) -> None:
    temp_root = Path(".tmp-test-artifacts").resolve()
    temp_root.mkdir(parents=True, exist_ok=True)
    db_path = temp_root / f"graph-animation-{uuid4().hex}.srctrldb"
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

        scene = GraphScene(reader=DatabaseReader(db_path), event_bus=EventBus())
        view = GraphView(scene)
        qtbot.addWidget(view)
        view.show()
        view.focus_symbol(class_id, depth=1)

        member_item = scene.get_node_item(method_id)
        assert member_item is not None
        assert member_item.isVisible()

        scene.toggle_node_expansion(class_id)
        qtbot.wait(250)
        assert not member_item.isVisible()

        scene.toggle_node_expansion(class_id)
        qtbot.wait(250)
        assert member_item.isVisible()
        assert member_item.opacity() == pytest.approx(1.0)
    finally:
        try:
            db_path.unlink(missing_ok=True)
        except PermissionError:
            pass
