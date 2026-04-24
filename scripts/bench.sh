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
exec uv run pytest tests/performance -m performance \
  --benchmark-json="$out" \
  "$@"
