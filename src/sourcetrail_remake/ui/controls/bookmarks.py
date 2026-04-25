"""Bookmark controls for the graph UI."""

from __future__ import annotations

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu, QToolButton, QVBoxLayout, QWidget

from sourcetrail_remake.core.types import GraphNodeRecord, NodeId


class BookmarkControl(QWidget):
    """Bookmark star with a popup list of saved symbols."""

    bookmark_selected = pyqtSignal(object)
    bookmark_toggled = pyqtSignal(object, bool)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("bookmark-control")
        self.current_symbol: GraphNodeRecord | None = None
        self._bookmarks: dict[NodeId, GraphNodeRecord] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.button = QToolButton(self)
        self.button.setObjectName("bookmark-toggle-button")
        self.button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.button.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.button.clicked.connect(self.toggle_current)
        self.menu = QMenu(self.button)
        self.button.setMenu(self.menu)
        layout.addWidget(self.button)
        self._refresh_button()

    def set_current_symbol(self, symbol: GraphNodeRecord | None) -> None:
        self.current_symbol = symbol
        self._refresh_button()
        self._rebuild_menu()

    def bookmarks(self) -> tuple[GraphNodeRecord, ...]:
        return tuple(self._bookmarks.values())

    def toggle_current(self) -> None:
        if self.current_symbol is None:
            return
        symbol_id = self.current_symbol.id
        if symbol_id in self._bookmarks:
            del self._bookmarks[symbol_id]
            self.bookmark_toggled.emit(symbol_id, False)
        else:
            self._bookmarks[symbol_id] = self.current_symbol
            self.bookmark_toggled.emit(symbol_id, True)
        self._refresh_button()
        self._rebuild_menu()

    def _refresh_button(self) -> None:
        if self.current_symbol is None:
            self.button.setText("☆")
            self.button.setEnabled(False)
            return
        is_bookmarked = self.current_symbol.id in self._bookmarks
        self.button.setEnabled(True)
        self.button.setText("★" if is_bookmarked else "☆")

    def _rebuild_menu(self) -> None:
        self.menu.clear()
        for symbol in self._bookmarks.values():
            action = QAction(symbol.serialized_name, self.menu)
            action.triggered.connect(
                lambda checked=False, node_id=symbol.id: self.bookmark_selected.emit(node_id)
            )
            self.menu.addAction(action)
