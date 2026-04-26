"""UI coverage for the D61-D69 Relation Window."""

from __future__ import annotations

from pathlib import Path

import pytest

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.core.types import EdgeType, NodeType, SourceLocation
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.indexer.relation_query import RelationQuery
from sourcetrail_remake.ui.panels.relation_window import (
    EMPTY_TEXT,
    PLACEHOLDER_TEXT,
    RECURSIVE_TEXT,
    RelationAxis,
    RelationWindow,
)


@pytest.mark.ui
def test_relation_window_populates_four_tabs_and_lazy_loads(qtbot, tmp_path: Path) -> None:
    db_path, ids = _build_relation_db(tmp_path, chain=True)
    event_bus = EventBus()
    window = RelationWindow(event_bus, RelationQuery(db_path))
    qtbot.addWidget(window)

    event_bus.symbol_selected.emit(int(ids["target"]))

    assert window.tabs.count() == 4
    called_by_tree = window._trees[RelationAxis.CALLED_BY]
    first = called_by_tree.topLevelItem(0)
    assert first.text(0) == "middle"
    assert first.child(0).text(0) == PLACEHOLDER_TEXT

    called_by_tree.expandItem(first)
    assert first.child(0).text(0) == "caller"


@pytest.mark.ui
def test_relation_window_depth_limit_and_recursive_label(qtbot, tmp_path: Path) -> None:
    db_path, ids = _build_relation_db(tmp_path, recursive=True)
    event_bus = EventBus()
    window = RelationWindow(event_bus, RelationQuery(db_path))
    qtbot.addWidget(window)
    window.depth_slider.setValue(1)

    event_bus.symbol_selected.emit(int(ids["caller"]))
    calls_tree = window._trees[RelationAxis.CALLS]
    first = calls_tree.topLevelItem(0)
    calls_tree.expandItem(first)

    assert first.child(0).text(0) == RECURSIVE_TEXT


@pytest.mark.ui
def test_relation_window_double_click_emits_symbol_selected(qtbot, tmp_path: Path) -> None:
    db_path, ids = _build_relation_db(tmp_path)
    event_bus = EventBus()
    window = RelationWindow(event_bus, RelationQuery(db_path))
    qtbot.addWidget(window)
    event_bus.symbol_selected.emit(int(ids["caller"]))
    calls_tree = window._trees[RelationAxis.CALLS]
    item = calls_tree.topLevelItem(0)

    with qtbot.waitSignal(event_bus.symbol_selected) as signal:
        window._activate_item(item, 0)

    assert signal.args == [int(ids["target"])]


@pytest.mark.ui
def test_relation_window_shows_empty_state(qtbot, tmp_path: Path) -> None:
    db_path, ids = _build_relation_db(tmp_path)
    event_bus = EventBus()
    window = RelationWindow(event_bus, RelationQuery(db_path))
    qtbot.addWidget(window)

    event_bus.symbol_selected.emit(int(ids["isolated"]))

    assert window._trees[RelationAxis.CALLS].topLevelItem(0).text(0) == EMPTY_TEXT


def _build_relation_db(tmp_path: Path, *, chain: bool = False, recursive: bool = False):
    source_path = tmp_path / "sample.py"
    source_path.write_text(
        "def caller():\n    middle()\n\ndef middle():\n    target()\n",
        encoding="utf-8",
    )
    db_path = tmp_path / "sample.srctrldb"
    with DatabaseWriter(db_path) as writer:
        writer.initialize_schema()
        file_id = writer.record_file(source_path, source_path.read_text(encoding="utf-8"))
        caller = writer.record_symbol(
            "caller",
            NodeType.NODE_FUNCTION,
            file_id,
            SourceLocation.from_name(line=1, column=4, name="caller"),
            qualified_name="sample.caller",
        )
        middle = writer.record_symbol(
            "middle",
            NodeType.NODE_FUNCTION,
            file_id,
            SourceLocation.from_name(line=3, column=4, name="middle"),
            qualified_name="sample.middle",
        )
        target = writer.record_symbol(
            "target",
            NodeType.NODE_FUNCTION,
            file_id,
            SourceLocation.from_name(line=5, column=4, name="target"),
            qualified_name="sample.target",
        )
        isolated = writer.record_symbol(
            "isolated",
            NodeType.NODE_FUNCTION,
            file_id,
            SourceLocation.from_name(line=6, column=4, name="isolated"),
            qualified_name="sample.isolated",
        )
        if chain:
            writer.record_edge(caller, middle, EdgeType.EDGE_CALL)
            writer.record_edge(middle, target, EdgeType.EDGE_CALL)
        else:
            writer.record_edge(caller, target, EdgeType.EDGE_CALL)
        if recursive:
            writer.record_edge(target, caller, EdgeType.EDGE_CALL)
    return db_path, {
        "caller": caller,
        "middle": middle,
        "target": target,
        "isolated": isolated,
    }
