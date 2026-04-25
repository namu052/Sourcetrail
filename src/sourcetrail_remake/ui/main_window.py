"""Minimal QMainWindow shell for Phase 0."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

from sourcetrail_remake.core.config import DEFAULT_CONFIG
from sourcetrail_remake.core.event_bus import EventBus


class MainWindow(QMainWindow):
    """Minimal application shell used for bootstrap validation."""

    def __init__(self, event_bus: EventBus):
        super().__init__()
        self.event_bus = event_bus
        self.setWindowTitle(DEFAULT_CONFIG.main_window_title)
        self.resize(1280, 720)

        message = QLabel("Phase 0 bootstrap shell")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setObjectName("phase0-shell-label")

        body = QWidget(self)
        layout = QVBoxLayout(body)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addWidget(message)

        self.setCentralWidget(body)
        status_bar = self.statusBar()
        assert status_bar is not None
        status_bar.showMessage("Ready")


def create_main_window(event_bus: EventBus) -> MainWindow:
    """Construct the default main window."""
    return MainWindow(event_bus)
