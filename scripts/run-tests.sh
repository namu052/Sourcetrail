#!/usr/bin/env bash
# scripts/run-tests.sh — uv run pytest 래퍼
# SoT: docs/references/build-and-test.md §3

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "run-tests: uv not in PATH. Install uv first." >&2
  exit 127
fi

if [[ ! -f "pyproject.toml" ]]; then
  echo "run-tests: pyproject.toml missing (pre-Phase-0 state) — nothing to run." >&2
  exit 0
fi

if [[ ! -d "tests" ]]; then
  echo "run-tests: tests/ missing — nothing to run yet." >&2
  exit 0
fi

# 인자가 없으면 전체, 있으면 그대로 패스스루 (-m unit, -k name, 파일경로 등)
exec uv run pytest "$@"
