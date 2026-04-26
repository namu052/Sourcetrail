"""Week 22 shortcut conflict checks."""

from __future__ import annotations

import pytest
from PyQt6.QtGui import QAction, QKeySequence, QShortcut
from PyQt6.QtWidgets import QWidget

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.ui.main_window import create_main_window
from sourcetrail_remake.ui.shortcuts import (
    collect_shortcut_bindings,
    find_shortcut_conflicts,
)


@pytest.mark.ui
def test_main_window_shortcuts_do_not_conflict(qtbot) -> None:
    window = create_main_window(EventBus())
    qtbot.addWidget(window)

    bindings = collect_shortcut_bindings(window)

    assert {binding.sequence for binding in bindings} >= {
        "Ctrl+Alt+1",
        "Ctrl+Alt+2",
        "Ctrl+Alt+3",
        "Ctrl+Alt+4",
        "Shift+F12",
    }
    assert find_shortcut_conflicts(bindings) == ()


@pytest.mark.ui
def test_shortcut_conflict_detector_reports_duplicate_sequences(qtbot) -> None:
    widget = QWidget()
    qtbot.addWidget(widget)
    action = QAction("Open A", widget)
    action.setShortcut(QKeySequence("Ctrl+P"))
    widget.addAction(action)
    shortcut = QShortcut(QKeySequence("Ctrl+P"), widget)
    shortcut.setObjectName("quick-open-shortcut")

    conflicts = find_shortcut_conflicts(collect_shortcut_bindings(widget))

    assert len(conflicts) == 1
    assert conflicts[0].sequence == "Ctrl+P"
    assert {binding.owner for binding in conflicts[0].bindings} == {
        "Open A",
        "quick-open-shortcut",
    }
