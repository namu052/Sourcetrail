"""Unit tests for the Parso-based symbol walker."""

from __future__ import annotations

from pathlib import Path

import pytest

from sourcetrail_remake.core.types import NodeType
from sourcetrail_remake.indexer.parso_walker import ParsoWalker


@pytest.mark.unit
def test_parso_walker_extracts_nested_symbols() -> None:
    project_root = Path("tests/fixtures/sample-minimal")
    walker = ParsoWalker(project_root)

    module = walker.parse_module(project_root / "session_manager.py")
    symbol_map = {symbol.qualified_name: symbol.node_type for symbol in module.symbols}

    assert symbol_map["session_manager.Session"] == NodeType.NODE_CLASS
    assert symbol_map["session_manager.Session.touch"] == NodeType.NODE_METHOD
    assert symbol_map["session_manager.Session.is_expired"] == NodeType.NODE_METHOD
    assert symbol_map["session_manager.Session.user_id"] == NodeType.NODE_FIELD
    assert symbol_map["session_manager.SessionManager"] == NodeType.NODE_CLASS
    assert symbol_map["session_manager.SessionManager.create_session"] == NodeType.NODE_METHOD
    assert symbol_map["session_manager.count_active_sessions"] == NodeType.NODE_FUNCTION
