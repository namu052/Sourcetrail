"""References lookup dialog with grouped results and source preview."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QPlainTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from sourcetrail_remake.indexer.relation_query import Occurrence

ROLE_OCCURRENCE = int(Qt.ItemDataRole.UserRole)
PREVIEW_RADIUS = 2


class ReferencesDialog(QDialog):
    """Show Lookup References results grouped by file."""

    def __init__(
        self,
        occurrences: list[Occurrence],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.occurrences = occurrences
        self.setWindowTitle("References")
        self.setObjectName("references-dialog")
        self.resize(860, 520)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.tree = QTreeWidget(self)
        self.tree.setObjectName("references-results-tree")
        self.tree.setHeaderLabels(["Reference", "Location"])
        self.tree.currentItemChanged.connect(self._show_preview)

        self.preview = QPlainTextEdit(self)
        self.preview.setObjectName("references-preview")
        self.preview.setReadOnly(True)
        self.preview.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        layout.addWidget(self.tree, 2)
        layout.addWidget(self.preview, 3)
        self._populate()

    def _populate(self) -> None:
        grouped: dict[str, list[Occurrence]] = defaultdict(list)
        for occurrence in self.occurrences:
            key = "<unknown>" if occurrence.file_path is None else str(occurrence.file_path)
            grouped[key].append(occurrence)

        for file_label in sorted(grouped):
            occurrences = grouped[file_label]
            parent = QTreeWidgetItem([Path(file_label).name, f"{len(occurrences)} references"])
            parent.setExpanded(True)
            self.tree.addTopLevelItem(parent)
            for occurrence in occurrences:
                item = QTreeWidgetItem(
                    [
                        occurrence.label,
                        f"{occurrence.start_line}:{occurrence.start_column}",
                    ]
                )
                item.setData(0, ROLE_OCCURRENCE, occurrence)
                parent.addChild(item)

        first_item = self._first_occurrence_item()
        if first_item is not None:
            self.tree.setCurrentItem(first_item)

    def _show_preview(
        self,
        current: QTreeWidgetItem | None,
        _previous: QTreeWidgetItem | None,
    ) -> None:
        if current is None:
            self.preview.clear()
            return
        value = current.data(0, ROLE_OCCURRENCE)
        if not isinstance(value, Occurrence):
            self.preview.clear()
            return
        self.preview.setPlainText(self._preview_text(value))

    def _preview_text(self, occurrence: Occurrence) -> str:
        if occurrence.file_path is None or not occurrence.file_path.exists():
            return ""
        lines = occurrence.file_path.read_text(encoding="utf-8").splitlines()
        start = max(occurrence.start_line - PREVIEW_RADIUS - 1, 0)
        end = min(occurrence.start_line + PREVIEW_RADIUS, len(lines))
        return "\n".join(
            f"{line_number:>4}: {lines[line_number - 1]}"
            for line_number in range(start + 1, end + 1)
        )

    def _first_occurrence_item(self) -> QTreeWidgetItem | None:
        for top_index in range(self.tree.topLevelItemCount()):
            parent = self.tree.topLevelItem(top_index)
            if parent is not None and parent.childCount() > 0:
                return parent.child(0)
        return None
