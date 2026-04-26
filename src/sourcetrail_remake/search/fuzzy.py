"""Fuzzy symbol lookup index for project-wide quick open."""

from __future__ import annotations

from dataclasses import dataclass

from sourcetrail_remake.core.types import GraphNodeRecord, NodeId
from sourcetrail_remake.db.reader import DatabaseReader


@dataclass(frozen=True, slots=True)
class FuzzySymbol:
    """Flat symbol entry used by the quick-open fuzzy matcher."""

    fqn: str
    name: str
    node_id: NodeId


@dataclass(frozen=True, slots=True)
class FuzzyResult:
    """Ranked quick-open result."""

    symbol: FuzzySymbol
    score: float
    match_kind: str


class SymbolFuzzyIndex:
    """Build and query a flat project symbol catalog."""

    def __init__(self) -> None:
        self._symbols: tuple[FuzzySymbol, ...] = ()

    def build(self, db: DatabaseReader) -> None:
        """Load non-file symbols from a DatabaseReader into a flat lookup list."""
        records = db.list_symbols(include_files=False)
        self._symbols = tuple(self._record_to_symbol(record) for record in records)

    def symbols(self) -> tuple[FuzzySymbol, ...]:
        """Return the current flat symbol catalog."""
        return self._symbols

    def search(self, query: str, limit: int = 50) -> list[FuzzyResult]:
        """Return ranked results for a query.

        Ranking is added by D92; D91 only establishes the index contract.
        """
        if not query.strip() or limit <= 0:
            return []
        normalized_query = query.casefold()
        results = [
            FuzzyResult(symbol=symbol, score=100.0, match_kind="contains")
            for symbol in self._symbols
            if normalized_query in symbol.fqn.casefold() or normalized_query in symbol.name.casefold()
        ]
        return results[:limit]

    def _record_to_symbol(self, record: GraphNodeRecord) -> FuzzySymbol:
        fqn = record.serialized_name
        return FuzzySymbol(
            fqn=fqn,
            name=record.display_name or fqn.rsplit(".", maxsplit=1)[-1],
            node_id=record.id,
        )
