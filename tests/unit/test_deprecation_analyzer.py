"""Unit coverage for deprecation diagnostics."""

from __future__ import annotations

import pytest

from sourcetrail_remake.indexer.deprecation import DeprecationAnalyzer
from sourcetrail_remake.ui.editor.decorator import DecorationKind


@pytest.mark.unit
def test_deprecation_analyzer_finds_decorator_and_call_site() -> None:
    findings = DeprecationAnalyzer().analyze_text(
        "from deprecated import deprecated\n"
        "@deprecated(reason='use new')\n"
        "def old():\n"
        "    pass\n"
        "def caller():\n"
        "    old()\n"
    )

    assert [(finding.name, finding.reason) for finding in findings] == [
        ("old", "decorated as deprecated"),
        ("old", "calls deprecated symbol"),
    ]


@pytest.mark.unit
def test_deprecation_analyzer_finds_warning_pattern() -> None:
    findings = DeprecationAnalyzer().analyze_text(
        "import warnings\ndef old():\n    warnings.warn('old', DeprecationWarning)\n"
    )

    assert findings[0].name == "DeprecationWarning"
    assert findings[0].reason == "emits DeprecationWarning"


@pytest.mark.unit
def test_deprecation_analyzer_exports_decorations() -> None:
    decorations = DeprecationAnalyzer().decorations_for_text("@deprecated\ndef old():\n    pass\n")

    assert decorations[0].kind == DecorationKind.DEPRECATED
    assert decorations[0].message == "Deprecated old: decorated as deprecated"
