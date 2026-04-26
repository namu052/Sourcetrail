"""Unit tests for the Symbol Window file index."""

from __future__ import annotations

from pathlib import Path

import pytest

from sourcetrail_remake.core.types import AccessKind
from sourcetrail_remake.indexer.symbol_index import SymbolIconKind, SymbolIndex, SymbolSortMode


@pytest.mark.unit
def test_symbol_index_builds_class_method_field_tree(tmp_path: Path) -> None:
    source = tmp_path / "sample.py"
    source.write_text(
        "\n".join(
            [
                "GLOBAL = 1",
                "",
                "class Session:",
                "    token = 'x'",
                "",
                "    def __private(self) -> None:",
                "        pass",
                "",
                "    @property",
                "    def name(self) -> str:",
                "        return 'demo'",
                "",
                "def make_session() -> Session:",
                "    return Session()",
                "",
            ]
        ),
        encoding="utf-8",
    )

    symbols = SymbolIndex().load_file(source)

    assert [item.name for item in symbols] == ["GLOBAL", "Session", "make_session"]
    session = symbols[1]
    assert [child.name for child in session.children] == ["token", "__private", "name"]
    assert session.children[0].icon_kind == SymbolIconKind.FIELD
    assert session.children[1].access == AccessKind.ACCESS_PRIVATE
    assert session.children[2].icon_kind == SymbolIconKind.PROPERTY


@pytest.mark.unit
def test_symbol_index_supports_alphabetical_sort_and_refresh(tmp_path: Path) -> None:
    source = tmp_path / "sample.py"
    source.write_text("def beta():\n    pass\n\ndef alpha():\n    pass\n", encoding="utf-8")
    index = SymbolIndex()

    assert [item.name for item in index.load_file(source)] == ["beta", "alpha"]
    alphabetical = index.load_file(source, sort_mode=SymbolSortMode.ALPHABETICAL)
    assert [item.name for item in alphabetical] == [
        "alpha",
        "beta",
    ]

    source.write_text("def gamma():\n    pass\n", encoding="utf-8")
    refreshed = index.refresh_file(source)

    assert [item.name for item in refreshed] == ["gamma"]
