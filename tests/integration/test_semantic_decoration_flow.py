"""Integration coverage for Week 15 semantic decoration flow."""

from __future__ import annotations

import pytest

from sourcetrail_remake.ui.dialogs.preferences import DecorationPreferences
from sourcetrail_remake.ui.editor.decorator import DecorationKind
from sourcetrail_remake.ui.editor.semantic import SemanticDecorationService


@pytest.mark.integration
def test_semantic_decoration_service_merges_week15_analyzers() -> None:
    service = SemanticDecorationService.create_default()

    decorations = service.analyze_text(
        "from deprecated import deprecated\n"
        "@deprecated\n"
        "def old():\n"
        "    warnings.warn('old', DeprecationWarning)\n"
        "def run(value):\n"
        "    stale = 1\n"
        "    return value + missing\n"
    )

    assert {decoration.kind for decoration in decorations} == {
        DecorationKind.UNUSED_VARIABLE,
        DecorationKind.UNDEFINED_REFERENCE,
        DecorationKind.DEPRECATED,
    }


@pytest.mark.integration
def test_semantic_decoration_service_honors_preferences() -> None:
    service = SemanticDecorationService.create_default(
        DecorationPreferences(
            unused_variable=False,
            undefined_reference=True,
            deprecated=False,
            type_hint=False,
        )
    )

    decorations = service.analyze_text("stale = 1\nanswer = missing\n")

    assert {decoration.kind for decoration in decorations} == {
        DecorationKind.UNDEFINED_REFERENCE,
    }
