"""Zoom controls for the graph view."""

from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class ZoomControl(QWidget):
    """Compact +/- zoom buttons with a percentage label."""

    zoom_in_requested = pyqtSignal()
    zoom_out_requested = pyqtSignal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("zoom-control")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.zoom_out_button = QPushButton("-", self)
        self.zoom_out_button.setObjectName("zoom-out-button")
        self.zoom_out_button.clicked.connect(self.zoom_out_requested.emit)

        self.zoom_in_button = QPushButton("+", self)
        self.zoom_in_button.setObjectName("zoom-in-button")
        self.zoom_in_button.clicked.connect(self.zoom_in_requested.emit)

        self.value_label = QLabel("100%", self)
        self.value_label.setObjectName("zoom-value-label")

        layout.addWidget(QLabel("Zoom", self))
        layout.addWidget(self.zoom_out_button)
        layout.addWidget(self.zoom_in_button)
        layout.addWidget(self.value_label)

    def set_zoom_percent(self, zoom_percent: int) -> None:
        self.value_label.setText(f"{zoom_percent}%")
