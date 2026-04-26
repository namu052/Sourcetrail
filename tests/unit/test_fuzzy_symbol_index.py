"""Unit coverage for project-wide fuzzy symbol indexing."""

from __future__ import annotations

from pathlib import Path

import pytest

from sourcetrail_remake.core.types import NodeType, SourceLocation
from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.search.fuzzy import SymbolFuzzyIndex


@pytest.mark.unit
def test_symbol_fuzzy_index_builds_flat_symbol_catalog(tmp_path: Path) -> None:
    db_path, ids = _build_symbol_db(tmp_path)
    index = SymbolFuzzyIndex()

    index.build(DatabaseReader(db_path))

    symbols = index.symbols()
    assert [(symbol.fqn, symbol.name, symbol.node_id) for symbol in symbols] == [
        ("sample.SessionManager", "SessionManager", ids["class"]),
        ("sample.build_session", "build_session", ids["function"]),
    ]


@pytest.mark.unit
def test_symbol_fuzzy_index_ranks_exact_prefix_then_fuzzy(tmp_path: Path) -> None:
    db_path, _ids = _build_symbol_db(tmp_path)
    index = SymbolFuzzyIndex()
    index.build(DatabaseReader(db_path))

    exact = index.search("SessionManager")
    prefix = index.search("build")
    fuzzy = index.search("sessm")

    assert exact[0].symbol.fqn == "sample.SessionManager"
    assert exact[0].match_kind == "exact"
    assert prefix[0].symbol.fqn == "sample.build_session"
    assert prefix[0].match_kind == "prefix"
    assert fuzzy[0].symbol.fqn == "sample.SessionManager"
    assert fuzzy[0].match_kind == "fuzzy"


def _build_symbol_db(tmp_path: Path):
    source_path = tmp_path / "sample.py"
    source_path.write_text(
        "class SessionManager:\n    pass\n\ndef build_session():\n    pass\n",
        encoding="utf-8",
    )
    db_path = tmp_path / "sample.srctrldb"
    with DatabaseWriter(db_path) as writer:
        writer.initialize_schema()
        file_id = writer.record_file(source_path, source_path.read_text(encoding="utf-8"))
        class_id = writer.record_symbol(
            "SessionManager",
            NodeType.NODE_CLASS,
            file_id,
            SourceLocation.from_name(line=1, column=6, name="SessionManager"),
            qualified_name="sample.SessionManager",
        )
        function_id = writer.record_symbol(
            "build_session",
            NodeType.NODE_FUNCTION,
            file_id,
            SourceLocation.from_name(line=4, column=4, name="build_session"),
            qualified_name="sample.build_session",
        )
    return db_path, {"class": class_id, "function": function_id}
