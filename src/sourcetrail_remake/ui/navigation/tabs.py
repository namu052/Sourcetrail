"""Symbol tab bar widgets."""

from __future__ import annotations

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import QTabBar, QWidget

from sourcetrail_remake.core.types import GraphNodeRecord, NodeId, NodeType


class SymbolTabBar(QTabBar):
    """Small tab strip that tracks the currently focused symbol."""

    symbol_requested = pyqtSignal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("symbol-tab-bar")
        self.setDocumentMode(True)
        self.setDrawBase(False)
        self.setMovable(True)
        self.setUsesScrollButtons(True)
        self.setElideMode(Qt.TextElideMode.ElideRight)
        self.setIconSize(QSize(14, 14))
        self.currentChanged.connect(self._emit_current_symbol)

    def open_symbol(self, symbol: GraphNodeRecord) -> None:
        existing_index = self._find_index(symbol.id)
        if existing_index is None:
            index = self.addTab(_tab_icon(symbol.node_type), symbol.display_name)
            self.setTabData(index, int(symbol.id))
            self.setTabToolTip(index, symbol.serialized_name)
            self.setCurrentIndex(index)
            return
        self.setCurrentIndex(existing_index)
        self.setTabText(existing_index, symbol.display_name)
        self.setTabToolTip(existing_index, symbol.serialized_name)

    def current_symbol_id(self) -> NodeId | None:
        current_index = self.currentIndex()
        if current_index < 0:
            return None
        return NodeId(int(self.tabData(current_index)))

    def _find_index(self, symbol_id: NodeId) -> int | None:
        for index in range(self.count()):
            tab_data = self.tabData(index)
            if tab_data is not None and int(tab_data) == int(symbol_id):
                return index
        return None

    def _emit_current_symbol(self, index: int) -> None:
        if index < 0:
            return
        tab_data = self.tabData(index)
        if tab_data is None:
            return
        self.symbol_requested.emit(NodeId(int(tab_data)))


def _tab_icon(node_type: NodeType) -> QIcon:
    pixmap = QPixmap(14, 14)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setPen(QColor("#ffffff"))
    painter.setBrush(_tab_color(node_type))
    painter.drawEllipse(1, 1, 12, 12)
    painter.end()
    return QIcon(pixmap)


def _tab_color(node_type: NodeType) -> QColor:
    if node_type == NodeType.NODE_CLASS:
        return QColor("#2563eb")
    if node_type == NodeType.NODE_METHOD:
        return QColor("#f97316")
    if node_type == NodeType.NODE_FIELD:
        return QColor("#16a34a")
    if node_type == NodeType.NODE_FUNCTION:
        return QColor("#7c3aed")
    return QColor("#64748b")
