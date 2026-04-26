"""Quick-open dialog backed by the project fuzzy symbol index."""

from __future__ import annotations

from PyQt6.QtCore import QModelIndex, QSettings, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QDialog, QLineEdit, QListView, QVBoxLayout, QWidget

from sourcetrail_remake.search.fuzzy import FuzzyResult, SymbolFuzzyIndex

ROLE_NODE_ID = int(Qt.ItemDataRole.UserRole)
ROLE_FQN = int(Qt.ItemDataRole.UserRole) + 1
DEBOUNCE_MS = 50
RECENT_KEY = "quick_open/recent_fqns"
MAX_RECENT = 10


class QuickOpenDialog(QDialog):
    """Ctrl+P-style symbol launcher with debounced fuzzy search."""

    symbol_selected = pyqtSignal(int)

    def __init__(
        self,
        index: SymbolFuzzyIndex,
        parent: QWidget | None = None,
        *,
        limit: int = 50,
        settings: QSettings | None = None,
    ) -> None:
        super().__init__(parent)
        self.index = index
        self.limit = limit
        self.settings = settings or QSettings("Sourcetrail_Remake", "Sourcetrail_Remake")
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

    def recent_fqns(self) -> tuple[str, ...]:
        """Return the most recently opened symbol FQNs."""
        value = self.settings.value(RECENT_KEY, [])
        if isinstance(value, str):
            return (value,)
        if isinstance(value, list):
            return tuple(str(item) for item in value)
        return ()

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
        query = self.line_edit.text()
        self._last_results = self._pin_recent(self.index.search(query, limit=self.limit), query)
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
        fqn = self.model.data(index, ROLE_FQN)
        if node_id is None:
            return
        if fqn is not None:
            self._remember_recent(str(fqn))
        self.symbol_selected.emit(int(node_id))
        self.accept()

    def _label_for(self, result: FuzzyResult) -> str:
        return f"{result.symbol.name}    {result.symbol.fqn}"

    def _pin_recent(self, results: list[FuzzyResult], query: str) -> tuple[FuzzyResult, ...]:
        recent_fqns = self.recent_fqns()
        if not recent_fqns:
            return tuple(results)

        by_fqn = {result.symbol.fqn: result for result in results}
        if not query.strip():
            for symbol in self.index.symbols():
                if symbol.fqn in recent_fqns and symbol.fqn not in by_fqn:
                    by_fqn[symbol.fqn] = FuzzyResult(
                        symbol=symbol,
                        score=130.0,
                        match_kind="recent",
                    )

        pinned = [by_fqn[fqn] for fqn in recent_fqns if fqn in by_fqn]
        pinned_fqns = {result.symbol.fqn for result in pinned}
        remainder = [result for result in results if result.symbol.fqn not in pinned_fqns]
        return tuple([*pinned, *remainder][: self.limit])

    def _remember_recent(self, fqn: str) -> None:
        recent = [item for item in self.recent_fqns() if item != fqn]
        recent.insert(0, fqn)
        self.settings.setValue(RECENT_KEY, recent[:MAX_RECENT])
