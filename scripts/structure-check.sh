#!/usr/bin/env bash
# scripts/structure-check.sh — 아키텍처/시크릿/보호 경로 룰 강제
# SoT: docs/references/architecture-rules.md, docs/security.md, docs/golden-rules.md

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail=0
warn=0
fail() { echo "FAIL: $*" >&2; fail=1; }
warn() { echo "WARN: $*" >&2; warn=1; }

PYROOT="src/sourcetrail_remake"

# ---- 1. Python 레이어 룰 (docs/references/architecture-rules.md §2) ----
# src/sourcetrail_remake/이 아직 없으면(Phase 0 D1 이전) §1 건너뜀.

if [[ -d "$PYROOT" ]]; then
  # 1-1. Domain(core/project, core/types 등) 격리
  if grep -rEn '^\s*(from|import)\s+(PyQt6|jedi|parso|rope|sqlite3)' \
       "$PYROOT/core/project.py" "$PYROOT/core/types.py" 2>/dev/null; then
    fail "Domain (core/project.py, core/types.py) must not import frameworks"
  fi

  # 1-2. Infrastructure → UI 금지
  for infra in db indexer refactor search; do
    if [[ -d "$PYROOT/$infra" ]]; then
      if grep -rEn '^\s*(from|import)\s+sourcetrail_remake\.ui' \
           "$PYROOT/$infra/" 2>/dev/null; then
        fail "Infrastructure ($infra/) must not depend on UI"
      fi
      if grep -rEn '^\s*(from|import)\s+sourcetrail_remake\.cli' \
           "$PYROOT/$infra/" 2>/dev/null; then
        fail "Infrastructure ($infra/) must not depend on CLI"
      fi
    fi
  done

  # 1-3. UI가 외부 분석 라이브러리 직접 사용 금지
  if [[ -d "$PYROOT/ui" ]]; then
    if grep -rEn '^\s*(from|import)\s+(jedi|parso|rope|sqlite3)' \
         "$PYROOT/ui/" 2>/dev/null; then
      fail "UI must go through Infrastructure (no direct jedi/parso/rope/sqlite3)"
    fi
  fi

  # 1-4. CLI → UI 금지
  if [[ -d "$PYROOT/cli" ]]; then
    if grep -rEn '^\s*(from|import)\s+sourcetrail_remake\.ui' \
         "$PYROOT/cli/" 2>/dev/null; then
      fail "CLI must not import UI"
    fi
  fi

  # 1-5. 패널 간 직접 import (EventBus 우회 금지)
  if [[ -d "$PYROOT/ui/panels" ]]; then
    if grep -rEn '^\s*(from|import)\s+sourcetrail_remake\.ui\.panels\.' \
         "$PYROOT/ui/panels/" 2>/dev/null | grep -v '__init__'; then
      warn "panels importing sibling panels — should communicate via core.event_bus"
    fi
  fi

  # 1-6. print 직접 사용
  if grep -rEn '\bprint\(' "$PYROOT/" 2>/dev/null \
       | grep -v '# allow-print' | grep -v '__main__.py'; then
    warn "use logging, not print (suppress with '# allow-print' comment)"
  fi

  # 1-7. pip subprocess
  if grep -rEn 'subprocess.*pip' "$PYROOT/" 2>/dev/null; then
    fail "do not call pip from code; use uv (Golden Rule G13)"
  fi

  # 1-8. 프레임워크 import는 frameworks/ 하위만
  if grep -rEn '^\s*(from|import)\s+(django|flask|fastapi|sqlalchemy)' \
       "$PYROOT/" 2>/dev/null \
       | grep -vE "$PYROOT/indexer/frameworks/"; then
    fail "framework imports allowed only in indexer/frameworks/"
  fi
fi

# ---- 2. Golden Rule G13 — uv 외 의존성 매니저 금지 ----

if [[ -f "poetry.lock" ]]; then fail "poetry.lock detected — use uv (Golden Rule G13)"; fi
if [[ -f "Pipfile" ]] || [[ -f "Pipfile.lock" ]]; then fail "pipenv detected — use uv (Golden Rule G13)"; fi
if [[ -f "requirements.txt" ]] && ! [[ -f "uv.lock" ]]; then
  warn "requirements.txt without uv.lock. 본 프로젝트는 uv.lock이 SoT."
