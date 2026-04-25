"""Search widgets for fully qualified symbol lookup."""

from __future__ import annotations

from rapidfuzz import fuzz, process

from PyQt6.QtCore import QObject, QStringListModel, Qt, pyqtSignal
from PyQt6.QtWidgets import QCompleter, QHBoxLayout, QLineEdit, QWidget

from sourcetrail_remake.core.types import GraphNodeRecord


class SymbolSearchBar(QWidget):
    """Line edit used for exact FQN navigation."""

    search_requested = pyqtSignal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("symbol-search-bar")
        self._catalog: tuple[GraphNodeRecord, ...] = ()
        self._suggestions: tuple[str, ...] = ()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.line_edit = QLineEdit(self)
        self.line_edit.setObjectName("fqn-search-line-edit")
        self.line_edit.setPlaceholderText("Search Fully Qualified Name")
        self.line_edit.returnPressed.connect(self._emit_search)
        self.line_edit.textEdited.connect(self._update_completions)
        layout.addWidget(self.line_edit)

        self.completer_model = QStringListModel(self)
        self.completer = QCompleter(self.completer_model, self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.activated.connect(self._apply_completion)
        self.line_edit.setCompleter(self.completer)

    def set_current_symbol(self, serialized_name: str) -> None:
        self.line_edit.setText(serialized_name)

    def set_catalog(self, symbols: tuple[GraphNodeRecord, ...]) -> None:
        self._catalog = symbols

    def suggestions(self) -> tuple[str, ...]:
        return self._suggestions

    def _emit_search(self) -> None:
        self.search_requested.emit(self.line_edit.text().strip())

    def _update_completions(self, query: str) -> None:
        normalized_query = query.strip()
        if not normalized_query:
            self._suggestions = ()
            self.completer_model.setStringList([])
            return

        exact_matches = [
            symbol.serialized_name
            for symbol in self._catalog
            if normalized_query.casefold() in symbol.serialized_name.casefold()
        ][:5]
        fuzzy_matches = [
            match[0]
            for match in process.extract(
                normalized_query,
                [symbol.serialized_name for symbol in self._catalog],
                scorer=fuzz.WRatio,
                limit=8,
            )
            if match[0] not in exact_matches and match[1] >= 40
        ]
        self._suggestions = tuple([*exact_matches, *fuzzy_matches][:8])
        self.completer_model.setStringList(list(self._suggestions))
        if self._suggestions:
            self.completer.complete()

    def _apply_completion(self, text: str) -> None:
        self.line_edit.setText(text)
        self.search_requested.emit(text)
