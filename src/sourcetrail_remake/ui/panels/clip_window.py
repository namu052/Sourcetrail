"""Clip window for drag-and-drop snippet capture."""

from __future__ import annotations

import json

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from sourcetrail_remake.core.clips import Clip, ClipId, ClipStore

CLIP_MIME_TYPE = "application/x-srm-clip"
ROLE_CLIP_ID = int(Qt.ItemDataRole.UserRole)


class ClipWindow(QWidget):
    """Panel that stores and previews reusable code clips."""

    clip_selected = pyqtSignal(str)
    clip_added = pyqtSignal(str)

    def __init__(self, store: ClipStore, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.store = store
        self.setObjectName("clip-window")
        self.setAcceptDrops(True)
        self._build_ui()
        self.refresh()

    def refresh(self) -> None:
        """Reload the clip list from storage."""
        self.list_widget.clear()
        for clip in self.store.list():
            item = QListWidgetItem(clip.title)
            item.setData(ROLE_CLIP_ID, str(clip.id))
            item.setToolTip(clip.note)
            self.list_widget.addItem(item)
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
            self._show_current_clip()

    def add_clip(
        self,
        title: str,
        text: str,
        *,
        tags: tuple[str, ...] = (),
        note: str = "",
    ) -> ClipId:
        """Add a clip through the window and refresh the list."""
        clip_id = self.store.add(title, text, tags=tags, note=note)
        self.refresh()
        self.clip_added.emit(str(clip_id))
        return clip_id

    def add_clip_from_mime(self, mime_text: str) -> ClipId:
        """Create a clip from serialized custom MIME or plain text."""
        try:
            payload = json.loads(mime_text)
        except json.JSONDecodeError:
            payload = {"title": "", "text": mime_text, "tags": [], "note": ""}
        return self.add_clip(
            str(payload.get("title", "")),
            str(payload.get("text", "")),
            tags=tuple(str(tag) for tag in payload.get("tags", [])),
            note=str(payload.get("note", "")),
        )

    def clip_to_mime(self, clip: Clip) -> str:
        """Serialize a clip for ``application/x-srm-clip`` drag data."""
        return json.dumps(
            {
                "id": str(clip.id),
                "title": clip.title,
                "text": clip.text,
                "tags": list(clip.tags),
                "note": clip.note,
            }
        )

    def export_to_json(self, path: str) -> None:
        """Export all clips to ``path`` and keep the panel state unchanged."""
        self.store.export_json(path)

    def import_from_json(self, path: str, *, replace: bool = False) -> int:
        """Import clips from ``path`` and refresh the panel."""
        count = self.store.import_json(path, replace=replace)
        self.refresh()
        return count

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        mime = event.mimeData()
        if mime.hasFormat(CLIP_MIME_TYPE) or mime.hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        mime = event.mimeData()
        if mime.hasFormat(CLIP_MIME_TYPE):
            text = bytes(mime.data(CLIP_MIME_TYPE)).decode("utf-8")
        elif mime.hasText():
            text = mime.text()
        else:
            return
        self.add_clip_from_mime(text)
        event.acceptProposedAction()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.list_widget = QListWidget(self)
        self.list_widget.setObjectName("clip-list")
        self.list_widget.setDragEnabled(True)
        self.list_widget.currentItemChanged.connect(self._show_current_clip)
        self.preview = QTextEdit(self)
        self.preview.setObjectName("clip-preview")
        self.preview.setReadOnly(True)
        self.add_selection_button = QPushButton("Add Selection", self)
        self.add_selection_button.setObjectName("clip-add-selection-button")

        layout.addWidget(self.list_widget, stretch=1)
        layout.addWidget(self.preview, stretch=2)
        layout.addWidget(self.add_selection_button)

    def _show_current_clip(self) -> None:
        item = self.list_widget.currentItem()
        if item is None:
            self.preview.clear()
            return
        clip_id = ClipId(str(item.data(ROLE_CLIP_ID)))
        clip = self.store.get(clip_id)
        if clip is None:
            self.preview.clear()
            return
        self.preview.setPlainText(clip.text)
        self.clip_selected.emit(str(clip.id))
