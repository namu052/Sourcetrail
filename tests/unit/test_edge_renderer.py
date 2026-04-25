"""Unit coverage for graph edge rendering."""

from __future__ import annotations

import pytest
from PyQt6.QtCore import QPointF, Qt

from sourcetrail_remake.core.types import EdgeType
from sourcetrail_remake.ui.graph.edges import EdgeRenderer, RenderedEdgeItem


@pytest.mark.unit
def test_edge_renderer_creates_call_edge_with_arrow_head() -> None:
    item = EdgeRenderer.create_edge(QPointF(20, 20), QPointF(200, 80), EdgeType.EDGE_CALL)
    assert isinstance(item, RenderedEdgeItem)

    assert item.pen().style() == Qt.PenStyle.SolidLine
    assert item.color.name() == "#f97316"
    assert item.path().elementCount() >= 4
    assert item.arrow_head.count() == 3


@pytest.mark.unit
def test_edge_renderer_creates_member_edge_with_dashed_pen() -> None:
    item = EdgeRenderer.create_edge(QPointF(20, 20), QPointF(200, 80), EdgeType.EDGE_MEMBER)
    assert isinstance(item, RenderedEdgeItem)

    assert item.pen().style() == Qt.PenStyle.DashLine
    assert item.color.name() == "#64748b"
