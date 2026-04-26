"""UI coverage for Week 21 bookmark panel filtering."""

from __future__ import annotations

import pytest
from PyQt6.QtWidgets import QComboBox, QTableWidget

from sourcetrail_remake.core.bookmarks import BookmarkStore
from sourcetrail_remake.ui.panels.bookmarks import BookmarkPanel


@pytest.mark.ui
def test_bookmark_panel_lists_and_filters_by_tag(qtbot, tmp_path) -> None:
    store = BookmarkStore(tmp_path / "bookmarks.sqlite")
    store.add("src/app.py", 5, "TODO", "first")
    store.add("src/worker.py", 12, "REVIEW", "second")

    panel = BookmarkPanel(store)
    qtbot.addWidget(panel)

    table = panel.findChild(QTableWidget, "bookmark-table")
    filter_box = panel.findChild(QComboBox, "bookmark-tag-filter")
    assert table is not None
    assert filter_box is not None
    assert table.rowCount() == 2

    panel.set_tag_filter("REVIEW")

    assert panel.current_tag() == "REVIEW"
    assert table.rowCount() == 1
    assert table.item(0, 0).text() == "src/worker.py"


@pytest.mark.ui
def test_bookmark_panel_emits_file_line_on_activation(qtbot, tmp_path) -> None:
    store = BookmarkStore(tmp_path / "bookmarks.sqlite")
    store.add("src/app.py", 5, "TODO", "first")
    panel = BookmarkPanel(store)
    qtbot.addWidget(panel)

    selected: list[tuple[str, int]] = []
    panel.bookmark_selected.connect(lambda file, line: selected.append((file, line)))
    table = panel.findChild(QTableWidget, "bookmark-table")
    assert table is not None

    panel._activate_item(table.item(0, 0))  # noqa: SLF001 - direct signal path coverage.

    assert selected == [("src/app.py", 5)]
