#!/usr/bin/env bash
# scripts/bench.sh — 성능 벤치 실행 (pytest-benchmark)
# SoT: docs/observability.md §8, docs/plan/01-requirements.md (비기능 요구사항)
# 사용: bash scripts/bench.sh [추가 pytest 인자]

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "bench: uv not in PATH" >&2; exit 127
fi

if [[ ! -d "tests/performance" ]]; then
  echo "bench: tests/performance/ missing — nothing to benchmark yet." >&2
  exit 0
fi

mkdir -p docs/generated/bench
ts=$(date +%Y%m%d-%H%M%S)
out="docs/generated/bench/${ts}.json"

echo "== benchmarks → $out =="
if ! find tests/performance -name 'test_*.py' -print -quit | grep -q .; then
  echo "bench: no pytest performance tests found; running native Phase 1 fallback."
  exec uv run python scripts/bench_phase1.py "$out"
fi

exec uv run pytest tests/performance -m performance \
  --benchmark-json="$out" \
  "$@"
