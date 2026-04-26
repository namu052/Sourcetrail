"""Symbol dock showing the current Python file outline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, QSortFilterProxyModel, Qt, pyqtSlot
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QDockWidget,
    QHBoxLayout,
    QLineEdit,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.core.types import AccessKind, NodeType
from sourcetrail_remake.indexer.symbol_index import (
    SymbolIconKind,
    SymbolIndex,
    SymbolOutlineItem,
    SymbolSortMode,
)

ROLE_ITEM = int(Qt.ItemDataRole.UserRole) + 1
ROLE_NAME = int(Qt.ItemDataRole.UserRole) + 2
ROLE_LINE = int(Qt.ItemDataRole.UserRole) + 3
ROLE_KIND = int(Qt.ItemDataRole.UserRole) + 4
INVALID_INDEX = QModelIndex()


@dataclass(slots=True)
class _SymbolNode:
    item: SymbolOutlineItem | None
    parent: _SymbolNode | None = None
    children: list[_SymbolNode] = field(default_factory=list)

    def row(self) -> int:
        if self.parent is None:
            return 0
        return self.parent.children.index(self)


class SymbolTreeModel(QAbstractItemModel):
    """Tree model for a file outline."""

    headers = ("Symbol", "Type", "Access", "Line")

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._root = _SymbolNode(None)
        self._icons = _build_icons()

    def set_symbols(self, symbols: tuple[SymbolOutlineItem, ...]) -> None:
        self.beginResetModel()
        self._root = _SymbolNode(None)
        self._root.children = [self._build_node(item, self._root) for item in symbols]
        self.endResetModel()

    def item_from_index(self, index: QModelIndex) -> SymbolOutlineItem | None:
        if not index.isValid():
            return None
        node = index.internalPointer()
        if not isinstance(node, _SymbolNode):
            return None
        return node.item

    def index(
        self,
        row: int,
        column: int,
        parent: QModelIndex = INVALID_INDEX,
    ) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        parent_node = self._node_from_index(parent)
        try:
            child = parent_node.children[row]
        except IndexError:
            return QModelIndex()
        return self.createIndex(row, column, child)

    def parent(self, index: QModelIndex) -> QModelIndex:  # type: ignore[override]
        if not index.isValid():
            return QModelIndex()
        node = self._node_from_index(index)
        parent_node = node.parent
        if parent_node is None or parent_node is self._root:
            return QModelIndex()
        return self.createIndex(parent_node.row(), 0, parent_node)

    def rowCount(self, parent: QModelIndex = INVALID_INDEX) -> int:
        if parent.column() > 0:
            return 0
        return len(self._node_from_index(parent).children)

    def columnCount(self, parent: QModelIndex = INVALID_INDEX) -> int:
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = int(Qt.ItemDataRole.DisplayRole)) -> Any:
        if not index.isValid():
            return None
        item = self.item_from_index(index)
        if item is None:
            return None
        if role == int(Qt.ItemDataRole.DisplayRole):
            return self._display_value(item, index.column())
        if role == int(Qt.ItemDataRole.DecorationRole) and index.column() == 0:
            return self._icons[item.icon_kind]
        if role == ROLE_ITEM:
            return item
        if role == ROLE_NAME:
            return item.name.lower()
        if role == ROLE_LINE:
            return item.line
        if role == ROLE_KIND:
            return self._type_label(item)
        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = int(Qt.ItemDataRole.DisplayRole),
    ) -> str | None:
        if orientation == Qt.Orientation.Horizontal and role == int(Qt.ItemDataRole.DisplayRole):
            return self.headers[section]
        return None

    def _build_node(self, item: SymbolOutlineItem, parent: _SymbolNode) -> _SymbolNode:
        node = _SymbolNode(item, parent)
        node.children = [self._build_node(child, node) for child in item.children]
        return node

    def _node_from_index(self, index: QModelIndex) -> _SymbolNode:
        if not index.isValid():
            return self._root
        node = index.internalPointer()
        if isinstance(node, _SymbolNode):
            return node
        return self._root

    def _display_value(self, item: SymbolOutlineItem, column: int) -> str:
        if column == 0:
            return item.name
        if column == 1:
            return self._type_label(item)
        if column == 2:
            return _access_label(item.access)
        if column == 3:
            return str(item.line)
        return ""

    def _type_label(self, item: SymbolOutlineItem) -> str:
        if item.icon_kind == SymbolIconKind.PROPERTY:
            return "property"
        if item.icon_kind == SymbolIconKind.STATIC:
            return "static"
        if item.node_type == NodeType.NODE_CLASS:
            return "class"
        if item.node_type == NodeType.NODE_METHOD:
            return "method"
        if item.node_type == NodeType.NODE_FUNCTION:
            return "function"
        if item.node_type == NodeType.NODE_FIELD:
            return "field"
        return "variable"


class SymbolFilterProxyModel(QSortFilterProxyModel):
    """Recursive case-insensitive filter over symbol names."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setRecursiveFilteringEnabled(True)

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        sort_role = self.sortRole()
        left_value = left.data(sort_role)
        right_value = right.data(sort_role)
        if isinstance(left_value, int) and isinstance(right_value, int):
            return left_value < right_value
        return str(left_value) < str(right_value)


