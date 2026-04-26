#!/usr/bin/env bash
# scripts/compat-check.sh — SourcetrailDB 100% 호환 검증
# SoT: docs/sop/sourcetrail-compat.md, docs/golden-rules.md G14
# 구현 상태: placeholder — Phase 0 D8 (PoC 1)에서 실제 로직 추가.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fixture="${1:-tests/fixtures/sample-minimal/}"

if [[ ! -d "tests" ]] || [[ ! -d "src/sourcetrail_remake/db" ]]; then
  echo "compat-check: project not yet bootstrapped (db/ or tests/ missing) — skipping."
  exit 0
fi

if [[ ! -f "scripts/compat_check_impl.py" ]]; then
  echo "compat-check: implementation not yet present — should be added in Phase 0 D8 (PoC 1)."
  echo "  Expected: scripts/compat_check_impl.py generates a .srctrldb, loads via"
  echo "  original Sourcetrail CLI (if available) and reports node/edge counts."
  echo "  Until then this gate is a no-op placeholder."
  exit 0
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "compat-check: uv not in PATH; skipping locally (CI enforces)."
  exit 0
fi

echo "== compat-check: $fixture =="
uv run python scripts/compat_check_impl.py "$fixture"
