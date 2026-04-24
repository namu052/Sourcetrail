#!/usr/bin/env bash
# scripts/type-check.sh — mypy strict 게이트
# SoT: docs/references/build-and-test.md §4, docs/golden-rules.md G1

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "type-check: uv not in PATH; CI will enforce. Skipping locally." >&2
  exit 0
fi

if [[ ! -f "pyproject.toml" ]]; then
  echo "type-check: pyproject.toml missing (pre-Phase-0 state) — skipping."
  exit 0
fi

if [[ ! -d "src/sourcetrail_remake" ]]; then
  echo "type-check: src/sourcetrail_remake/ missing (pre-Phase-0 state) — skipping."
  exit 0
fi

# mypy는 전체 src/를 본다 (타입 의존성 때문에 변경 파일 한정이 어려움).
# strict 모드는 pyproject.toml의 [tool.mypy]에서 설정.

echo "== mypy strict (src/) =="
uv run mypy src/
