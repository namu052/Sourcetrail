"""Database-backed graph scene for the Phase 1 renderer."""

from __future__ import annotations

from PyQt6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPointF,
    QPropertyAnimation,
)
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsObject,
    QGraphicsPathItem,
    QGraphicsScene,
)

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.core.types import (
    GraphNeighborhood,
    GraphNodeRecord,
    NodeId,
    NodeType,
)
from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.ui.graph.edges import BundledEdgeRecord, EdgeRenderer
from sourcetrail_remake.ui.graph.layout import GraphLayoutEngine
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
        self.layout_engine = GraphLayoutEngine()
        self._node_items: dict[NodeId, QGraphicsObject] = {}
        self._edge_items: dict[int, QGraphicsPathItem] = {}
        self._edge_endpoints: dict[int, tuple[NodeId, NodeId]] = {}
        self._node_positions: dict[NodeId, QPointF] = {}
        self._member_nodes_by_parent: dict[NodeId, list[NodeId]] = {}
        self._collapsed_nodes: set[NodeId] = set()
        self._active_animations: list[QParallelAnimationGroup] = []
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
        self.render_neighborhood(neighborhood)

    def render_neighborhood(self, neighborhood: GraphNeighborhood) -> None:
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
        self._edge_endpoints.clear()
        self._node_positions.clear()
        self._member_nodes_by_parent.clear()
        self._collapsed_nodes.clear()
        text_item = self.addSimpleText(message)
        text_item.setBrush(QBrush(QColor("#6b7280")))
        text_item.setPos(32, 32)
        self.setSceneRect(0, 0, 960, 540)

    def _render(self, neighborhood: GraphNeighborhood) -> None:
        self.clear()
        self._node_items.clear()
        self._edge_items.clear()
        self._edge_endpoints.clear()
        self._collapsed_nodes.clear()
        self._selected_node_id = neighborhood.root_id

        ordered_nodes = tuple(
            sorted(
                neighborhood.nodes,
                key=lambda node: (node.member_count == 0, int(node.id)),
            )
        )
        positions = self.layout_engine.compute_layout(neighborhood)
        self._node_positions = positions
        node_map = {node.id: node for node in neighborhood.nodes}
        self._member_nodes_by_parent = {}
        for node in neighborhood.nodes:
            if node.parent_id is None:
                continue
            self._member_nodes_by_parent.setdefault(node.parent_id, []).append(node.id)

        for node in ordered_nodes:
            item = self._add_node(node, positions[node.id], is_root=node.id == neighborhood.root_id)
            self._node_items[node.id] = item

        for edge in EdgeRenderer.bundle_parallel_edges(neighborhood.edges):
            source_item = self._node_items.get(edge.source)
            target_item = self._node_items.get(edge.target)
            if source_item is None or target_item is None:
                continue
            path_item = self._add_edge(edge, source_item, target_item)
            self._edge_items[int(edge.id)] = path_item
            self._edge_endpoints[int(edge.id)] = (edge.source, edge.target)

        self._apply_selection_state()
        self.setSceneRect(self.itemsBoundingRect().adjusted(-48, -48, 48, 48))
        if node_map and self.event_bus is not None:
            self.event_bus.layout_changed.emit("sugiyama-force")

    def _add_node(
        self,
        node: GraphNodeRecord,
        position: QPointF,
        *,
        is_root: bool,
    ) -> QGraphicsObject:
        if node.is_unsolved:
            item = NodeRenderer.create_unsolved()
            assert isinstance(item, QGraphicsObject)
            if hasattr(item, "set_label"):
                item.set_label(node.display_name)
            item.setPos(position)
            self.addItem(item)
        elif node.node_type == NodeType.NODE_CLASS:
            item = NodeRenderer.create_class_container(node.display_name, node.member_count)
            assert isinstance(item, QGraphicsObject)
            item.setPos(position)
            self.addItem(item)
        else:
            item = NodeRenderer.create_member(node.display_name, node.node_type)
            assert isinstance(item, QGraphicsObject)
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
        edge: BundledEdgeRecord,
        source_item: QGraphicsItem,
        target_item: QGraphicsItem,
    ) -> QGraphicsPathItem:
        start = source_item.sceneBoundingRect().center()
        end = target_item.sceneBoundingRect().center()
        item = EdgeRenderer.create_edge(start, end, edge.edge_type, bundle_count=edge.bundle_count)
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
            if hasattr(item, "set_selected_state"):
                item.set_selected_state(is_selected)
                continue

    def toggle_node_expansion(self, node_id: NodeId) -> None:
        child_ids = self._member_nodes_by_parent.get(node_id, [])
        if not child_ids:
            return
        if node_id in self._collapsed_nodes:
            self._collapsed_nodes.remove(node_id)
            self._animate_child_nodes(node_id, child_ids, expand=True)
            return
        self._collapsed_nodes.add(node_id)
        self._animate_child_nodes(node_id, child_ids, expand=False)

    def get_node_item(self, node_id: NodeId) -> QGraphicsObject | None:
        return self._node_items.get(node_id)

    def _animate_child_nodes(
        self,
        parent_id: NodeId,
        child_ids: list[NodeId],
        *,
        expand: bool,
    ) -> None:
        parent_item = self._node_items.get(parent_id)
        if parent_item is None:
            return
        collapsed_origin = parent_item.pos() + QPointF(28, 68)
        for index, child_id in enumerate(child_ids):
            child_item = self._node_items.get(child_id)
            if child_item is None:
                continue
            if expand:
                child_item.setVisible(True)
                child_item.setOpacity(0.0)
                child_item.setPos(collapsed_origin + QPointF(index * 6, index * 6))
            animation = self._build_node_animation(
                child_item,
                start_pos=child_item.pos(),
                end_pos=self._node_positions.get(child_id, child_item.pos())
                if expand
                else collapsed_origin + QPointF(index * 6, index * 6),
                start_opacity=child_item.opacity(),
                end_opacity=1.0 if expand else 0.0,
                hide_when_finished=not expand,
            )
            animation.start()
            self._active_animations.append(animation)
        self._sync_edge_visibility(child_ids, visible=expand)

    def _build_node_animation(
        self,
        item: QGraphicsObject,
        *,
        start_pos: QPointF,
        end_pos: QPointF,
        start_opacity: float,
        end_opacity: float,
        hide_when_finished: bool,
    ) -> QParallelAnimationGroup:
        group = QParallelAnimationGroup(self)

        pos_animation = QPropertyAnimation(item, b"pos", group)
        pos_animation.setDuration(180)
        pos_animation.setStartValue(start_pos)
        pos_animation.setEndValue(end_pos)
        pos_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        group.addAnimation(pos_animation)

        opacity_animation = QPropertyAnimation(item, b"opacity", group)
        opacity_animation.setDuration(180)
        opacity_animation.setStartValue(start_opacity)
        opacity_animation.setEndValue(end_opacity)
        opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        group.addAnimation(opacity_animation)

        if hide_when_finished:
            group.finished.connect(lambda target=item: target.setVisible(False))
        group.finished.connect(lambda completed=group: self._discard_animation(completed))
        return group

    def _discard_animation(self, animation: QParallelAnimationGroup) -> None:
        self._active_animations = [
            active_animation
            for active_animation in self._active_animations
            if active_animation is not animation
        ]

    def _sync_edge_visibility(self, child_ids: list[NodeId], *, visible: bool) -> None:
        child_id_set = set(child_ids)
        for edge_id, edge_item in self._edge_items.items():
            source, target = self._edge_endpoints[edge_id]
            if source in child_id_set or target in child_id_set:
                edge_item.setVisible(visible)
