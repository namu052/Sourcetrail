"""Depth control widgets for the graph view."""

from __future__ import annotations

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QSlider, QVBoxLayout, QWidget


class DepthControl(QWidget):
    """Vertical slider that controls graph expansion depth."""

    value_changed = pyqtSignal(int)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("depth-control")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title = QLabel("Depth", self)
        title.setObjectName("depth-control-title")
        self.value_label = QLabel("1", self)
        self.value_label.setObjectName("depth-control-value")
        self.slider = QSlider(Qt.Orientation.Vertical, self)
        self.slider.setObjectName("depth-slider")
        self.slider.setRange(1, 10)
        self.slider.setValue(1)
        self.slider.valueChanged.connect(self._on_value_changed)

        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.value_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.slider, alignment=Qt.AlignmentFlag.AlignHCenter)

    def value(self) -> int:
        return self.slider.value()

    def set_value(self, value: int) -> None:
        self.slider.setValue(value)

    def _on_value_changed(self, value: int) -> None:
        self.value_label.setText(str(value))
        self.value_changed.emit(value)
