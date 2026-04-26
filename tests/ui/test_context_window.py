"""Unit coverage for the Phase 2 Context Window."""

from __future__ import annotations

from pathlib import Path

import pytest
from PyQt6.QtCore import Qt

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.core.types import EdgeType, NodeType, SourceLocation
from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.ui.panels.context_window import ContextWindow


@pytest.mark.ui
def test_context_window_loads_declaration_for_cursor(qtbot, tmp_path: Path) -> None:
    source_path, reader = _build_context_reader(tmp_path)
    event_bus = EventBus()
    window = ContextWindow(event_bus, reader)
    qtbot.addWidget(window)

    event_bus.cursor_moved.emit(str(source_path), 2, 12)
    window.refresh_now()

    assert window.open_button.isEnabled()
    assert window.current_file == str(source_path)
    assert window.current_line == 2
    assert window.breadcrumb_label.text() == "bar"
    assert "def bar" in window.preview.text()
    assert window.preview.hasSelectedText()


@pytest.mark.ui
def test_context_window_open_button_emits_file_opened(qtbot, tmp_path: Path) -> None:
    source_path, reader = _build_context_reader(tmp_path)
    event_bus = EventBus()
    window = ContextWindow(event_bus, reader)
    qtbot.addWidget(window)

    event_bus.cursor_moved.emit(str(source_path), 2, 12)
    window.refresh_now()

    with qtbot.waitSignal(event_bus.file_opened) as signal:
        qtbot.mouseClick(window.open_button, Qt.MouseButton.LeftButton)

    assert signal.args == [str(source_path), 2]


@pytest.mark.ui
def test_context_window_keeps_recent_five_breadcrumbs(qtbot, tmp_path: Path) -> None:
    _source_path, reader = _build_context_reader(tmp_path)
    window = ContextWindow(EventBus(), reader)
    qtbot.addWidget(window)

    for index in range(7):
        window._push_recent_context(f"symbol_{index}")

    assert window.breadcrumb_label.text() == ""
    assert window._recent_contexts == ["symbol_2", "symbol_3", "symbol_4", "symbol_5", "symbol_6"]


def _build_context_reader(tmp_path: Path) -> tuple[Path, DatabaseReader]:
    source_path = tmp_path / "sample.py"
    source = "class Foo:\n    def bar(self) -> None:\n        pass\n"
    source_path.write_text(source, encoding="utf-8")
    db_path = tmp_path / "sample.srctrldb"

    with DatabaseWriter(db_path) as writer:
        writer.initialize_schema()
        file_id = writer.record_file(source_path, source)
        class_id = writer.record_symbol(
            "Foo",
            NodeType.NODE_CLASS,
            file_id,
            SourceLocation.from_name(line=1, column=6, name="Foo"),
            qualified_name="sample.Foo",
        )
        method_id = writer.record_symbol(
            "bar",
            NodeType.NODE_METHOD,
            file_id,
            SourceLocation.from_name(line=2, column=8, name="bar"),
            qualified_name="sample.Foo.bar",
        )
        writer.record_edge(class_id, method_id, EdgeType.EDGE_MEMBER)

    return source_path.resolve(), DatabaseReader(db_path)
