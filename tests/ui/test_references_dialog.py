"""UI coverage for Lookup References dialog."""

from __future__ import annotations

from pathlib import Path

import pytest
from PyQt6.QtWidgets import QPlainTextEdit, QTreeWidget

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.indexer.relation_query import Occurrence
from sourcetrail_remake.ui.dialogs.references import ReferencesDialog
from sourcetrail_remake.ui.main_window import MainWindow


@pytest.mark.ui
def test_references_dialog_groups_results_and_shows_preview(qtbot, tmp_path: Path) -> None:
    source_path = tmp_path / "sample.py"
    source_path.write_text(
        "def caller():\n    target()\n\ndef target():\n    pass\n",
        encoding="utf-8",
    )
    dialog = ReferencesDialog(
        [
            Occurrence(
                element_id=1,
                file_path=source_path,
                start_line=2,
                start_column=4,
                end_line=2,
                end_column=10,
                label="target",
            )
        ]
    )
    qtbot.addWidget(dialog)

    tree = dialog.findChild(QTreeWidget, "references-results-tree")
    preview = dialog.findChild(QPlainTextEdit, "references-preview")

    assert tree is not None
    assert preview is not None
    assert tree.topLevelItemCount() == 1
    assert tree.topLevelItem(0).text(0) == "sample.py"
    assert tree.topLevelItem(0).child(0).text(1) == "2:4"
    assert "target()" in preview.toPlainText()


@pytest.mark.ui
def test_main_window_registers_shift_f12_references_shortcut(qtbot) -> None:
    window = MainWindow(EventBus())
    qtbot.addWidget(window)

    assert window.references_shortcut.key().toString() == "Shift+F12"
