"""Week 22 fuzzy lookup performance gate."""

from __future__ import annotations

from time import perf_counter

import pytest

from sourcetrail_remake.core.types import NodeId
from sourcetrail_remake.search.fuzzy import FuzzySymbol, SymbolFuzzyIndex


@pytest.mark.performance
def test_fuzzy_lookup_exact_match_stays_under_50ms_for_large_catalog() -> None:
    index = SymbolFuzzyIndex()
    index.set_symbols(
        FuzzySymbol(
            fqn=f"large.module_{number:05d}.Symbol{number:05d}",
            name=f"Symbol{number:05d}",
            node_id=NodeId(number + 1),
        )
        for number in range(100_000)
    )

    started = perf_counter()
    results = index.search("Symbol99999", limit=20)
    elapsed_ms = (perf_counter() - started) * 1000

    assert results[0].symbol.fqn == "large.module_99999.Symbol99999"
    assert elapsed_ms < 50
