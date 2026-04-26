"""Unit coverage for undefined reference diagnostics."""

from __future__ import annotations

import pytest

from sourcetrail_remake.indexer.undefined import UndefinedReferenceAnalyzer
from sourcetrail_remake.ui.editor.decorator import DecorationKind


@pytest.mark.unit
def test_undefined_reference_analyzer_reports_unbound_load() -> None:
    diagnostics = UndefinedReferenceAnalyzer().analyze_text(
        "def run(value):\n    return value + missing_name\n"
    )

    assert [(item.name, item.range.start_line) for item in diagnostics] == [("missing_name", 2)]


@pytest.mark.unit
def test_undefined_reference_analyzer_skips_imports_and_builtins() -> None:
    diagnostics = UndefinedReferenceAnalyzer().analyze_text(
        "import pathlib\ndef run(value):\n    return len(pathlib.Path(str(value)))\n"
    )

    assert diagnostics == []


@pytest.mark.unit
def test_undefined_reference_analyzer_exports_red_squiggle_decorations() -> None:
    decorations = UndefinedReferenceAnalyzer().decorations_for_text("answer = missing\n")

    assert decorations[0].kind == DecorationKind.UNDEFINED_REFERENCE
    assert decorations[0].message == "Undefined reference: missing"
