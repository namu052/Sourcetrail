"""Dockable bookmark list with tag filtering."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from sourcetrail_remake.core.bookmarks import Bookmark, BookmarkStore

ROLE_FILE = int(Qt.ItemDataRole.UserRole)
ROLE_LINE = int(Qt.ItemDataRole.UserRole) + 1
ALL_TAGS_LABEL = "All Tags"


class BookmarkPanel(QWidget):
    """Table view for file-line bookmarks."""

    bookmark_selected = pyqtSignal(str, int)

    def __init__(self, store: BookmarkStore, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.store = store
        self.setObjectName("bookmark-panel")
        self._build_ui()
        self.refresh()

    def refresh(self) -> None:
        """Reload tag choices and table rows from the store."""
        current_tag = self.current_tag()
        self._reload_tags(current_tag)
        self._reload_rows()

    def current_tag(self) -> str:
        """Return the active tag filter, or an empty string for all tags."""
        if self.tag_filter.currentIndex() <= 0:
            return ""
        return self.tag_filter.currentText()

    def set_tag_filter(self, tag: str) -> None:
        """Select a tag filter by text and refresh rows."""
        index = self.tag_filter.findText(tag)
        self.tag_filter.setCurrentIndex(max(index, 0))
        self._reload_rows()

    def bookmarks(self) -> tuple[Bookmark, ...]:
        """Return the bookmark records currently visible in the table."""
        tag = self.current_tag()
        rows = self.store.list_by_tag(tag) if tag else self.store.list()
        return tuple(rows)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        filter_row = QWidget(self)
        filter_layout = QHBoxLayout(filter_row)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(6)
        label = QLabel("Tag", filter_row)
        self.tag_filter = QComboBox(filter_row)
        self.tag_filter.setObjectName("bookmark-tag-filter")
        self.tag_filter.currentIndexChanged.connect(self._reload_rows)
        filter_layout.addWidget(label)
        filter_layout.addWidget(self.tag_filter, stretch=1)

        self.table = QTableWidget(0, 4, self)
        self.table.setObjectName("bookmark-table")
        self.table.setHorizontalHeaderLabels(["File", "Line", "Tag", "Note"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self._activate_item)
        header = self.table.horizontalHeader()
        assert header is not None
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(filter_row)
        layout.addWidget(self.table, stretch=1)

    def _reload_tags(self, preferred: str) -> None:
        self.tag_filter.blockSignals(True)
        self.tag_filter.clear()
        self.tag_filter.addItem(ALL_TAGS_LABEL)
        for tag in self.store.tags():
            self.tag_filter.addItem(tag)
        index = self.tag_filter.findText(preferred)
        self.tag_filter.setCurrentIndex(max(index, 0))
        self.tag_filter.blockSignals(False)

    def _reload_rows(self) -> None:
        rows = self.bookmarks()
        self.table.setRowCount(len(rows))
        for row_index, bookmark in enumerate(rows):
            self._set_row(row_index, bookmark)
        if rows:
            self.table.selectRow(0)

    def _set_row(self, row_index: int, bookmark: Bookmark) -> None:
        values = [bookmark.file, str(bookmark.line), bookmark.tag, bookmark.note]
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            item.setData(ROLE_FILE, bookmark.file)
            item.setData(ROLE_LINE, bookmark.line)
            self.table.setItem(row_index, column, item)

    def _activate_item(self, item: QTableWidgetItem) -> None:
        file = item.data(ROLE_FILE)
        line = item.data(ROLE_LINE)
        if file is None or line is None:
            return
        self.bookmark_selected.emit(str(file), int(line))
