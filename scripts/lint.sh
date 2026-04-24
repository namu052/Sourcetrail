#!/usr/bin/env bash
# scripts/lint.sh — ruff 게이트 (변경 파일 한정)
# SoT: docs/references/build-and-test.md §4

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

mode="${1:-}"

# uv 가용 여부 확인
if ! command -v uv >/dev/null 2>&1; then
  # 로컬 개발 머신에 uv 없을 수 있음. CI(harness-gate.yml)는 항상 설치.
  files="$(bash scripts/changed-files.sh 2>/dev/null | grep -E '\.py$' || true)"
  if [[ -z "$files" ]]; then
    echo "lint: uv not in PATH and no Python changes — skipping locally."
    exit 0
  fi
  echo "lint: uv not in PATH; CI will enforce. Skipping locally." >&2
  exit 0
fi

# pyproject.toml이 아직 없으면 (Phase 0 D1 이전) skip
if [[ ! -f "pyproject.toml" ]]; then
  echo "lint: pyproject.toml missing (pre-Phase-0 state) — skipping."
  exit 0
fi

if [[ "$mode" == "--staged-only" ]]; then
  files="$(bash scripts/changed-files.sh --staged | grep -E '\.py$' || true)"
else
  files="$(bash scripts/changed-files.sh | grep -E '\.py$' || true)"
fi

if [[ -z "$files" ]]; then
  echo "lint: no Python files changed."
  exit 0
fi

# C++ legacy 및 외부 소스는 Python이 아니므로 이미 필터링됨.
# poc/ 는 격리된 PoC 디렉터리 — lint는 적용하지만 mypy strict는 제외 가능.

fail=0

echo "== ruff check =="
if ! uv run ruff check $files; then
  fail=1
fi

echo "== ruff format --check =="
if ! uv run ruff format --check $files; then
  echo ""
  echo "lint: format violations. Run:"
  echo "  uv run ruff format <file>"
  fail=1
fi

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi

echo "lint: OK ($(echo "$files" | wc -l | tr -d ' ') file(s))"
