"""UI coverage for the fuzzy quick-open dialog."""

from __future__ import annotations

import pytest
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import QLineEdit, QListView

from sourcetrail_remake.core.types import NodeId
from sourcetrail_remake.search.fuzzy import FuzzySymbol, SymbolFuzzyIndex
from sourcetrail_remake.ui.dialogs.quick_open import DEBOUNCE_MS, QuickOpenDialog


@pytest.mark.ui
def test_quick_open_dialog_debounces_and_lists_fuzzy_results(qtbot) -> None:
    index = SymbolFuzzyIndex()
    index._symbols = (  # noqa: SLF001 - test fixture injects a small in-memory catalog.
        FuzzySymbol(fqn="sample.SessionManager", name="SessionManager", node_id=NodeId(1)),
        FuzzySymbol(fqn="sample.build_session", name="build_session", node_id=NodeId(2)),
    )
    dialog = QuickOpenDialog(index)
    qtbot.addWidget(dialog)

    line_edit = dialog.findChild(QLineEdit, "quick-open-line-edit")
    list_view = dialog.findChild(QListView, "quick-open-results")
    assert line_edit is not None
    assert list_view is not None

    qtbot.keyClicks(line_edit, "sessm")
    qtbot.wait(DEBOUNCE_MS + 20)

    assert dialog.results()[0].symbol.fqn == "sample.SessionManager"
    assert list_view.model().rowCount() == 2


@pytest.mark.ui
def test_quick_open_dialog_emits_selected_symbol(qtbot) -> None:
    index = SymbolFuzzyIndex()
    index._symbols = (  # noqa: SLF001 - test fixture injects a small in-memory catalog.
        FuzzySymbol(fqn="sample.SessionManager", name="SessionManager", node_id=NodeId(1)),
    )
    dialog = QuickOpenDialog(index)
    qtbot.addWidget(dialog)

    selected: list[int] = []
    dialog.symbol_selected.connect(selected.append)
    dialog.set_query("SessionManager")
    qtbot.wait(DEBOUNCE_MS + 20)
    qtbot.keyClick(dialog.findChild(QLineEdit, "quick-open-line-edit"), Qt.Key.Key_Return)

    assert selected == [1]


@pytest.mark.ui
def test_quick_open_dialog_pins_recent_selection(qtbot, tmp_path) -> None:
    settings = QSettings(str(tmp_path / "quick-open.ini"), QSettings.Format.IniFormat)
    index = SymbolFuzzyIndex()
    index._symbols = (  # noqa: SLF001 - test fixture injects a small in-memory catalog.
        FuzzySymbol(fqn="sample.SessionManager", name="SessionManager", node_id=NodeId(1)),
        FuzzySymbol(fqn="sample.build_session", name="build_session", node_id=NodeId(2)),
    )
    first_dialog = QuickOpenDialog(index, settings=settings)
    qtbot.addWidget(first_dialog)

    first_dialog.set_query("build")
    qtbot.wait(DEBOUNCE_MS + 20)
    qtbot.keyClick(first_dialog.findChild(QLineEdit, "quick-open-line-edit"), Qt.Key.Key_Return)

    second_dialog = QuickOpenDialog(index, settings=settings)
    qtbot.addWidget(second_dialog)
    second_dialog.set_query("s")
    qtbot.wait(DEBOUNCE_MS + 20)

    assert second_dialog.recent_fqns() == ("sample.build_session",)
    assert second_dialog.results()[0].symbol.fqn == "sample.build_session"
