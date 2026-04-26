"""Unit coverage for graph node renderers."""

from __future__ import annotations

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGraphicsScene

from sourcetrail_remake.core.types import NodeType
from sourcetrail_remake.ui.graph.nodes import (
    ClassContainerItem,
    MemberNodeItem,
    NodeRenderer,
    UnsolvedNodeItem,
)


@pytest.mark.unit
def test_node_renderer_creates_class_container(qtbot) -> None:
    scene = QGraphicsScene()
    item = NodeRenderer.create_class_container("SessionManager", member_count=4)
    assert isinstance(item, ClassContainerItem)

    scene.addItem(item)
    item.set_selected_state(True)

    assert item.boundingRect().width() == 240
    assert item.boundingRect().height() == 132
    assert item.member_count == 4


@pytest.mark.unit
def test_node_renderer_creates_member_node(qtbot) -> None:
    scene = QGraphicsScene()
    item = NodeRenderer.create_member("cleanup_expired", NodeType.NODE_METHOD)
    assert isinstance(item, MemberNodeItem)

    scene.addItem(item)
    item.set_selected_state(True)

    assert item.boundingRect().width() == 220
    assert item.node_type == NodeType.NODE_METHOD
    assert item.accent_color.name() == "#f97316"


@pytest.mark.unit
def test_node_renderer_creates_unsolved_node(qtbot) -> None:
    scene = QGraphicsScene()
    item = NodeRenderer.create_unsolved()
    assert isinstance(item, UnsolvedNodeItem)

    scene.addItem(item)
    item.set_label("missing_cleanup_handler")
    item.set_selected_state(True)

    assert item.label == "missing_cleanup_handler"
    assert item.pattern_style == Qt.BrushStyle.DiagCrossPattern
