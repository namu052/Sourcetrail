"""Context dock showing the declaration around the current editor cursor."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.core.types import SymbolContext
from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.ui.editor.editor import QScintillaEditor


class ContextWindow(QDockWidget):
    """Dock widget for the Phase 2 Context Window workflow."""

    def __init__(self, event_bus: EventBus, reader: DatabaseReader, parent: QWidget | None = None):
        super().__init__("Context", parent)
        self.event_bus = event_bus
        self.reader = reader
        self.current_file = ""
        self.current_line = 0
        self.setObjectName("context-window-dock")
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self._build_ui()
        self.event_bus.cursor_moved.connect(self.on_cursor_moved)

    @pyqtSlot(str, int, int)
    def on_cursor_moved(self, file: str, line: int, col: int) -> None:
        """Receive cursor movement events from the editor."""
        self.current_file = file
        self.current_line = line
        context = self.reader.find_context_at(file, line, col)
        if context is None:
            self._show_empty_context(file, line, col)
            return
        self._show_context(context)

    def _build_ui(self) -> None:
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        header = QWidget(container)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        self.breadcrumb_label = QLabel("", header)
        self.breadcrumb_label.setObjectName("context-breadcrumb-label")
        self.breadcrumb_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.status_label = QLabel("No cursor context", header)
        self.status_label.setObjectName("context-status-label")
        self.open_button = QPushButton("Open Source", header)
        self.open_button.setObjectName("context-open-source-button")
        self.open_button.setEnabled(False)

        header_layout.addWidget(self.breadcrumb_label, stretch=1)
        header_layout.addWidget(self.status_label)
        header_layout.addWidget(self.open_button)

        self.preview = QScintillaEditor(container)
        self.preview.setObjectName("context-preview-editor")
        self.preview.setReadOnly(True)
        self.preview.setMarginWidth(0, "000")

        layout.addWidget(header)
        layout.addWidget(self.preview, stretch=1)
        self.setWidget(container)

    def _show_context(self, context: SymbolContext) -> None:
        self.current_file = str(context.file_path)
        self.current_line = context.location.start_line
        breadcrumb = [item.display_name for item in context.breadcrumbs]
        breadcrumb.append(context.node.display_name)
        self.breadcrumb_label.setText(" > ".join(breadcrumb))
        self.status_label.setText(
            f"{context.file_path.name}:{context.location.start_line}:"
            f"{context.location.start_column}"
        )
        self.preview.load_text(context.source, path=context.file_path)
        self.preview.goto_line(context.location.start_line)
        self.preview.highlight_range(
            start_line=context.location.start_line,
            start_column=context.location.start_column,
            end_line=context.location.end_line,
            end_column=context.location.end_column,
        )
        self.open_button.setEnabled(True)

    def _show_empty_context(self, file: str, line: int, col: int) -> None:
        self.breadcrumb_label.setText("")
        self.status_label.setText(f"{file}:{line}:{col}")
        self.preview.load_text("")
        self.open_button.setEnabled(False)
