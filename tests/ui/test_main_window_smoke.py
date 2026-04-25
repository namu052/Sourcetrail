"""Qt smoke tests for the bootstrap shell."""

from __future__ import annotations

import pytest

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.ui.main_window import create_main_window


@pytest.mark.ui
def test_main_window_smoke(qtbot) -> None:
    window = create_main_window(EventBus())
    qtbot.addWidget(window)
    window.show()
    assert window.windowTitle() == "Sourcetrail_Remake"
