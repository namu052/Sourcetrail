"""Main application window for the graph UI."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QLabel,
    QDockWidget,
    QMainWindow,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from sourcetrail_remake.core.config import DEFAULT_CONFIG
from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.ui.graph.scene import GraphScene
from sourcetrail_remake.ui.graph.view import GraphView


class MainWindow(QMainWindow):
    """Application shell with the dock layout required for the graph workflow."""

    def __init__(self, event_bus: EventBus, *, reader: DatabaseReader | None = None):
        super().__init__()
        self.event_bus = event_bus
        self.reader = reader
        self.graph_scene = GraphScene(reader=reader, event_bus=event_bus)
        self.graph_view = GraphView(self.graph_scene)
        self.setWindowTitle(DEFAULT_CONFIG.main_window_title)
        self.resize(1440, 900)
        self._build_shell()

    def _build_shell(self) -> None:
        self.setDockNestingEnabled(True)
        self.setDocumentMode(True)

        central = QWidget(self)
        central.setObjectName("graph-central-shell")
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(12, 12, 12, 12)
        central_layout.addWidget(self.graph_view)
        self.setCentralWidget(central)

        self._add_dock(
            title="Graph Overview",
            area=Qt.DockWidgetArea.LeftDockWidgetArea,
            object_name="graph-overview-dock",
            widget=self._create_label_panel(
                "Overview",
                "The graph scene, depth control, and legend attach here in Week 5-6.",
            ),
        )
        self._add_dock(
            title="Selection",
            area=Qt.DockWidgetArea.RightDockWidgetArea,
            object_name="graph-selection-dock",
            widget=self._create_label_panel(
                "Selection",
                "Selected symbol details and actions will appear here.",
            ),
        )
        self._add_dock(
            title="Graph Log",
            area=Qt.DockWidgetArea.BottomDockWidgetArea,
            object_name="graph-log-dock",
            widget=self._create_log_panel(),
        )

        status_bar = self.statusBar()
        assert status_bar is not None
        status_bar.showMessage("Ready")

    def _add_dock(
        self,
        *,
        title: str,
        area: Qt.DockWidgetArea,
        object_name: str,
        widget: QWidget,
    ) -> QDockWidget:
        dock = QDockWidget(title, self)
        dock.setObjectName(object_name)
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        dock.setWidget(widget)
        self.addDockWidget(area, dock)
        return dock

    def _create_label_panel(self, heading: str, body: str) -> QWidget:
        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)

        heading_label = QLabel(heading, panel)
        heading_label.setObjectName(f"{heading.lower()}-heading-label")
        body_label = QLabel(body, panel)
        body_label.setWordWrap(True)
        body_label.setObjectName(f"{heading.lower()}-body-label")

        layout.addWidget(heading_label)
        layout.addWidget(body_label)
        layout.addStretch(1)
        return panel

    def _create_log_panel(self) -> QWidget:
        log_widget = QTextEdit(self)
        log_widget.setObjectName("graph-log-text")
        log_widget.setReadOnly(True)
        log_widget.setPlainText(
            "Week 5-6 graph rendering shell initialized.\n"
            "Graph loading, layout, and node interactions are added incrementally."
        )
        return log_widget


def create_main_window(event_bus: EventBus) -> MainWindow:
    """Construct the default main window."""
    return MainWindow(event_bus)