fi

# ---- 3. Golden Rule G15 — Windows 전용 (분기 코드 감지) ----

if [[ -d "$PYROOT" ]]; then
  if grep -rEn "sys\.platform\s*(==|!=)\s*['\"]darwin['\"]" "$PYROOT/" 2>/dev/null; then
    warn "macOS branch in code — G15 says Windows-only. Get human approval."
  fi
  if grep -rEn "sys\.platform\s*(==|!=)\s*['\"]linux['\"]" "$PYROOT/" 2>/dev/null; then
    warn "Linux branch in code — G15 says Windows-only. Get human approval."
  fi
fi

# ---- 4. 시크릿 패턴 (docs/security.md) ----

PATTERNS='(sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----)'
changed="$(bash scripts/changed-files.sh 2>/dev/null || true)"
if [[ -n "$changed" ]]; then
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    [[ ! -f "$f" ]] && continue
    # .travis.yml의 base64 encrypted deploy key는 기존 legacy — skip
    if [[ "$f" == ".travis.yml" ]]; then continue; fi
    if grep -EnH "$PATTERNS" "$f" >/dev/null 2>&1; then
      fail "possible secret in $f (see docs/security.md)"
    fi
  done <<<"$changed"
fi

# ---- 5. 절대 경로 하드코딩 (Python 테스트/코드) ----

if [[ -n "$changed" ]]; then
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    [[ ! -f "$f" ]] && continue
    case "$f" in
      tests/*|src/sourcetrail_remake/*)
        if grep -EnH '"(/home/|C:[\\/]Users[\\/])' "$f" >/dev/null 2>&1; then
          warn "$f: hardcoded absolute path — use tmp_path / fixtures."
        fi
        ;;
    esac
  done <<<"$changed"
fi

# ---- 6. 파일/라인 크기 (G12, soft) ----

if [[ -n "$changed" ]]; then
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    [[ ! -f "$f" ]] && continue
    case "$f" in
      src/sourcetrail_remake/*.py|tests/*.py)
        lines=$(wc -l <"$f" | tr -d ' ')
        if (( lines > 800 )); then
          warn "$f: $lines lines (>800, consider split — Golden Rule G12)"
        fi
        ;;
    esac
  done <<<"$changed"
fi

# ---- 7. C++ legacy 영역 변경 감지 (G7) ----
# 수정 자체를 막진 않지만 사람 승인 필요 경로로 warn.

if [[ -n "$changed" ]]; then
  while IFS= read -r f; do
    case "$f" in
      CMakeLists.txt|cmake/*|script/*|.clang-format|.travis.yml|appveyor.yml)
        warn "$f: C++ legacy touched — Golden Rule G7 requires human approval (docs/sop/human-approval.md)"
        ;;
      src/lib*/*|src/app/*|src/indexer/*|src/external/*|src/test/*|java_indexer/*|ide_plugins/*|bin/*|deployment/*|setup/*|testing/*)
        warn "$f: C++ legacy touched — Golden Rule G7 requires human approval"
        ;;
      docs/documentation/*|docs/readme/*)
        warn "$f: legacy Sourcetrail docs touched — Golden Rule G7"
        ;;
    esac
  done <<<"$changed"
fi

# ---- 8. 보호 경로 (docs/sop/human-approval.md §1) ----

if [[ -n "$changed" ]]; then
  while IFS= read -r f; do
    case "$f" in
      pyproject.toml|uv.lock|.pre-commit-config.yaml|.github/CODEOWNERS|.github/workflows/*|.claude/hooks/*|.codex/config.*.toml|docs/golden-rules.md|docs/security.md|docs/reliability.md|docs/sop/human-approval.md|docs/plan/*)
        warn "$f: protected path changed — see docs/sop/human-approval.md (human approval required)"
        ;;
    esac
  done <<<"$changed"
fi

if [[ "$fail" -ne 0 ]]; then
  echo ""
  echo "structure-check: FAILED. See messages above and docs/references/architecture-rules.md."
  exit 1
fi

if [[ "$warn" -ne 0 ]]; then
  echo "structure-check: passed with warnings."
else
  echo "structure-check: OK"
fi
exit 0
