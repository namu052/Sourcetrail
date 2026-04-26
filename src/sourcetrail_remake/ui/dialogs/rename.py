"""Smart Rename preview dialog."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from sourcetrail_remake.refactor.rename import FileChange, RenamePreview, ScopeConflict

ROLE_PATH = int(Qt.ItemDataRole.UserRole)


class RenameDialog(QDialog):
    """Preview and confirmation dialog for RopeRenameService changes."""

    def __init__(self, preview: RenamePreview, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.preview = preview
        self.setWindowTitle(f"Rename {preview.old_name} to {preview.new_name}")
        self.setObjectName("rename-dialog")
        self.resize(880, 540)
        self._build_ui()

    def selected_file(self) -> Path | None:
        item = self.files.currentItem()
        if item is None:
            return None
        value = item.data(ROLE_PATH)
        return value if isinstance(value, Path) else None

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        root.addWidget(QLabel(self._summary_text()))
        conflict_text = self._conflict_text(self.preview.conflicts)
        if conflict_text:
            warning = QLabel(conflict_text)
            warning.setObjectName("rename-conflict-warning")
            warning.setWordWrap(True)
            root.addWidget(warning)

        content = QHBoxLayout()
        self.files = QListWidget(self)
        self.files.setObjectName("rename-files-list")
        self.files.currentItemChanged.connect(self._show_selected_diff)
        self.diff = QPlainTextEdit(self)
        self.diff.setObjectName("rename-diff-view")
        self.diff.setReadOnly(True)
        self.diff.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        for change in self.preview.changes:
            item = QListWidgetItem(self._file_label(change))
            item.setData(ROLE_PATH, change.path)
            self.files.addItem(item)

        content.addWidget(self.files, 1)
        content.addWidget(self.diff, 3)
        root.addLayout(content, 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Apply | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

        if self.files.count() > 0:
            self.files.setCurrentRow(0)

    def _show_selected_diff(self) -> None:
        path = self.selected_file()
        if path is None:
            self.diff.clear()
            return
        change = next((item for item in self.preview.changes if item.path == path), None)
        self.diff.setPlainText("" if change is None else change.diff)

    def _summary_text(self) -> str:
        return (
            f"{len(self.preview.affected_files)} files will change: "
            f"{self.preview.old_name} -> {self.preview.new_name}"
        )

    def _conflict_text(self, conflicts: tuple[ScopeConflict, ...]) -> str:
        if not conflicts:
            return ""
        return "\n".join(
            f"{conflict.path.name}:{conflict.line}:{conflict.column} {conflict.message}"
            for conflict in conflicts
        )

    def _file_label(self, change: FileChange) -> str:
        try:
            return change.path.relative_to(Path.cwd()).as_posix()
        except ValueError:
            return change.path.name
