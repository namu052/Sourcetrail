"""UI coverage for QSettings layout persistence."""

from __future__ import annotations

from pathlib import Path

import pytest
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import QLabel, QMainWindow

from sourcetrail_remake.ui.layout_manager import PRESET_SPECS, LayoutManager, LayoutPreset


@pytest.mark.ui
def test_layout_manager_saves_and_restores_main_window_state(
    qtbot,
    tmp_path: Path,
) -> None:
    settings = QSettings(str(tmp_path / "layout.ini"), QSettings.Format.IniFormat)
    manager = LayoutManager(settings)
    window = QMainWindow()
    qtbot.addWidget(window)
    dock = window.addDockWidget(
        Qt.DockWidgetArea.LeftDockWidgetArea,
        _dock("dock-a"),
    )
    assert dock is None

    snapshot = manager.save(window)

    restored = QMainWindow()
    qtbot.addWidget(restored)
    restored.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, _dock("dock-a"))

    assert not snapshot.is_empty
    assert manager.restore(restored)


@pytest.mark.ui
def test_layout_manager_applies_source_insight_preset(qtbot, tmp_path: Path) -> None:
    settings = QSettings(str(tmp_path / "layout.ini"), QSettings.Format.IniFormat)
    manager = LayoutManager(settings)
    window = QMainWindow()
    qtbot.addWidget(window)
    context_dock = _dock("context-window-dock")
    window.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, context_dock)

    manager.apply_preset(window, LayoutPreset.SOURCE_INSIGHT)

    assert window.dockWidgetArea(context_dock) == Qt.DockWidgetArea.LeftDockWidgetArea
    assert set(PRESET_SPECS) == {
        LayoutPreset.READING,
        LayoutPreset.GRAPH_CENTRIC,
        LayoutPreset.REFACTOR,
        LayoutPreset.CUSTOM,
        LayoutPreset.DEFAULT,
        LayoutPreset.SOURCE_INSIGHT,
        LayoutPreset.WIDE,
    }


@pytest.mark.ui
def test_layout_manager_applies_refactor_split(qtbot, tmp_path: Path) -> None:
    from PyQt6.QtWidgets import QSplitter, QTextEdit

    settings = QSettings(str(tmp_path / "layout.ini"), QSettings.Format.IniFormat)
    manager = LayoutManager(settings)
    window = QMainWindow()
    qtbot.addWidget(window)
    splitter = QSplitter(Qt.Orientation.Horizontal, window)
    splitter.setObjectName("central-editor-splitter")
    splitter.addWidget(QTextEdit("Primary", splitter))
    secondary = QTextEdit("Secondary", splitter)
    secondary.setObjectName("refactor-secondary-editor")
    secondary.setVisible(False)
    splitter.addWidget(secondary)
    window.setCentralWidget(splitter)

    manager.apply_preset(window, LayoutPreset.REFACTOR)

    assert not secondary.isHidden()


def _dock(object_name: str):
    from PyQt6.QtWidgets import QDockWidget

    dock = QDockWidget("Dock")
    dock.setObjectName(object_name)
    dock.setWidget(QLabel("body"))
    return dock
