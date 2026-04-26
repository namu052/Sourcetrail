"""Quick-open dialog backed by the project fuzzy symbol index."""

from __future__ import annotations

from PyQt6.QtCore import QModelIndex, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QDialog, QLineEdit, QListView, QVBoxLayout, QWidget

from sourcetrail_remake.core.types import NodeId
from sourcetrail_remake.search.fuzzy import FuzzyResult, SymbolFuzzyIndex

ROLE_NODE_ID = int(Qt.ItemDataRole.UserRole)
ROLE_FQN = int(Qt.ItemDataRole.UserRole) + 1
DEBOUNCE_MS = 50


class QuickOpenDialog(QDialog):
    """Ctrl+P-style symbol launcher with debounced fuzzy search."""

    symbol_selected = pyqtSignal(int)

    def __init__(
        self,
        index: SymbolFuzzyIndex,
        parent: QWidget | None = None,
        *,
        limit: int = 50,
    ) -> None:
        super().__init__(parent)
        self.index = index
        self.limit = limit
        self._last_results: tuple[FuzzyResult, ...] = ()
        self.setWindowTitle("Quick Open")
        self.setObjectName("quick-open-dialog")
        self.resize(620, 420)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(DEBOUNCE_MS)
        self._timer.timeout.connect(self._run_search)

        self._build_ui()

    def results(self) -> tuple[FuzzyResult, ...]:
        """Return the currently displayed result records."""
        return self._last_results

    def set_query(self, query: str) -> None:
        """Set the query text and schedule a debounced search."""
        self.line_edit.setText(query)
        self._schedule_search(query)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.line_edit = QLineEdit(self)
        self.line_edit.setObjectName("quick-open-line-edit")
        self.line_edit.setPlaceholderText("Open Symbol")
        self.line_edit.textEdited.connect(self._schedule_search)
        self.line_edit.returnPressed.connect(self._activate_current)

        self.model = QStandardItemModel(self)
        self.list_view = QListView(self)
        self.list_view.setObjectName("quick-open-results")
        self.list_view.setModel(self.model)
        self.list_view.doubleClicked.connect(self._activate_index)

        layout.addWidget(self.line_edit)
        layout.addWidget(self.list_view, stretch=1)

    def _schedule_search(self, _query: str) -> None:
        self._timer.start()

    def _run_search(self) -> None:
        self._last_results = tuple(self.index.search(self.line_edit.text(), limit=self.limit))
        self.model.clear()
        for result in self._last_results:
            item = QStandardItem(self._label_for(result))
            item.setEditable(False)
            item.setData(int(result.symbol.node_id), ROLE_NODE_ID)
            item.setData(result.symbol.fqn, ROLE_FQN)
            self.model.appendRow(item)
        if self.model.rowCount() > 0:
            self.list_view.setCurrentIndex(self.model.index(0, 0))

    def _activate_current(self) -> None:
        index = self.list_view.currentIndex()
        if index.isValid():
            self._activate_index(index)

    def _activate_index(self, index: QModelIndex) -> None:
        node_id = self.model.data(index, ROLE_NODE_ID)
        if node_id is None:
            return
        self.symbol_selected.emit(int(node_id))
        self.accept()

    def _label_for(self, result: FuzzyResult) -> str:
        return f"{result.symbol.name}    {result.symbol.fqn}"
