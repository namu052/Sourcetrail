"""Integration flow for Symbol and Relation panel event synchronization."""

from __future__ import annotations

from pathlib import Path

import pytest

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.core.types import EdgeType, NodeType, SourceLocation
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.indexer.relation_query import RelationQuery
from sourcetrail_remake.indexer.symbol_index import SymbolIndex
from sourcetrail_remake.ui.panels.relation_window import RelationAxis, RelationWindow
from sourcetrail_remake.ui.panels.symbol_window import SymbolWindow


@pytest.mark.integration
def test_symbol_and_relation_panels_share_event_bus(qtbot, tmp_path: Path) -> None:
    source_path, db_path, ids = _build_panel_flow_fixture(tmp_path)
    event_bus = EventBus()
    symbol_window = SymbolWindow(event_bus, SymbolIndex())
    relation_window = RelationWindow(event_bus, RelationQuery(db_path))
    qtbot.addWidget(symbol_window)
    qtbot.addWidget(relation_window)

    event_bus.file_opened.emit(str(source_path), 1)
    event_bus.symbol_selected.emit(int(ids["caller"]))

    assert symbol_window.model.index(0, 0).data() == "caller"
    calls_tree = relation_window._trees[RelationAxis.CALLS]
    assert calls_tree.topLevelItem(0).text(0) == "target"


def _build_panel_flow_fixture(tmp_path: Path):
    source_path = tmp_path / "sample.py"
    source_path.write_text(
        "def caller():\n    target()\n\ndef target():\n    pass\n",
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
        target = writer.record_symbol(
            "target",
            NodeType.NODE_FUNCTION,
            file_id,
            SourceLocation.from_name(line=4, column=4, name="target"),
            qualified_name="sample.target",
        )
        writer.record_edge(caller, target, EdgeType.EDGE_CALL)
    return source_path, db_path, {"caller": caller, "target": target}
