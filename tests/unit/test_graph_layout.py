"""Unit coverage for the deterministic graph layout engine."""

from __future__ import annotations

import pytest

from sourcetrail_remake.core.types import (
    EdgeId,
    EdgeType,
    GraphEdgeRecord,
    GraphNeighborhood,
    GraphNodeRecord,
    NodeId,
    NodeType,
)
from sourcetrail_remake.ui.graph.layout import GraphLayoutEngine


@pytest.mark.unit
def test_graph_layout_engine_is_deterministic() -> None:
    neighborhood = GraphNeighborhood(
        root_id=NodeId(1),
        depth=2,
        nodes=(
            GraphNodeRecord(NodeId(1), "pkg.SessionManager", "SessionManager", NodeType.NODE_CLASS, 2),
            GraphNodeRecord(NodeId(2), "pkg.cleanup_expired", "cleanup_expired", NodeType.NODE_METHOD, 0),
            GraphNodeRecord(NodeId(3), "pkg.notify", "notify", NodeType.NODE_FUNCTION, 0),
        ),
        edges=(
            GraphEdgeRecord(EdgeId(10), NodeId(1), NodeId(2), EdgeType.EDGE_MEMBER),
            GraphEdgeRecord(EdgeId(11), NodeId(2), NodeId(3), EdgeType.EDGE_CALL),
        ),
    )

    engine = GraphLayoutEngine()
    first = engine.compute_layout(neighborhood)
    second = engine.compute_layout(neighborhood)

    assert first == second
    assert first[NodeId(1)].x() < first[NodeId(2)].x() < first[NodeId(3)].x()


@pytest.mark.unit
def test_graph_layout_engine_separates_nodes_in_same_layer() -> None:
    neighborhood = GraphNeighborhood(
        root_id=NodeId(1),
        depth=1,
        nodes=(
            GraphNodeRecord(NodeId(1), "pkg.root", "root", NodeType.NODE_CLASS, 2),
            GraphNodeRecord(NodeId(2), "pkg.a", "a", NodeType.NODE_METHOD, 0),
            GraphNodeRecord(NodeId(3), "pkg.b", "b", NodeType.NODE_METHOD, 0),
        ),
        edges=(
            GraphEdgeRecord(EdgeId(10), NodeId(1), NodeId(2), EdgeType.EDGE_CALL),
            GraphEdgeRecord(EdgeId(11), NodeId(1), NodeId(3), EdgeType.EDGE_CALL),
        ),
    )

    engine = GraphLayoutEngine(node_spacing=140.0)
    positions = engine.compute_layout(neighborhood)

    assert positions[NodeId(2)].x() == positions[NodeId(3)].x()
    assert abs(positions[NodeId(2)].y() - positions[NodeId(3)].y()) >= 140.0
