#!/usr/bin/env bash
# scripts/check-adapter-sync.sh — AGENTS.md ↔ CLAUDE.md ↔ adapter configs 드리프트 검사
# SoT: docs/golden-rules.md G5, docs/failure-modes.md #1, docs/index-of-deliverables.md

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail=0
warn=0
fail() { echo "FAIL: $*" >&2; fail=1; }
warn() { echo "WARN: $*" >&2; warn=1; }

# ---- 1. 두 어댑터 모두 docs/README.md를 첫 링크로 ----

for f in AGENTS.md CLAUDE.md; do
  if [[ ! -f "$f" ]]; then
    fail "$f missing"
    continue
  fi
  if ! grep -m1 -E '^[0-9]+\.\s+\[`?docs/README\.md`?\]' "$f" >/dev/null; then
    fail "$f: 'Harness Entry' should list docs/README.md as item #1"
  fi
done

# ---- 2. Harness Entry 섹션이 너무 길면 경고 ----

for f in AGENTS.md CLAUDE.md; do
  [[ -f "$f" ]] || continue
  lines=$(awk '/^## Harness Entry/{flag=1; next} flag && /^## /{exit} flag' "$f" | wc -l | tr -d ' ')
  if (( lines > 30 )); then
    warn "$f: Harness Entry section is $lines lines (>30). Move policy to docs/."
  fi
done

# ---- 3. .codex/config.toml ↔ .codex/config.balanced.toml 동기 ----

if [[ -f .codex/config.toml && -f .codex/config.balanced.toml ]]; then
  if ! diff <(grep -vE '^\s*(#|$)' .codex/config.toml) \
            <(grep -vE '^\s*(#|$)' .codex/config.balanced.toml) >/dev/null; then
    warn ".codex/config.toml ↔ .codex/config.balanced.toml differ. Re-sync."
  fi
fi

# ---- 4. .codex/config.*.toml의 [shell] allow 리스트에 deprecated C++ 명령 잔존 검사 ----
# [paths] protected의 "cmake/**"(G7 보호용)는 정당하므로 제외.

for cf in .codex/config.toml .codex/config.balanced.toml .codex/config.semi-autonomous.toml; do
  [[ -f "$cf" ]] || continue
  # [shell] 섹션부터 다음 [section]까지 추출해서 검사
  shell_block=$(awk '/^\[shell\]/{flag=1; next} flag && /^\[/{flag=0} flag' "$cf")
  if echo "$shell_block" | grep -E '"(cmake |bash script/buildonly\.sh|bash script/build\.sh|^ninja)' >/dev/null 2>&1; then
    fail "$cf: deprecated C++ build command in [shell] allowlist (this project is Python). See docs/references/build-and-test.md."
  fi
done

# ---- 5. docs/index-of-deliverables.md 항목이 실제 존재하는지 ----
# 단, `*` glob 패턴이 들어간 경로는 G7 보호 영역 묘사용이므로 검사 제외.

INDEX="docs/index-of-deliverables.md"
if [[ -f "$INDEX" ]]; then
  while IFS= read -r path; do
    [[ -z "$path" ]] && continue
    # glob 패턴은 묘사용 (e.g. src/lib*/ 또는 src/lib*/, src/app/...)
    case "$path" in
      *\**) continue ;;
      *,*) continue ;;   # 콤마 포함도 묘사용
    esac
    if [[ ! -e "$path" ]]; then
      fail "index-of-deliverables.md references missing path: $path"
    fi
  done < <(awk -F'|' '
    /^\| `[^`]+`/ {
      n = split($2, a, "`");
      if (n >= 2) print a[2];
    }
  ' "$INDEX")
fi

# ---- 6. 어댑터에 정책 본문 복붙 흔적 ----
# 도구 권한/샌드박스 정책이 AGENTS/CLAUDE 본문에 들어오면 fail

for f in AGENTS.md CLAUDE.md; do
  [[ -f "$f" ]] || continue
  if grep -E '^\s*(sandbox_mode|approval_policy|network_access|auto_confirm)\s*=' "$f" >/dev/null; then
    fail "$f: contains adapter-config policy body. Move to .codex/ or .claude/ (Golden Rule G5)."
  fi
  if grep -E '(sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36})' "$f" >/dev/null; then
    fail "$f: secret-like string found."
  fi
done

if [[ "$fail" -ne 0 ]]; then
  echo "check-adapter-sync: FAILED"
  exit 1
fi
if [[ "$warn" -ne 0 ]]; then
  echo "check-adapter-sync: passed with warnings"
else
  echo "check-adapter-sync: OK"
fi
exit 0
