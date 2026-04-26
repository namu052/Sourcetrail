#!/usr/bin/env bash
# scripts/docs-freshness.sh — exec-plans/active/ 정체 + 정합성 검사
# SoT: docs/README.md §3, docs/exec-plans/

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail=0
warn=0
fail() { echo "FAIL: $*" >&2; fail=1; }
warn() { echo "WARN: $*" >&2; warn=1; }

ACTIVE_DIR="docs/exec-plans/active"
[[ -d "$ACTIVE_DIR" ]] || { echo "no $ACTIVE_DIR yet — skip"; exit 0; }

now_epoch=$(date +%s)
threshold_days=30

shopt -s nullglob
for f in "$ACTIVE_DIR"/*.md; do
  base=$(basename "$f")
  [[ "$base" == "_template.md" ]] && continue

  lu=$(awk '/^last_updated:/{print $2; exit}' "$f" || true)
  if [[ -z "$lu" || "$lu" == "YYYY-MM-DD" ]]; then
    fail "$f: missing or placeholder last_updated"
    continue
  fi

  if file_epoch=$(date -d "$lu" +%s 2>/dev/null); then :; \
  elif file_epoch=$(date -j -f "%Y-%m-%d" "$lu" +%s 2>/dev/null); then :; \
  else
    warn "$f: cannot parse last_updated=$lu"
    continue
  fi

  age_days=$(( (now_epoch - file_epoch) / 86400 ))
  if (( age_days > threshold_days )); then
    warn "$f: stale ($age_days days since last_updated). Refresh or move to completed/."
  fi

  status=$(awk '/^status:/{print $2; exit}' "$f" || true)
  if [[ -z "$status" ]]; then
    fail "$f: missing status frontmatter"
  fi
done
shopt -u nullglob

# ---- pyproject.toml ↔ docs/references/build-and-test.md 정합성 ----

if [[ -f "pyproject.toml" ]]; then
  py_req=$(grep -E 'requires-python\s*=' pyproject.toml | head -1 || true)
  if [[ -n "$py_req" ]]; then
    if ! grep -qE 'Python.*3\.12' docs/references/build-and-test.md 2>/dev/null; then
      warn "docs/references/build-and-test.md does not mention Python 3.12 from pyproject.toml ($py_req)"
    fi
  fi
fi

# ---- uv.lock ↔ pyproject.toml 정합성 ----

if [[ -f "pyproject.toml" ]] && [[ ! -f "uv.lock" ]]; then
  warn "pyproject.toml present but uv.lock missing — run 'uv sync' and commit uv.lock"
fi

# ---- docs/plan/ 항목이 docs/index-of-deliverables.md에 등재됐는지 ----

if [[ -d "docs/plan" ]] && [[ -f "docs/index-of-deliverables.md" ]]; then
  shopt -s nullglob
  for p in docs/plan/*.md; do
    base=$(basename "$p")
    if ! grep -F "docs/plan/$base" docs/index-of-deliverables.md >/dev/null 2>&1; then
      warn "docs/plan/$base not listed in docs/index-of-deliverables.md"
    fi
  done
  shopt -u nullglob
fi

if [[ "$fail" -ne 0 ]]; then
  echo "docs-freshness: FAILED"
  exit 1
fi
if [[ "$warn" -ne 0 ]]; then
  echo "docs-freshness: passed with warnings"
else
  echo "docs-freshness: OK"
fi
exit 0
