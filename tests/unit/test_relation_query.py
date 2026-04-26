"""Unit coverage for RelationQuery directional DB reads."""

from __future__ import annotations

from pathlib import Path

import pytest

from sourcetrail_remake.core.types import EdgeType, NodeType, SourceLocation
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.indexer.relation_query import RelationQuery


@pytest.mark.unit
def test_relation_query_reads_callers_callees_references_and_overrides(tmp_path: Path) -> None:
    db_path, ids = _build_relation_db(tmp_path)
    query = RelationQuery(db_path)

    callers = query.get_callers(ids["target"], depth=2)
    callees = query.get_callees(ids["caller"], depth=2)
    references = query.get_references(ids["target"])
    overrides = query.get_overrides(ids["base"])

    assert [relation.display_name for relation in callers] == ["caller"]
    assert [relation.display_name for relation in callees] == ["target"]
    assert references[0].label == "target"
    assert overrides == [ids["child"]]


@pytest.mark.unit
def test_relation_query_marks_recursive_call_chain(tmp_path: Path) -> None:
    db_path, ids = _build_relation_db(tmp_path, recursive=True)
    query = RelationQuery(db_path)

    callees = query.get_callees(ids["caller"], depth=3)

    assert any(relation.is_recursive for relation in callees)


def _build_relation_db(tmp_path: Path, *, recursive: bool = False):
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
        base = writer.record_symbol(
            "Base.run",
            NodeType.NODE_METHOD,
            file_id,
            SourceLocation.from_name(line=1, column=4, name="run"),
            qualified_name="sample.Base.run",
        )
        child = writer.record_symbol(
            "Child.run",
            NodeType.NODE_METHOD,
            file_id,
            SourceLocation.from_name(line=4, column=4, name="run"),
            qualified_name="sample.Child.run",
        )
        writer.record_edge(caller, target, EdgeType.EDGE_CALL)
        writer.record_edge(base, child, EdgeType.EDGE_OVERRIDE)
        if recursive:
            writer.record_edge(target, caller, EdgeType.EDGE_CALL)
    return db_path, {"caller": caller, "target": target, "base": base, "child": child}
