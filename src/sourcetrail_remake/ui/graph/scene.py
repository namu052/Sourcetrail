"""Database-backed graph scene for the Phase 1 renderer."""

from __future__ import annotations

from collections.abc import Iterable

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsPathItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
)

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.core.types import EdgeType, GraphEdgeRecord, GraphNeighborhood, GraphNodeRecord, NodeId, NodeType
from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.ui.graph.edges import EdgeRenderer
from sourcetrail_remake.ui.graph.nodes import NodeRenderer


class GraphScene(QGraphicsScene):
    """Scene that renders graph neighborhoods from a SourcetrailDB file."""

    def __init__(
        self,
        *,
        reader: DatabaseReader | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        super().__init__()
        self.reader = reader
        self.event_bus = event_bus
        self._node_items: dict[NodeId, QGraphicsItem] = {}
        self._edge_items: dict[int, QGraphicsPathItem] = {}
        self._selected_node_id: NodeId | None = None
        self.setBackgroundBrush(QBrush(QColor("#fbfbfd")))
        self.selectionChanged.connect(self._handle_selection_changed)
        self._show_placeholder("Open a database and select a symbol to render the graph.")

    def set_reader(self, reader: DatabaseReader | None) -> None:
        self.reader = reader

    def load_symbol(self, symbol_id: NodeId, depth: int) -> None:
        if self.reader is None:
            self._show_placeholder("Graph database is not loaded yet.")
            return
        neighborhood = self.reader.load_graph(symbol_id, depth)
        self._render(neighborhood)

    def on_node_clicked(self, node_id: NodeId) -> None:
        self._selected_node_id = node_id
        if self.event_bus is not None:
            self.event_bus.symbol_selected.emit(node_id)
        self._apply_selection_state()

    def _show_placeholder(self, message: str) -> None:
        self.clear()
        self._node_items.clear()
        self._edge_items.clear()
        text_item = self.addSimpleText(message)
        text_item.setBrush(QBrush(QColor("#6b7280")))
        text_item.setPos(32, 32)
        self.setSceneRect(0, 0, 960, 540)

    def _render(self, neighborhood: GraphNeighborhood) -> None:
        self.clear()
        self._node_items.clear()
        self._edge_items.clear()
        self._selected_node_id = neighborhood.root_id

        ordered_nodes = tuple(sorted(neighborhood.nodes, key=lambda node: (node.member_count == 0, int(node.id))))
        positions = self._grid_positions(ordered_nodes)
        node_map = {node.id: node for node in neighborhood.nodes}

        for node in ordered_nodes:
            item = self._add_node(node, positions[node.id], is_root=node.id == neighborhood.root_id)
            self._node_items[node.id] = item

        for edge in neighborhood.edges:
            source_item = self._node_items.get(edge.source)
            target_item = self._node_items.get(edge.target)
            if source_item is None or target_item is None:
                continue
            path_item = self._add_edge(edge, source_item, target_item)
            self._edge_items[int(edge.id)] = path_item

        self._apply_selection_state()
        self.setSceneRect(self.itemsBoundingRect().adjusted(-48, -48, 48, 48))
        if node_map and self.event_bus is not None:
            self.event_bus.layout_changed.emit("grid")

    def _grid_positions(self, nodes: Iterable[GraphNodeRecord]) -> dict[NodeId, QPointF]:
        positions: dict[NodeId, QPointF] = {}
        for index, node in enumerate(nodes):
            column = index % 3
            row = index // 3
            positions[node.id] = QPointF(60 + column * 260, 60 + row * 180)
        return positions

    def _add_node(self, node: GraphNodeRecord, position: QPointF, *, is_root: bool) -> QGraphicsItem:
        if node.is_unsolved:
            item = NodeRenderer.create_unsolved()
            if hasattr(item, "set_label"):
                item.set_label(node.display_name)
            item.setPos(position)
            self.addItem(item)
        elif node.node_type == NodeType.NODE_CLASS:
            item = NodeRenderer.create_class_container(node.display_name, node.member_count)
            item.setPos(position)
            self.addItem(item)
        else:
            item = NodeRenderer.create_member(node.display_name, node.node_type)
            item.setPos(position)
            self.addItem(item)

        item.setData(0, int(node.id))
        item.setData(1, int(node.node_type))
        item.setData(2, node.is_unsolved)
        item.setData(3, is_root)
        item.setToolTip(node.serialized_name)
        return item

    def _add_edge(
        self,
        edge: GraphEdgeRecord,
        source_item: QGraphicsItem,
        target_item: QGraphicsItem,
    ) -> QGraphicsPathItem:
        start = source_item.sceneBoundingRect().center()
        end = target_item.sceneBoundingRect().center()
        item = EdgeRenderer.create_edge(start, end, edge.edge_type)
        self.addItem(item)
        return item

    def _handle_selection_changed(self) -> None:
        selected_items = self.selectedItems()
        if not selected_items:
            return
        node_id = selected_items[0].data(0)
        if node_id is not None:
            self.on_node_clicked(NodeId(int(node_id)))

    def _apply_selection_state(self) -> None:
        for node_id, item in self._node_items.items():
            is_selected = node_id == self._selected_node_id
            is_unsolved = bool(item.data(2))
            if hasattr(item, "set_selected_state"):
                item.set_selected_state(is_selected)
                continue
            if isinstance(item, QGraphicsRectItem):
                base_color = "#fde68a" if is_selected else "#ffffff"
                if is_unsolved and not is_selected:
                    base_color = "#f5d0a9"
                pen_color = "#f59e0b" if is_selected else "#1f2937"
                item.setBrush(QBrush(QColor(base_color)))
                item.setPen(QPen(QColor(pen_color), 3 if is_selected else 2))
