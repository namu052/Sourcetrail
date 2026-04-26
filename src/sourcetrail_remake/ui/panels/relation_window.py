"""Relation dock for browsing calls, references, and override links."""

from __future__ import annotations

from enum import StrEnum

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QSlider,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.core.types import NodeId
from sourcetrail_remake.indexer.relation_query import Occurrence, Relation, RelationQuery


class RelationAxis(StrEnum):
    """Supported Relation Window tabs."""

    CALLED_BY = "Called by"
    CALLS = "Calls"
    REFERENCES = "References"
    OVERRIDES = "Overrides"


ROLE_NODE_ID = int(Qt.ItemDataRole.UserRole)
ROLE_AXIS = int(Qt.ItemDataRole.UserRole) + 1
ROLE_LOADED = int(Qt.ItemDataRole.UserRole) + 2
PLACEHOLDER_TEXT = "Loading..."
EMPTY_TEXT = "관계가 없습니다"
RECURSIVE_TEXT = "(recursive)"


class RelationWindow(QDockWidget):
    """Tree-mode relation panel for the currently selected symbol."""

    def __init__(
        self,
        event_bus: EventBus,
        query: RelationQuery,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("Relations", parent)
        self.event_bus = event_bus
        self.query = query
        self.current_node_id: NodeId | None = None
        self.max_depth = 3
        self.setObjectName("relation-window-dock")
        self._trees: dict[RelationAxis, QTreeWidget] = {}
        self._build_ui()
        self.event_bus.symbol_selected.connect(self.on_symbol_selected)

    @pyqtSlot(int)
    def on_symbol_selected(self, node_id: int) -> None:
        self.current_node_id = NodeId(int(node_id))
        self.reload()

    def reload(self) -> None:
        for axis, tree in self._trees.items():
            tree.clear()
            if self.current_node_id is None:
                self._show_empty(tree)
                continue
            self._populate_axis(axis, tree, self.current_node_id, depth=0)

    def _build_ui(self) -> None:
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        depth_bar = QWidget(container)
        depth_layout = QHBoxLayout(depth_bar)
        depth_layout.setContentsMargins(0, 0, 0, 0)
        self.depth_label = QLabel("Depth: 3", depth_bar)
        self.depth_slider = QSlider(Qt.Orientation.Horizontal, depth_bar)
        self.depth_slider.setObjectName("relation-depth-slider")
        self.depth_slider.setRange(1, 5)
        self.depth_slider.setValue(self.max_depth)
        self.depth_slider.valueChanged.connect(self._set_depth)
        depth_layout.addWidget(self.depth_label)
        depth_layout.addWidget(self.depth_slider, stretch=1)

        self.tabs = QTabWidget(container)
        self.tabs.setObjectName("relation-tabs")
        for axis in RelationAxis:
            tree = QTreeWidget(self.tabs)
            tree.setObjectName(f"relation-tree-{axis.name.lower()}")
            tree.setHeaderLabels(["Symbol", "Kind"])
            tree.itemExpanded.connect(lambda item, axis=axis: self._expand_item(axis, item))
            tree.itemDoubleClicked.connect(self._activate_item)
            self._trees[axis] = tree
            self.tabs.addTab(tree, axis.value)

        layout.addWidget(depth_bar)
        layout.addWidget(self.tabs, stretch=1)
        self.setWidget(container)

    def _set_depth(self, value: int) -> None:
        self.max_depth = value
        self.depth_label.setText(f"Depth: {value}")
        self.reload()

    def _populate_axis(
        self,
        axis: RelationAxis,
        tree: QTreeWidget,
        node_id: NodeId,
        *,
        depth: int,
    ) -> None:
        if axis == RelationAxis.REFERENCES:
            occurrences = self.query.get_references(node_id)
            if not occurrences:
                self._show_empty(tree)
                return
            for occurrence in occurrences:
                tree.addTopLevelItem(self._occurrence_item(occurrence))
            return

        relations = self._relations_for_axis(axis, node_id, depth)
        if not relations:
            self._show_empty(tree)
            return
        for relation in relations:
            tree.addTopLevelItem(self._relation_item(axis, relation))

    def _expand_item(self, axis: RelationAxis, item: QTreeWidgetItem) -> None:
        if item.data(0, ROLE_LOADED):
            return
        item.setData(0, ROLE_LOADED, True)
        self._clear_placeholder(item)
        node_id = item.data(0, ROLE_NODE_ID)
        if node_id is None:
            return
        current_depth = self._item_depth(item)
        if current_depth >= self.max_depth:
            item.addChild(QTreeWidgetItem([RECURSIVE_TEXT, "depth limit"]))
            return
        relations = self._relations_for_axis(axis, NodeId(int(node_id)), current_depth)
        if not relations:
            item.addChild(QTreeWidgetItem([EMPTY_TEXT, ""]))
            return
        for relation in relations:
            item.addChild(self._relation_item(axis, relation))

    def _activate_item(self, item: QTreeWidgetItem, _column: int) -> None:
        node_id = item.data(0, ROLE_NODE_ID)
        if node_id is None:
            return
        self.event_bus.symbol_selected.emit(int(node_id))

    def _relations_for_axis(
        self,
        axis: RelationAxis,
        node_id: NodeId,
        depth: int,
    ) -> list[Relation]:
        remaining_depth = max(self.max_depth - depth, 1)
        if axis == RelationAxis.CALLED_BY:
            return self.query.get_callers(node_id, depth=remaining_depth)
        if axis == RelationAxis.CALLS:
            return self.query.get_callees(node_id, depth=remaining_depth)
        if axis == RelationAxis.OVERRIDES:
            return self.query.get_override_relations(node_id, depth=remaining_depth)
        return []

    def _relation_item(self, axis: RelationAxis, relation: Relation) -> QTreeWidgetItem:
        label = relation.display_name
        if relation.is_recursive:
            label = f"{label} {RECURSIVE_TEXT}"
        item = QTreeWidgetItem([label, relation.edge_type.name.removeprefix("EDGE_").lower()])
        item.setData(0, ROLE_NODE_ID, int(relation.node_id))
        item.setData(0, ROLE_AXIS, axis.value)
        item.setData(0, ROLE_LOADED, False)
        if relation.depth < self.max_depth and not relation.is_recursive:
            item.addChild(QTreeWidgetItem([PLACEHOLDER_TEXT, ""]))
        return item

    def _occurrence_item(self, occurrence: Occurrence) -> QTreeWidgetItem:
        path = "<unknown>" if occurrence.file_path is None else occurrence.file_path.name
        item = QTreeWidgetItem(
            [
                f"{occurrence.label}:{occurrence.start_line}:{occurrence.start_column}",
                path,
            ]
        )
        item.setData(0, ROLE_NODE_ID, occurrence.element_id)
        item.setData(0, ROLE_LOADED, True)
        return item

    def _show_empty(self, tree: QTreeWidget) -> None:
        item = QTreeWidgetItem([EMPTY_TEXT, ""])
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
        tree.addTopLevelItem(item)

    def _clear_placeholder(self, item: QTreeWidgetItem) -> None:
        for index in reversed(range(item.childCount())):
            child = item.child(index)
            if child is not None and child.text(0) == PLACEHOLDER_TEXT:
                item.removeChild(child)

    def _item_depth(self, item: QTreeWidgetItem) -> int:
        depth = 1
        parent = item.parent()
        while parent is not None:
            depth += 1
            parent = parent.parent()
        return depth
