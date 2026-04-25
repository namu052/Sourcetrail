"""Unit tests for the Jedi wrapper."""

from __future__ import annotations

from pathlib import Path

import pytest

from sourcetrail_remake.core.types import NodeType
from sourcetrail_remake.indexer.jedi_resolver import JediResolver
from sourcetrail_remake.indexer.mappings import classify_edge_type, map_name_type
from sourcetrail_remake.indexer.parso_walker import ParsoWalker


@pytest.mark.unit
def test_map_name_type_promotes_methods_and_builtins() -> None:
    project_root = Path("tests/fixtures/sample-minimal")
    parent = next(
        symbol
        for symbol in ParsoWalker(project_root).parse_module(project_root / "session_manager.py").symbols
        if symbol.qualified_name == "session_manager.Session"
    )

    assert map_name_type("function", parent=parent) == NodeType.NODE_METHOD
    assert map_name_type("statement", parent=parent) == NodeType.NODE_FIELD
    assert map_name_type("class", is_builtin=True) == NodeType.NODE_BUILTIN_TYPE


@pytest.mark.unit
def test_classify_edge_type_handles_imports_calls_and_member_access() -> None:
    assert classify_edge_type("from flask import Flask", column=18, name="Flask").name == "EDGE_IMPORT"
    assert classify_edge_type("response = requests.get(url)", column=20, name="get").name == "EDGE_CALL"
    assert classify_edge_type("manager.sessions", column=8, name="sessions").name == "EDGE_MEMBER"
    assert classify_edge_type("return session", column=7, name="session").name == "EDGE_USAGE"


@pytest.mark.unit
def test_jedi_resolver_collects_references_and_definitions() -> None:
    project_root = Path("tests/fixtures/sample-minimal")
    path = project_root / "session_manager.py"
    source = path.read_text(encoding="utf-8")
    resolver = JediResolver(project_root)

    definitions = resolver.collect_names(source, path, definitions=True, references=False)
    references = resolver.get_references(source, path, line=24, column=6, include_builtins=False)

    assert any(item.qualified_name == "session_manager.SessionManager" for item in definitions)
    assert any(item.name == "SessionManager" and not item.is_definition for item in references)
