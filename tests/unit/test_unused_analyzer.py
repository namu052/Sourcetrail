"""Unit coverage for unused variable diagnostics."""

from __future__ import annotations

import pytest

from sourcetrail_remake.indexer.unused import UnusedVariableAnalyzer
from sourcetrail_remake.ui.editor.decorator import DecorationKind


@pytest.mark.unit
def test_unused_variable_analyzer_reports_unread_assignment() -> None:
    diagnostics = UnusedVariableAnalyzer().analyze_text(
        "def run(value):\n"
        "    used = value\n"
        "    stale = 1\n"
        "    return used\n"
    )

    assert [(item.name, item.range.start_line) for item in diagnostics] == [("stale", 3)]


@pytest.mark.unit
def test_unused_variable_analyzer_skips_underscore_names() -> None:
    diagnostics = UnusedVariableAnalyzer().analyze_text(
        "def run(value):\n"
        "    _ignored = value\n"
        "    return value\n"
    )

    assert diagnostics == []


@pytest.mark.unit
def test_unused_variable_analyzer_exports_decorations() -> None:
    decorations = UnusedVariableAnalyzer().decorations_for_text("orphan = 1\n")

    assert decorations[0].kind == DecorationKind.UNUSED_VARIABLE
    assert decorations[0].message == "Unused variable: orphan"
