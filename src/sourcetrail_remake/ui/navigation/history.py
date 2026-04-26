"""History navigation widgets."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QHBoxLayout, QMenu, QToolButton, QWidget

from sourcetrail_remake.core.types import NodeId


class HistoryNavigator(QWidget):
    """Back/forward/home controls for symbol navigation."""

    back_requested = pyqtSignal()
    forward_requested = pyqtSignal()
    home_requested = pyqtSignal()
    history_requested = pyqtSignal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("history-navigator")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.back_button = QToolButton(self)
        self.back_button.setObjectName("history-back-button")
        self.back_button.setText("Back")
        self.back_button.setEnabled(False)
        self.back_button.clicked.connect(self.back_requested.emit)

        self.history_button = QToolButton(self)
        self.history_button.setObjectName("history-menu-button")
        self.history_button.setText("History")
        self.history_button.setEnabled(False)
        self.history_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.history_menu = QMenu(self.history_button)
        self.history_button.setMenu(self.history_menu)

        self.forward_button = QToolButton(self)
        self.forward_button.setObjectName("history-forward-button")
        self.forward_button.setText("Forward")
        self.forward_button.setEnabled(False)
        self.forward_button.clicked.connect(self.forward_requested.emit)

        self.home_button = QToolButton(self)
        self.home_button.setObjectName("history-home-button")
        self.home_button.setText("Home")
        self.home_button.setEnabled(False)
        self.home_button.clicked.connect(self.home_requested.emit)

        layout.addWidget(self.back_button)
        layout.addWidget(self.history_button)
        layout.addWidget(self.forward_button)
        layout.addWidget(self.home_button)

    def update_state(
        self,
        *,
        can_go_back: bool,
        can_go_forward: bool,
        has_home: bool,
    ) -> None:
        self.back_button.setEnabled(can_go_back)
        self.forward_button.setEnabled(can_go_forward)
        self.home_button.setEnabled(has_home)

    def set_entries(
        self,
        entries: list[tuple[NodeId, str]],
        *,
        current_index: int,
    ) -> None:
        self.history_menu.clear()
        self.history_button.setEnabled(bool(entries))

        for index, (node_id, label) in enumerate(entries):
            action = QAction(label, self.history_menu)
            action.setCheckable(True)
            action.setChecked(index == current_index)
            action.triggered.connect(
                lambda checked=False, selected=node_id: self.history_requested.emit(selected)
            )
            self.history_menu.addAction(action)
