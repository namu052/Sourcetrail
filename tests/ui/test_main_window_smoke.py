"""Qt smoke tests for the bootstrap shell."""

from __future__ import annotations

import pytest
from PyQt6.QtWidgets import QDockWidget, QStatusBar

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.ui.main_window import create_main_window


@pytest.mark.ui
def test_main_window_smoke(qtbot) -> None:
    window = create_main_window(EventBus())
    qtbot.addWidget(window)
    window.show()
    assert window.windowTitle() == "Sourcetrail_Remake"
    assert window.centralWidget() is not None
    assert window.findChild(QStatusBar) is not None
    assert window.findChild(QDockWidget, "graph-overview-dock") is not None
    assert window.findChild(QDockWidget, "graph-selection-dock") is not None
    assert window.findChild(QDockWidget, "graph-log-dock") is not None
