"""Additional branch coverage for Week 15 semantic decoration modules."""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest
from PyQt6.Qsci import QsciScintilla
from PyQt6.QtCore import QSettings

from sourcetrail_remake.core.diagnostics import Decoration, DecorationKind, SourceRange
from sourcetrail_remake.indexer.deprecation import DeprecationAnalyzer
from sourcetrail_remake.indexer.undefined import UndefinedReferenceAnalyzer
from sourcetrail_remake.indexer.unused import UnusedVariableAnalyzer
from sourcetrail_remake.ui.dialogs.preferences import DecorationPreferences
from sourcetrail_remake.ui.editor.decorator import SyntaxDecorator
from sourcetrail_remake.ui.editor.semantic import SemanticDecorationService
from sourcetrail_remake.ui.layout_manager import LayoutManager, LayoutSnapshot


class FakeEditor:
    def __init__(self) -> None:
        self.defined: list[tuple[object, int]] = []
        self.colors: list[tuple[object, int]] = []
        self.filled: list[tuple[int, int, int, int, int]] = []
        self.cleared: list[tuple[int, int, int, int, int]] = []

    def indicatorDefine(self, style: object, indicator_id: int) -> None:
        self.defined.append((style, indicator_id))

    def setIndicatorForegroundColor(self, color: object, indicator_id: int) -> None:
        self.colors.append((color, indicator_id))

    def lines(self) -> int:
        return 2

    def lineLength(self, _line: int) -> int:
        return 12

    def clearIndicatorRange(
        self,
        start_line: int,
        start_column: int,
        end_line: int,
        end_column: int,
        indicator_id: int,
    ) -> None:
        self.cleared.append((start_line, start_column, end_line, end_column, indicator_id))

    def fillIndicatorRange(
        self,
        start_line: int,
        start_column: int,
        end_line: int,
        end_column: int,
        indicator_id: int,
    ) -> None:
        self.filled.append((start_line, start_column, end_line, end_column, indicator_id))


@pytest.mark.unit
def test_syntax_decorator_applies_only_enabled_indicators() -> None:
    editor = FakeEditor()
    decorator = SyntaxDecorator(
        cast(QsciScintilla, editor),
        enabled=frozenset({DecorationKind.DEPRECATED}),
    )
    decorator.apply(
        [
            Decoration(DecorationKind.UNUSED_VARIABLE, SourceRange(1, 0, 1, 6), "unused"),
            Decoration(DecorationKind.DEPRECATED, SourceRange(2, 4, 2, 7), "deprecated"),
        ]
    )

    assert len(editor.defined) == 4
    assert editor.filled == [(1, 4, 1, 7, 10)]
    assert len(editor.cleared) == 4


@pytest.mark.unit
def test_analyzers_cover_file_and_nested_scope_paths(tmp_path: Path) -> None:
    source_path = tmp_path / "sample.py"
    source_path.write_text(
        "import warnings\n"
        "from pathlib import Path\n"
        "@deprecated\n"
        "class Old:\n"
        "    pass\n"
        "async def task(value):\n"
        "    unused = 1\n"
        "    lambda item: item\n"
        "    warnings.warn('x', DeprecationWarning)\n"
        "    return Path(str(value)) + missing\n",
        encoding="utf-8",
    )

    assert UnusedVariableAnalyzer().analyze_file(source_path)[0].name == "unused"
    assert DeprecationAnalyzer().analyze_file(source_path)[0].name == "Old"
    assert UndefinedReferenceAnalyzer().analyze_file(source_path)[0].name == "deprecated"


@pytest.mark.unit
def test_semantic_service_analyze_file_and_empty_layout_paths(tmp_path: Path) -> None:
    source_path = tmp_path / "sample.py"
    source_path.write_text("unused = missing\n", encoding="utf-8")
    service = SemanticDecorationService.create_default(
        DecorationPreferences(deprecated=False, type_hint=False)
    )
    settings = QSettings(str(tmp_path / "layout.ini"), QSettings.Format.IniFormat)

    assert {decoration.kind for decoration in service.analyze_file(source_path)} == {
        DecorationKind.UNUSED_VARIABLE,
        DecorationKind.UNDEFINED_REFERENCE,
    }
    assert LayoutSnapshot(b"", b"").is_empty
    assert LayoutManager(settings).load().is_empty
