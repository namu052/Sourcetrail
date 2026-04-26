"""Unit coverage for graph scene rendering and layout integration."""

from __future__ import annotations

import pytest

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.core.types import (
    EdgeId,
    EdgeType,
    GraphEdgeRecord,
    GraphNeighborhood,
    GraphNodeRecord,
    NodeId,
    NodeType,
)
from sourcetrail_remake.ui.graph.edges import RenderedEdgeItem
from sourcetrail_remake.ui.graph.scene import GraphScene


@pytest.mark.unit
def test_graph_scene_renders_layout_and_bundled_edges(qtbot) -> None:
    neighborhood = GraphNeighborhood(
        root_id=NodeId(1),
        depth=2,
        nodes=(
            GraphNodeRecord(
                NodeId(1),
                "pkg.SessionManager",
                "SessionManager",
                NodeType.NODE_CLASS,
                1,
            ),
            GraphNodeRecord(
                NodeId(2),
                "pkg.SessionManager.cleanup_expired",
                "cleanup_expired",
                NodeType.NODE_METHOD,
                0,
                parent_id=NodeId(1),
            ),
            GraphNodeRecord(NodeId(3), "pkg.notify", "notify", NodeType.NODE_FUNCTION, 0),
        ),
        edges=(
            GraphEdgeRecord(EdgeId(10), NodeId(1), NodeId(2), EdgeType.EDGE_MEMBER),
            GraphEdgeRecord(EdgeId(11), NodeId(2), NodeId(3), EdgeType.EDGE_CALL),
            GraphEdgeRecord(EdgeId(12), NodeId(2), NodeId(3), EdgeType.EDGE_USAGE),
        ),
    )

    event_bus = EventBus()
    scene = GraphScene(event_bus=event_bus)
    expected_positions = scene.layout_engine.compute_layout(neighborhood)

    with qtbot.waitSignal(event_bus.layout_changed):
        scene.render_neighborhood(neighborhood)

    root_item = scene.get_node_item(NodeId(1))
    assert root_item is not None
    assert root_item.pos() == expected_positions[NodeId(1)]
    assert len(scene._edge_items) == 2

    edge_items = [item for item in scene._edge_items.values() if isinstance(item, RenderedEdgeItem)]
    assert any(item.bundle_count == 2 for item in edge_items)
