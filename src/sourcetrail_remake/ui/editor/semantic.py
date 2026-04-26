"""Semantic decoration aggregation for editor integration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sourcetrail_remake.core.diagnostics import Decoration
from sourcetrail_remake.indexer.deprecation import DeprecationAnalyzer
from sourcetrail_remake.indexer.undefined import UndefinedReferenceAnalyzer
from sourcetrail_remake.indexer.unused import UnusedVariableAnalyzer
from sourcetrail_remake.ui.dialogs.preferences import DecorationPreferences


@dataclass(slots=True)
class SemanticDecorationService:
    """Run all MVP semantic analyzers and filter through preferences."""

    preferences: DecorationPreferences
    unused_analyzer: UnusedVariableAnalyzer
    deprecation_analyzer: DeprecationAnalyzer
    undefined_analyzer: UndefinedReferenceAnalyzer

    @classmethod
    def create_default(
        cls,
        preferences: DecorationPreferences | None = None,
    ) -> SemanticDecorationService:
        return cls(
            preferences=preferences or DecorationPreferences(),
            unused_analyzer=UnusedVariableAnalyzer(),
            deprecation_analyzer=DeprecationAnalyzer(),
            undefined_analyzer=UndefinedReferenceAnalyzer(),
        )

    def analyze_text(self, source: str, *, path: Path | None = None) -> list[Decoration]:
        enabled = self.preferences.enabled_kinds()
        decorations = [
            *self.unused_analyzer.decorations_for_text(source, path=path),
            *self.deprecation_analyzer.decorations_for_text(source, path=path),
            *self.undefined_analyzer.decorations_for_text(source, path=path),
        ]
        return [decoration for decoration in decorations if decoration.kind in enabled]

    def analyze_file(self, path: Path) -> list[Decoration]:
        source = Path(path).read_text(encoding="utf-8")
        return self.analyze_text(source, path=Path(path))
