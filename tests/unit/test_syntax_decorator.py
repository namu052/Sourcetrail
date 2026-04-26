"""Unit coverage for semantic decoration data helpers."""

from __future__ import annotations

import pytest

from sourcetrail_remake.core.diagnostics import DecorationKind, SourceRange
from sourcetrail_remake.ui.editor.decorator import (
    IndicatorId,
    _indicator_for_kind,
)


@pytest.mark.unit
def test_source_range_normalizes_to_valid_qscintilla_coordinates() -> None:
    assert SourceRange(0, -4, 0, -1).normalized() == SourceRange(1, 0, 1, 1)


@pytest.mark.unit
def test_decoration_kinds_have_stable_indicator_slots() -> None:
    assert _indicator_for_kind(DecorationKind.UNUSED_VARIABLE) == IndicatorId.UNUSED_VARIABLE
    assert (
        _indicator_for_kind(DecorationKind.UNDEFINED_REFERENCE) == IndicatorId.UNDEFINED_REFERENCE
    )
    assert _indicator_for_kind(DecorationKind.DEPRECATED) == IndicatorId.DEPRECATED
    assert _indicator_for_kind(DecorationKind.TYPE_HINT) == IndicatorId.TYPE_HINT
