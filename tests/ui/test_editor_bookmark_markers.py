"""UI coverage for Week 21 editor bookmark margin markers."""

from __future__ import annotations

import pytest

from sourcetrail_remake.ui.editor.editor import BOOKMARK_MARGIN, QScintillaEditor


@pytest.mark.ui
def test_editor_bookmark_markers_are_added_replaced_and_removed(qtbot) -> None:
    editor = QScintillaEditor()
    qtbot.addWidget(editor)
    editor.load_text("alpha\nbeta\ngamma\n")

    assert editor.marginWidth(BOOKMARK_MARGIN) > 0

    editor.add_bookmark_marker(2)
    assert editor.bookmark_marker_lines() == (2,)

    editor.set_bookmark_markers((1, 3))
    assert editor.bookmark_marker_lines() == (1, 3)

    editor.remove_bookmark_marker(1)
    assert editor.bookmark_marker_lines() == (3,)

    editor.clear_bookmark_markers()
    assert editor.bookmark_marker_lines() == ()


@pytest.mark.ui
def test_editor_bookmark_marker_rejects_zero_line(qtbot) -> None:
    editor = QScintillaEditor()
    qtbot.addWidget(editor)

    with pytest.raises(ValueError, match="one-based"):
        editor.add_bookmark_marker(0)
