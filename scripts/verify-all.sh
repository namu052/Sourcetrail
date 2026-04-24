#!/usr/bin/env bash
# scripts/verify-all.sh — 공용 검증 게이트 진입점
# SoT: docs/references/build-and-test.md §5
#
# 환경 무관 게이트 (Python 도구 미설치 시 graceful skip):
#   1) lint           (ruff)
#   2) type-check     (mypy strict)  — pyproject.toml 있을 때만
#   3) structure-check
#   4) docs-freshness
#   5) check-adapter-sync
#
# 별도 호출:
#   bash scripts/run-tests.sh                  (uv run pytest)
#   bash scripts/compat-check.sh               (Phase 0 D8 이후)
#   bash scripts/bench.sh                      (tests/performance/ 있을 때)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

step() { printf "\n==[ %s ]==\n" "$1"; }

rc=0

step "lint"
if ! bash scripts/lint.sh; then rc=1; fi

step "type-check"
if ! bash scripts/type-check.sh; then rc=1; fi

step "structure-check"
if ! bash scripts/structure-check.sh; then rc=1; fi

step "docs-freshness"
if ! bash scripts/docs-freshness.sh; then rc=1; fi

step "check-adapter-sync"
if ! bash scripts/check-adapter-sync.sh; then rc=1; fi

echo ""
if [[ "$rc" -eq 0 ]]; then
  echo "verify-all: ALL GATES PASSED"
else
  echo "verify-all: FAILED — see messages above"
fi
exit "$rc"
