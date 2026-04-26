"""Fuzzy symbol lookup index for project-wide quick open."""

from __future__ import annotations

from dataclasses import dataclass

from rapidfuzz import fuzz, process

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
        """Return exact, prefix, then fuzzy matches for a query."""
        normalized_query = query.strip().casefold()
        if not normalized_query or limit <= 0:
            return []

        ranked: dict[NodeId, FuzzyResult] = {}
        for symbol in self._symbols:
            match_kind, score = self._literal_rank(symbol, normalized_query)
            if match_kind is not None:
                ranked[symbol.node_id] = FuzzyResult(
                    symbol=symbol,
                    score=score,
                    match_kind=match_kind,
                )

        choices = {
            index: f"{symbol.name} {symbol.fqn}"
            for index, symbol in enumerate(self._symbols)
            if symbol.node_id not in ranked
        }
        fuzzy_matches = process.extract(
            query,
            choices,
            scorer=fuzz.WRatio,
            limit=max(limit * 2, limit),
        )
        for _choice, score, index in fuzzy_matches:
            symbol = self._symbols[int(index)]
            adjusted_score = max(float(score), self._subsequence_score(normalized_query, symbol))
            if adjusted_score < 40:
                continue
            ranked[symbol.node_id] = FuzzyResult(
                symbol=symbol,
                score=adjusted_score,
                match_kind="fuzzy",
            )

        return sorted(
            ranked.values(),
            key=lambda result: (
                self._kind_weight(result.match_kind),
                result.score,
                -int(result.symbol.node_id),
            ),
            reverse=True,
        )[:limit]

    def _record_to_symbol(self, record: GraphNodeRecord) -> FuzzySymbol:
        fqn = record.serialized_name
        return FuzzySymbol(
            fqn=fqn,
            name=record.display_name or fqn.rsplit(".", maxsplit=1)[-1],
            node_id=record.id,
        )

    def _literal_rank(self, symbol: FuzzySymbol, normalized_query: str) -> tuple[str | None, float]:
        name = symbol.name.casefold()
        fqn = symbol.fqn.casefold()
        if name == normalized_query or fqn == normalized_query:
            return "exact", 120.0
        if name.startswith(normalized_query) or fqn.startswith(normalized_query):
            return "prefix", 110.0
        return None, 0.0

    def _kind_weight(self, match_kind: str) -> int:
        if match_kind == "exact":
            return 3
        if match_kind == "prefix":
            return 2
        return 1

    def _subsequence_score(self, normalized_query: str, symbol: FuzzySymbol) -> float:
        target = symbol.name.casefold()
        position = -1
        span_start = 0
        for char_index, char in enumerate(normalized_query):
            position = target.find(char, position + 1)
            if position < 0:
                return 0.0
            if char_index == 0:
                span_start = position
        span = max(position - span_start + 1, len(normalized_query))
        compactness = len(normalized_query) / span
        return 80.0 + (compactness * 15.0)
