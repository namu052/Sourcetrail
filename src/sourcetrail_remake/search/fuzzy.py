"""Fuzzy symbol lookup index for project-wide quick open."""

from __future__ import annotations

from collections.abc import Iterable
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


@dataclass(frozen=True, slots=True)
class _SearchEntry:
    symbol: FuzzySymbol
    normalized_name: str
    normalized_fqn: str
    choice: str


class SymbolFuzzyIndex:
    """Build and query a flat project symbol catalog."""

    def __init__(self) -> None:
        self._symbols: tuple[FuzzySymbol, ...] = ()
        self._entries: tuple[_SearchEntry, ...] = ()
        self._exact_entries: dict[str, tuple[_SearchEntry, ...]] = {}

    def build(self, db: DatabaseReader) -> None:
        """Load non-file symbols from a DatabaseReader into a flat lookup list."""
        records = db.list_symbols(include_files=False)
        self.set_symbols(self._record_to_symbol(record) for record in records)

    def set_symbols(self, symbols: Iterable[FuzzySymbol]) -> None:
        """Replace the lookup catalog with prebuilt symbols."""
        self._symbols = tuple(symbols)
        self._entries = tuple(_entry_for(symbol) for symbol in self._symbols)
        self._exact_entries = _exact_lookup(self._entries)

    def symbols(self) -> tuple[FuzzySymbol, ...]:
        """Return the current flat symbol catalog."""
        return self._symbols

    def search(self, query: str, limit: int = 50) -> list[FuzzyResult]:
        """Return exact, prefix, then fuzzy matches for a query."""
        normalized_query = query.strip().casefold()
        if not normalized_query or limit <= 0:
            return []
        entries = self._current_entries()
        exact_entries = self._exact_entries.get(normalized_query, ())
        if exact_entries:
            return self._sort_results(
                FuzzyResult(symbol=entry.symbol, score=120.0, match_kind="exact")
                for entry in exact_entries
            )[:limit]

        ranked: dict[NodeId, FuzzyResult] = {}
        for entry in entries:
            match_kind, score = self._literal_rank(entry, normalized_query)
            if match_kind is not None:
                symbol = entry.symbol
                ranked[symbol.node_id] = FuzzyResult(
                    symbol=symbol,
                    score=score,
                    match_kind=match_kind,
                )
        exact_results = [
            result for result in ranked.values() if result.match_kind == "exact"
        ]
        if exact_results:
            return self._sort_results(exact_results)[:limit]
        if len(ranked) >= limit:
            return self._sort_results(ranked.values())[:limit]

        choices = {
            index: entry.choice
            for index, entry in enumerate(entries)
            if entry.symbol.node_id not in ranked
            and self._could_match_fuzzy(normalized_query, entry)
        }
        fuzzy_matches = process.extract(
            query,
            choices,
            scorer=fuzz.WRatio,
            limit=max(limit * 2, limit),
        )
        for _choice, score, index in fuzzy_matches:
            symbol = entries[int(index)].symbol
            adjusted_score = max(
                float(score),
                self._subsequence_score(normalized_query, entries[int(index)]),
            )
            if adjusted_score < 40:
                continue
            ranked[symbol.node_id] = FuzzyResult(
                symbol=symbol,
                score=adjusted_score,
                match_kind="fuzzy",
            )

        return self._sort_results(ranked.values())[:limit]

    def _record_to_symbol(self, record: GraphNodeRecord) -> FuzzySymbol:
        fqn = record.serialized_name
        return FuzzySymbol(
            fqn=fqn,
            name=record.display_name or fqn.rsplit(".", maxsplit=1)[-1],
            node_id=record.id,
        )

    def _current_entries(self) -> tuple[_SearchEntry, ...]:
        if len(self._entries) != len(self._symbols):
            self._entries = tuple(_entry_for(symbol) for symbol in self._symbols)
            self._exact_entries = _exact_lookup(self._entries)
        return self._entries

    def _literal_rank(
        self, entry: _SearchEntry, normalized_query: str
    ) -> tuple[str | None, float]:
        if entry.normalized_name == normalized_query or entry.normalized_fqn == normalized_query:
            return "exact", 120.0
        if entry.normalized_name.startswith(normalized_query) or entry.normalized_fqn.startswith(
            normalized_query
        ):
            return "prefix", 110.0
        return None, 0.0

    def _kind_weight(self, match_kind: str) -> int:
        if match_kind == "exact":
            return 3
        if match_kind == "prefix":
            return 2
        return 1

    def _could_match_fuzzy(self, normalized_query: str, entry: _SearchEntry) -> bool:
        return (
            normalized_query in entry.normalized_name
            or normalized_query in entry.normalized_fqn
            or _is_subsequence(normalized_query, entry.normalized_name)
            or _is_subsequence(normalized_query, entry.normalized_fqn)
        )

    def _subsequence_score(self, normalized_query: str, entry: _SearchEntry) -> float:
        target = entry.normalized_name
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

    def _sort_results(self, results: Iterable[FuzzyResult]) -> list[FuzzyResult]:
        return sorted(
            results,
            key=lambda result: (
                self._kind_weight(result.match_kind),
                result.score,
                -int(result.symbol.node_id),
            ),
            reverse=True,
        )


def _entry_for(symbol: FuzzySymbol) -> _SearchEntry:
    return _SearchEntry(
        symbol=symbol,
        normalized_name=symbol.name.casefold(),
        normalized_fqn=symbol.fqn.casefold(),
        choice=f"{symbol.name} {symbol.fqn}",
    )


def _exact_lookup(entries: Iterable[_SearchEntry]) -> dict[str, tuple[_SearchEntry, ...]]:
    lookup: dict[str, list[_SearchEntry]] = {}
    for entry in entries:
        lookup.setdefault(entry.normalized_name, []).append(entry)
        if entry.normalized_fqn != entry.normalized_name:
            lookup.setdefault(entry.normalized_fqn, []).append(entry)
    return {key: tuple(value) for key, value in lookup.items()}


def _is_subsequence(needle: str, haystack: str) -> bool:
    position = -1
    for char in needle:
        position = haystack.find(char, position + 1)
        if position < 0:
            return False
    return True
