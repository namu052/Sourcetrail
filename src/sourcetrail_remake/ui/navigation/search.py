"""Search widgets for fully qualified symbol lookup."""

from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QWidget


class SymbolSearchBar(QWidget):
    """Line edit used for exact FQN navigation."""

    search_requested = pyqtSignal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("symbol-search-bar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.line_edit = QLineEdit(self)
        self.line_edit.setObjectName("fqn-search-line-edit")
        self.line_edit.setPlaceholderText("Search Fully Qualified Name")
        self.line_edit.returnPressed.connect(self._emit_search)
        layout.addWidget(self.line_edit)

    def set_current_symbol(self, serialized_name: str) -> None:
        self.line_edit.setText(serialized_name)

    def _emit_search(self) -> None:
        self.search_requested.emit(self.line_edit.text().strip())
