"""Qt smoke coverage for the graph scene/view stack."""

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
def test_graph_scene_load_symbol_renders_database_graph(qtbot) -> None:
    temp_root = Path(".tmp-test-artifacts").resolve()
    temp_root.mkdir(parents=True, exist_ok=True)
    db_path = temp_root / f"graph-scene-{uuid4().hex}.srctrldb"
    try:
        with DatabaseWriter(db_path) as writer:
            writer.initialize_schema()
            file_id = writer.record_file(
                Path("tests/fixtures/sample-minimal/session_manager.py").resolve(),
                "class SessionManager:\n    def cleanup_expired(self) -> None:\n        notify()\n",
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
            external_id = writer.record_symbol(
                "notify",
                NodeType.NODE_FUNCTION,
                None,
                None,
                qualified_name="sample_external.notify",
            )
            writer.record_edge(class_id, method_id, EdgeType.EDGE_MEMBER, file=file_id)
            writer.record_edge(method_id, external_id, EdgeType.EDGE_CALL, file=file_id)

        event_bus = EventBus()
        scene = GraphScene(reader=DatabaseReader(db_path), event_bus=event_bus)
        view = GraphView(scene)
        qtbot.addWidget(view)
        view.show()

        view.focus_symbol(method_id, depth=1)
        node_items = [item for item in scene.items() if item.data(0) is not None]

        assert len(node_items) == 3
        assert scene.sceneRect().width() > 0
        with qtbot.waitSignal(event_bus.symbol_selected):
            scene.on_node_clicked(external_id)
    finally:
        try:
            db_path.unlink(missing_ok=True)
        except PermissionError:
            pass
