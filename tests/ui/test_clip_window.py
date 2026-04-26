"""UI coverage for Week 21 clip window drag/drop helpers."""

from __future__ import annotations

import pytest
from PyQt6.QtWidgets import QListWidget, QTextEdit

from sourcetrail_remake.core.clips import ClipStore
from sourcetrail_remake.ui.panels.clip_window import ClipWindow


@pytest.mark.ui
def test_clip_window_adds_and_previews_clip(qtbot, tmp_path) -> None:
    window = ClipWindow(ClipStore(tmp_path / ".srm-clips"))
    qtbot.addWidget(window)

    clip_id = window.add_clip("Example", "value = 1", tags=("REVIEW",))

    list_widget = window.findChild(QListWidget, "clip-list")
    preview = window.findChild(QTextEdit, "clip-preview")
    assert list_widget is not None
    assert preview is not None
    assert list_widget.count() == 1
    assert window.store.get(clip_id) is not None
    assert preview.toPlainText() == "value = 1"


@pytest.mark.ui
def test_clip_window_accepts_custom_mime_payload(qtbot, tmp_path) -> None:
    window = ClipWindow(ClipStore(tmp_path / ".srm-clips"))
    qtbot.addWidget(window)

    clip_id = window.add_clip_from_mime(
        '{"title": "Dragged", "text": "print(1)", "tags": ["TODO"], "note": "from editor"}'
    )
    clip = window.store.get(clip_id)

    assert clip is not None
    assert clip.title == "Dragged"
    assert clip.text == "print(1)"
    assert clip.tags == ("TODO",)
