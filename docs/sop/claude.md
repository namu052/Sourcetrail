# SOP — Claude Code (Sourcetrail_Remake / Python)

Claude Code로 본 리포에서 작업할 때의 표준 절차. **공용 진입은 `CLAUDE.md` → 이 SOP → `docs/README.md` → `docs/plan/00-overview.md`** 순.

## 1. 시작

- 새 작업: `docs/README.md` 우선순위 + `docs/plan/00-overview.md`로 phase 컨텍스트.
- 큰 변경: `/explore-codebase` 스킬로 모듈맵 (Python 트리 + C++ legacy 격리) 확인.
- 계획: `/create-exec-plan` 스킬로 `docs/exec-plans/active/` 새 plan.

## 2. 표준 작업 루프

`docs/sop/codex.md` §2와 동일. Claude 실행 포인트:

| 단계 | Claude 메커니즘 |
|---|---|
| 1. 컨텍스트 | Read / Glob / Grep, 또는 `Explore` 서브에이전트 |
| 2. 계획 | `/create-exec-plan` SKILL |
| 3. 재현 | 직접 pytest 호출 또는 `e2e-runner` 에이전트 (UI 시나리오) |
| 4. 수정 | Edit / Write |
| 5. 검증 | `/run-verification` SKILL → `bash scripts/verify-all.sh` |
| 6. 자기 리뷰 | `code-reviewer` 에이전트 |
| 7. compat (해당 시) | `bash scripts/compat-check.sh` |
| 8. PR | `/prepare-pr` SKILL |

## 3. 권한 / Hook

`docs/security.md`와 같은 룰. Claude 강제 메커니즘:

- **Permissions**: 기본 `default` 모드. `acceptEdits`는 위험 명령 통제와 충돌 — 사용 금지.
- **PreToolUse hook**: `Bash`의 위험 명령 차단 (rm -rf, --force, --no-verify, pip install 등). `.claude/hooks/README.md` 초안.
- **PostToolUse hook**: `.py` 편집 후 `uv run ruff format` 자동 (Phase 0 D2 이후).

> hook 적용은 **사용자 승인 필요**. 글로벌 `~/.claude/settings.json`과 충돌 검토 후 `update-config` 스킬.

## 4. 에이전트 사용 우선순위

(글로벌 `~/.claude/rules/agents.md`와 호환)

```
1. planner       → 무엇을
2. architect     → 어떻게
3. tdd-guide     → 테스트와 함께 구현
4. code-reviewer → 품질
5. security-reviewer → 보안 (커밋 전)
6. e2e-runner    → UI 시나리오 (pytest-qt)
```

## 5. 모델 선택

| 작업 | 권장 |
|---|---|
| 일상 코딩, 오케스트레이션 | Sonnet 4.6 |
| 아키텍처 결정, 깊은 분석 | Opus 4.7 |
| 반복적 단순 작업 (lint fix, format) | Haiku 4.5 |

## 6. 컨텍스트 윈도우

마지막 20%에선 **대규모 리팩토링 / 다중 파일 변경 금지** (글로벌 규칙).
필요 시 작업 분할 → `docs/exec-plans/active/`의 plan이 새 세션 인계 매개체.

## 7. Claude 전용 주의

- **memory 시스템**: 글로벌 사용자 정보는 OK. 본 리포 정책은 모두 `docs/`. memory에 정책 사본 두지 말 것.
- **slash command (skill)**: 본 리포의 SKILL은 `.claude/skills/` 4종만. 추가는 사람 승인.
- **MCP 서버**: 너무 많이 활성화 금지. 본 리포 작업엔 기본 도구로 충분.
- **C++ legacy**: Read는 자유, Edit/Write는 G7 — 사람 승인 필요.
