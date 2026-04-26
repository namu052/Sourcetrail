"""UI tests for the Smart Rename dialog."""

from __future__ import annotations

from pathlib import Path

import pytest
from PyQt6.QtWidgets import QListWidget, QPlainTextEdit
from rope.base.change import ChangeSet

from sourcetrail_remake.core.types import NodeId
from sourcetrail_remake.refactor.rename import FileChange, RenamePreview
from sourcetrail_remake.ui.dialogs.rename import RenameDialog


@pytest.mark.ui
def test_rename_dialog_shows_affected_files_and_diff(qtbot, tmp_path: Path) -> None:
    changed_file = tmp_path / "module.py"
    preview = RenamePreview(
        node_id=NodeId(1),
        old_name="value",
        new_name="total",
        affected_files=(changed_file,),
        changes=(
            FileChange(
                path=changed_file,
                old_text="value = 1\n",
                new_text="total = 1\n",
                diff="--- a/module.py\n+++ b/module.py\n-value = 1\n+total = 1\n",
            ),
        ),
        conflicts=(),
        rope_changes=ChangeSet("rename value"),
    )

    dialog = RenameDialog(preview)
    qtbot.addWidget(dialog)

    files = dialog.findChild(QListWidget, "rename-files-list")
    diff = dialog.findChild(QPlainTextEdit, "rename-diff-view")

    assert files is not None
    assert diff is not None
    assert files.count() == 1
    assert "total = 1" in diff.toPlainText()
