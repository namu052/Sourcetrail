"""Shared source diagnostics used by indexers and UI decoration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DecorationKind(StrEnum):
    """Semantic decoration categories controlled by preferences."""

    UNUSED_VARIABLE = "unused_variable"
    UNDEFINED_REFERENCE = "undefined_reference"
    DEPRECATED = "deprecated"
    TYPE_HINT = "type_hint"


@dataclass(frozen=True, slots=True)
class SourceRange:
    """One-based source range with zero-based columns."""

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
    """A semantic marker ready to apply to an editor."""

    kind: DecorationKind
    range: SourceRange
    message: str
