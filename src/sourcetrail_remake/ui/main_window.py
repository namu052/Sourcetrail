"""Main application window for the graph UI."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QLabel,
    QDockWidget,
    QHBoxLayout,
    QMainWindow,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from sourcetrail_remake.core.config import DEFAULT_CONFIG
from sourcetrail_remake.core.types import GraphNodeRecord, NodeId
from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.ui.controls.depth import DepthControl
from sourcetrail_remake.ui.controls.zoom import ZoomControl
from sourcetrail_remake.ui.graph.scene import GraphScene
from sourcetrail_remake.ui.graph.view import GraphView
from sourcetrail_remake.ui.navigation.history import HistoryNavigator
from sourcetrail_remake.ui.navigation.search import SymbolSearchBar
from sourcetrail_remake.ui.navigation.tabs import SymbolTabBar


class MainWindow(QMainWindow):
    """Application shell with the dock layout required for the graph workflow."""

    def __init__(
        self,
        event_bus: EventBus,
        *,
        reader: DatabaseReader | None = None,
        initial_symbol_id: NodeId | None = None,
    ):
        super().__init__()
        self.event_bus = event_bus
        self.reader = reader
        self.initial_symbol_id = initial_symbol_id
        self.current_symbol_id: NodeId | None = None
        self.current_depth = 1
        self.home_symbol_id: NodeId | None = initial_symbol_id
        self.history_entries: list[NodeId] = []
        self.history_index = -1
        self.graph_scene = GraphScene(reader=reader, event_bus=event_bus)
        self.graph_view = GraphView(self.graph_scene)
        self.setWindowTitle(DEFAULT_CONFIG.main_window_title)
        self.resize(1440, 900)
        self._build_shell()
        self._connect_signals()
        if self.reader is not None:
            self.search_bar.set_catalog(self.reader.list_symbols())
        if self.reader is not None and self.initial_symbol_id is not None:
            self.focus_symbol(self.initial_symbol_id)

    def _build_shell(self) -> None:
        self.setDockNestingEnabled(True)
        self.setDocumentMode(True)

        central = QWidget(self)
        central.setObjectName("graph-central-shell")
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(12, 12, 12, 12)
        central_layout.setSpacing(10)
        central_layout.addWidget(self._create_navigation_strip())
        central_layout.addWidget(self.graph_view)
        self.setCentralWidget(central)

        self._add_dock(
            title="Graph Overview",
            area=Qt.DockWidgetArea.LeftDockWidgetArea,
            object_name="graph-overview-dock",
            widget=self._create_overview_panel(),
        )
        self._add_dock(
            title="Selection",
            area=Qt.DockWidgetArea.RightDockWidgetArea,
            object_name="graph-selection-dock",
            widget=self._create_selection_panel(),
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

    def _connect_signals(self) -> None:
        self.event_bus.symbol_selected.connect(self._on_symbol_selected)
        self.symbol_tabs.symbol_requested.connect(self._focus_symbol_from_tab)
        self.history_navigator.back_requested.connect(self.navigate_back)
        self.history_navigator.forward_requested.connect(self.navigate_forward)
        self.history_navigator.home_requested.connect(self.navigate_home)
        self.history_navigator.history_requested.connect(self.navigate_to_history_entry)
        self.search_bar.search_requested.connect(self.focus_symbol_by_name)
        self.depth_control.value_changed.connect(self._on_depth_changed)
        self.zoom_control.zoom_in_requested.connect(self.zoom_in)
        self.zoom_control.zoom_out_requested.connect(self.zoom_out)

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

    def _create_navigation_strip(self) -> QWidget:
        strip = QWidget(self)
        strip.setObjectName("graph-navigation-strip")
        layout = QHBoxLayout(strip)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.history_navigator = HistoryNavigator(strip)
        navigation_label = QLabel("Symbols", strip)
        navigation_label.setObjectName("graph-navigation-label")
        self.symbol_tabs = SymbolTabBar(strip)
        self.search_bar = SymbolSearchBar(strip)

        layout.addWidget(self.history_navigator)
        layout.addWidget(navigation_label)
        layout.addWidget(self.symbol_tabs, stretch=1)
        layout.addWidget(self.search_bar, stretch=1)
        return strip

    def _create_overview_panel(self) -> QWidget:
        panel = QWidget(self)
        panel.setObjectName("graph-overview-panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        overview_label = QLabel("Overview", panel)
        overview_label.setObjectName("overview-heading-label")
        helper_label = QLabel("Adjust BFS expansion depth for the current graph.", panel)
        helper_label.setWordWrap(True)
        helper_label.setObjectName("overview-helper-label")
        self.depth_control = DepthControl(panel)
        self.zoom_control = ZoomControl(panel)

        layout.addWidget(overview_label)
        layout.addWidget(helper_label)
        layout.addWidget(self.depth_control, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.zoom_control)
        layout.addStretch(1)
        return panel

    def _create_selection_panel(self) -> QWidget:
        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)

        heading_label = QLabel("Selection", panel)
        heading_label.setObjectName("selection-heading-label")
        self.selection_name_label = QLabel("No symbol selected", panel)
        self.selection_name_label.setObjectName("selection-name-label")
        self.selection_type_label = QLabel("Type: —", panel)
        self.selection_type_label.setObjectName("selection-type-label")
        self.selection_fqn_label = QLabel("Qualified name: —", panel)
        self.selection_fqn_label.setObjectName("selection-fqn-label")
        self.selection_fqn_label.setWordWrap(True)

        layout.addWidget(heading_label)
        layout.addWidget(self.selection_name_label)
        layout.addWidget(self.selection_type_label)
        layout.addWidget(self.selection_fqn_label)
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

    def focus_symbol(self, node_id: NodeId, *, record_history: bool = True) -> None:
        if self.reader is None:
            return
        symbol = self.reader.get_symbol(node_id)
        if symbol is None:
            return
        if self.home_symbol_id is None:
            self.home_symbol_id = node_id
        self.current_symbol_id = node_id
        self.graph_view.focus_symbol(node_id, depth=self.current_depth)
        self.symbol_tabs.open_symbol(symbol)
        self._update_selection_panel(symbol)
        self.search_bar.set_current_symbol(symbol.serialized_name)
        if record_history:
            self._push_history(node_id)
        self._update_history_controls()
        self.zoom_control.set_zoom_percent(self.graph_view.zoom_percent())

        status_bar = self.statusBar()
        assert status_bar is not None
        status_bar.showMessage(f"Focused {symbol.serialized_name}")

    def _focus_symbol_from_tab(self, node_id: NodeId) -> None:
        if self.current_symbol_id == node_id:
            return
        self.focus_symbol(node_id, record_history=False)

    def _on_symbol_selected(self, node_id: object) -> None:
        if not isinstance(node_id, int):
            node_id = int(node_id)
        self.focus_symbol(NodeId(node_id))

    def _update_selection_panel(self, symbol: GraphNodeRecord) -> None:
        self.selection_name_label.setText(symbol.display_name)
        self.selection_type_label.setText(
            f"Type: {symbol.node_type.name.removeprefix('NODE_').replace('_', ' ').title()}"
        )
        self.selection_fqn_label.setText(f"Qualified name: {symbol.serialized_name}")

    def navigate_back(self) -> None:
        if self.history_index <= 0:
            return
        self.history_index -= 1
        self.focus_symbol(self.history_entries[self.history_index], record_history=False)

    def navigate_forward(self) -> None:
        if self.history_index < 0 or self.history_index >= len(self.history_entries) - 1:
            return
        self.history_index += 1
        self.focus_symbol(self.history_entries[self.history_index], record_history=False)

    def navigate_home(self) -> None:
        if self.home_symbol_id is None:
            return
        self.focus_symbol(self.home_symbol_id, record_history=False)

    def navigate_to_history_entry(self, node_id: NodeId) -> None:
        if node_id not in self.history_entries:
            return
        self.history_index = self.history_entries.index(node_id)
        self.focus_symbol(node_id, record_history=False)

    def _push_history(self, node_id: NodeId) -> None:
        if self.history_index >= 0 and self.history_entries[self.history_index] == node_id:
            return
        if self.history_index < len(self.history_entries) - 1:
            self.history_entries = self.history_entries[: self.history_index + 1]
        self.history_entries.append(node_id)
        self.history_index = len(self.history_entries) - 1

    def _update_history_controls(self) -> None:
        self.history_navigator.update_state(
            can_go_back=self.history_index > 0,
            can_go_forward=0 <= self.history_index < len(self.history_entries) - 1,
            has_home=self.home_symbol_id is not None,
        )
        self.history_navigator.set_entries(
            [
                (entry, self._history_label(entry))
                for entry in self.history_entries
            ],
            current_index=self.history_index,
        )

    def _history_label(self, node_id: NodeId) -> str:
        if self.reader is None:
            return str(int(node_id))
        symbol = self.reader.get_symbol(node_id)
        if symbol is None:
            return str(int(node_id))
        return symbol.serialized_name

    def focus_symbol_by_name(self, serialized_name: str) -> None:
        if self.reader is None or not serialized_name:
            return
        symbol_id = self.reader.find_symbol_id(serialized_name)
        if symbol_id is None:
            status_bar = self.statusBar()
            assert status_bar is not None
            status_bar.showMessage(f"Symbol not found: {serialized_name}")
            return
        self.focus_symbol(symbol_id)

    def _on_depth_changed(self, value: int) -> None:
        self.current_depth = value
        if self.current_symbol_id is not None:
            self.focus_symbol(self.current_symbol_id, record_history=False)

    def zoom_in(self) -> None:
        self.graph_view.zoom_in()
        self.zoom_control.set_zoom_percent(self.graph_view.zoom_percent())

    def zoom_out(self) -> None:
        self.graph_view.zoom_out()
        self.zoom_control.set_zoom_percent(self.graph_view.zoom_percent())


def create_main_window(
    event_bus: EventBus,
    *,
    reader: DatabaseReader | None = None,
    initial_symbol_id: NodeId | None = None,
) -> MainWindow:
    """Construct the default main window."""
    return MainWindow(
        event_bus,
        reader=reader,
        initial_symbol_id=initial_symbol_id,
    )