class SymbolWindow(QDockWidget):
    """Dock widget for D51-D60 Symbol Window behavior."""

    def __init__(
        self,
        event_bus: EventBus,
        index: SymbolIndex,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("Symbols", parent)
        self.event_bus = event_bus
        self.index = index
        self.current_file = ""
        self.sort_mode = SymbolSortMode.DECLARATION
        self.setObjectName("symbol-window-dock")
        self._build_ui()
        self.event_bus.file_opened.connect(self.on_file_opened)
        self.event_bus.file_saved.connect(self.on_file_saved)

    @pyqtSlot(str, int)
    def on_file_opened(self, file: str, _line: int = 1) -> None:
        self.current_file = file
        self.reload(force=False)

    @pyqtSlot(str)
    def on_file_saved(self, file: str) -> None:
        if self.current_file and file == self.current_file:
            self.reload(force=True)

    def reload(self, *, force: bool = False) -> None:
        if not self.current_file:
            self.model.set_symbols(())
            return
        symbols = (
            self.index.refresh_file(self.current_file, sort_mode=self.sort_mode)
            if force
            else self.index.load_file(self.current_file, sort_mode=self.sort_mode)
        )
        self.model.set_symbols(symbols)
        self.tree.expandAll()
        self.tree.resizeColumnToContents(0)

    def _build_ui(self) -> None:
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        toolbar = QWidget(container)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(8)

        self.filter_edit = QLineEdit(toolbar)
        self.filter_edit.setObjectName("symbol-filter-edit")
        self.filter_edit.setPlaceholderText("Filter symbols")

        self.sort_combo = QComboBox(toolbar)
        self.sort_combo.setObjectName("symbol-sort-combo")
        self.sort_combo.addItem("Declaration", SymbolSortMode.DECLARATION.value)
        self.sort_combo.addItem("Alphabetical", SymbolSortMode.ALPHABETICAL.value)

        toolbar_layout.addWidget(self.filter_edit, stretch=1)
        toolbar_layout.addWidget(self.sort_combo)

        self.model = SymbolTreeModel(container)
        self.proxy_model = SymbolFilterProxyModel(container)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterKeyColumn(0)
        self.proxy_model.setSortRole(ROLE_LINE)

        self.tree = QTreeView(container)
        self.tree.setObjectName("symbol-tree-view")
        self.tree.setModel(self.proxy_model)
        self.tree.setRootIsDecorated(True)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(False)
        self.tree.doubleClicked.connect(self._open_index)

        self.filter_edit.textChanged.connect(self.proxy_model.setFilterFixedString)
        self.sort_combo.currentIndexChanged.connect(self._change_sort_mode)

        layout.addWidget(toolbar)
        layout.addWidget(self.tree, stretch=1)
        self.setWidget(container)

    def _change_sort_mode(self, index: int) -> None:
        data = self.sort_combo.itemData(index)
        self.sort_mode = SymbolSortMode(str(data))
        self.proxy_model.setSortRole(
            ROLE_NAME if self.sort_mode == SymbolSortMode.ALPHABETICAL else ROLE_LINE
        )
        self.reload(force=False)

    def _open_index(self, index: QModelIndex) -> None:
        source_index = self.proxy_model.mapToSource(index)
        item = self.model.item_from_index(source_index)
        if item is None or not self.current_file:
            return
        self.event_bus.file_opened.emit(self.current_file, item.line)


def _access_label(access: AccessKind) -> str:
    if access == AccessKind.ACCESS_PRIVATE:
        return "private"
    if access == AccessKind.ACCESS_PROTECTED:
        return "protected"
    return "public"


def _build_icons() -> dict[SymbolIconKind, QIcon]:
    colors = {
        SymbolIconKind.CLASS: "#8250df",
        SymbolIconKind.FUNCTION: "#0969da",
        SymbolIconKind.METHOD: "#1a7f37",
        SymbolIconKind.FIELD: "#bf8700",
        SymbolIconKind.PROPERTY: "#cf222e",
        SymbolIconKind.STATIC: "#6f42c1",
        SymbolIconKind.VARIABLE: "#57606a",
    }
    return {kind: _square_icon(color) for kind, color in colors.items()}


def _square_icon(color: str) -> QIcon:
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(color))
    painter.setPen(QColor("#24292f"))
    painter.drawRoundedRect(2, 2, 12, 12, 2, 2)
    painter.end()
    return QIcon(pixmap)
