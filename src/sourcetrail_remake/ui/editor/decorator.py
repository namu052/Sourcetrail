"""Semantic decoration support for the QScintilla editor."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, StrEnum

from PyQt6.Qsci import QsciScintilla
from PyQt6.QtGui import QColor


class DecorationKind(StrEnum):
    """Semantic decoration categories controlled by preferences."""

    UNUSED_VARIABLE = "unused_variable"
    UNDEFINED_REFERENCE = "undefined_reference"
    DEPRECATED = "deprecated"
    TYPE_HINT = "type_hint"


class IndicatorId(IntEnum):
    """Dedicated QScintilla indicator slots used by the decorator."""

    UNUSED_VARIABLE = 8
    UNDEFINED_REFERENCE = 9
    DEPRECATED = 10
    TYPE_HINT = 11


@dataclass(frozen=True, slots=True)
class SourceRange:
    """One-based source range with zero-based columns, matching core SourceLocation."""

    start_line: int
    start_column: int
    end_line: int
    end_column: int

    def normalized(self) -> SourceRange:
        start_line = max(self.start_line, 1)
        end_line = max(self.end_line, start_line)
        start_column = max(self.start_column, 0)
        end_column = max(self.end_column, start_column + 1 if end_line == start_line else 0)
        return SourceRange(start_line, start_column, end_line, end_column)


@dataclass(frozen=True, slots=True)
class Decoration:
    """A semantic marker ready to apply to QScintilla."""

    kind: DecorationKind
    range: SourceRange
    message: str


DEFAULT_ENABLED_DECORATIONS: frozenset[DecorationKind] = frozenset(DecorationKind)


class SyntaxDecorator:
    """Apply semantic indicators to a QScintilla editor."""

    def __init__(
        self,
        editor: QsciScintilla,
        *,
        enabled: frozenset[DecorationKind] = DEFAULT_ENABLED_DECORATIONS,
    ) -> None:
        self.editor = editor
        self.enabled = enabled
        self._configure_indicators()

    def set_enabled(self, enabled: frozenset[DecorationKind]) -> None:
        self.enabled = enabled

    def apply(self, decorations: list[Decoration]) -> None:
        """Clear known indicators and apply enabled decorations."""
        self.clear()
        for decoration in decorations:
            if decoration.kind not in self.enabled:
                continue
            self._fill_indicator(decoration)

    def clear(self) -> None:
        """Clear all decorator-managed indicators across the current document."""
        line_count = max(self.editor.lines(), 1)
        last_line = line_count - 1
        last_column = max(self.editor.lineLength(last_line), 0)
        for indicator_id in IndicatorId:
            self.editor.clearIndicatorRange(0, 0, last_line, last_column, int(indicator_id))

    def _configure_indicators(self) -> None:
        self._define_indicator(
            IndicatorId.UNUSED_VARIABLE,
            QsciScintilla.IndicatorStyle.SquiggleIndicator,
            "#8c959f",
        )
        self._define_indicator(
            IndicatorId.UNDEFINED_REFERENCE,
            QsciScintilla.IndicatorStyle.SquiggleIndicator,
            "#d1242f",
        )
        self._define_indicator(
            IndicatorId.DEPRECATED,
            QsciScintilla.IndicatorStyle.StraightBoxIndicator,
            "#bf8700",
        )
        self._define_indicator(
            IndicatorId.TYPE_HINT,
            QsciScintilla.IndicatorStyle.PlainIndicator,
            "#0969da",
        )

    def _define_indicator(
        self,
        indicator_id: IndicatorId,
        style: QsciScintilla.IndicatorStyle,
        color: str,
    ) -> None:
        self.editor.indicatorDefine(style, int(indicator_id))
        self.editor.setIndicatorForegroundColor(QColor(color), int(indicator_id))

    def _fill_indicator(self, decoration: Decoration) -> None:
        source_range = decoration.range.normalized()
        indicator_id = _indicator_for_kind(decoration.kind)
        self.editor.fillIndicatorRange(
            source_range.start_line - 1,
            source_range.start_column,
            source_range.end_line - 1,
            source_range.end_column,
            int(indicator_id),
        )


def _indicator_for_kind(kind: DecorationKind) -> IndicatorId:
    if kind == DecorationKind.UNUSED_VARIABLE:
        return IndicatorId.UNUSED_VARIABLE
    if kind == DecorationKind.UNDEFINED_REFERENCE:
        return IndicatorId.UNDEFINED_REFERENCE
    if kind == DecorationKind.DEPRECATED:
        return IndicatorId.DEPRECATED
    return IndicatorId.TYPE_HINT
