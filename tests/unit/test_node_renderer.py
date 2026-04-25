"""Unit coverage for graph node renderers."""

from __future__ import annotations

import pytest
from PyQt6.QtWidgets import QGraphicsScene

from sourcetrail_remake.ui.graph.nodes import ClassContainerItem, NodeRenderer


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
