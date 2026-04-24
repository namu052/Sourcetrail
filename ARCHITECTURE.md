# ARCHITECTURE.md

이 문서는 **공용 하네스 엔지니어링 시스템**의 최상위 아키텍처를 정의한다.
구체적 운영 규칙·정책은 `docs/`에 있고, 도구별 사용법은 어댑터(`AGENTS.md`, `CLAUDE.md`, `.codex/`, `.claude/`)에 있다. 이 파일은 **그 둘이 어떻게 맞물리는지**만 기술한다.

> 본 리포의 작업 대상은 **Sourcetrail_Remake (Python 데스크톱 앱)**. 기존 C++ Sourcetrail은 **읽기 전용 reference**.

## 1. 핵심 원칙

| # | 원칙 |
|---|---|
| 1 | 공용 코어 80~90% / 도구별 분기 10~20%. |
| 2 | Source of truth는 `docs/`와 `scripts/`. AGENTS.md/CLAUDE.md는 **링크 허브**. |
| 3 | "권고"보다 "**자동으로 검사되고 위반 시 실패하는 규칙**". |
| 4 | 사람은 승인·고위험·프로덕션 결정. 에이전트는 탐색·수정·검증·PR 준비. |
| 5 | 도구별 진입 방식(AGENTS / CLAUDE / .codex / .claude)은 존중하되 **결과 품질 게이트는 동일**. |
| 6 | C++ legacy 자산은 보존, 무수정 (Golden Rule G7). 신규 개발은 모두 Python. |

## 2. 시스템 다이어그램

```
                          ┌──────────────────────────────┐
                          │   Human reviewer / approver  │
                          │  (승인·고위험·프로덕션 결정)  │
                          └──────────────┬───────────────┘
                                         │ approves / requests changes
              ┌──────────────────────────┴──────────────────────────┐
              │                                                     │
   ┌──────────▼──────────┐                              ┌───────────▼─────────┐
   │   Codex CLI Adapter │                              │ Claude Code Adapter │
   │                     │                              │                     │
   │  AGENTS.md (entry)  │                              │  CLAUDE.md (entry)  │
   │  .codex/config*.toml│                              │  .claude/skills/    │
   │  .codex/README      │                              │  .claude/hooks/     │
   │                     │                              │                     │
   │  approval / sandbox │                              │  skills / hooks /   │
   │  / worktree control │                              │  permissions        │
   └──────────┬──────────┘                              └───────────┬─────────┘
              │                                                     │
              │     ┌───────────────────────────────────────┐       │
              └────►│         Shared Harness Core           │◄──────┘
                    │                                       │
                    │  docs/                                │
                    │   ├─ README.md         (entry index)  │
                    │   ├─ plan/             (대관 31주)    │
                    │   ├─ design-docs/      (왜 — ADR)     │
                    │   ├─ product-specs/    (무엇)         │
                    │   ├─ exec-plans/       (active/done)  │
                    │   ├─ references/       (build/arch)   │
                    │   ├─ sop/              (codex/claude/ │
                    │   │                    human/worktree │
                    │   │                    /compat)       │
                    │   ├─ generated/        (자동생성)     │
                    │   └─ {golden-rules, autonomy-levels,  │
                    │       drift-control, failure-modes,   │
                    │       observability, security,        │
                    │       reliability, quality-score,     │
                    │       roadmap-31w, index-of-deliv.}.md│
                    │                                       │
                    │  scripts/                             │
                    │   ├─ verify-all.sh   (게이트 진입점)  │
                    │   ├─ lint.sh          (ruff)          │
                    │   ├─ type-check.sh    (mypy strict)   │
                    │   ├─ structure-check.sh               │
                    │   ├─ docs-freshness.sh                │
                    │   ├─ run-tests.sh     (uv run pytest) │
                    │   ├─ compat-check.sh  (G14)           │
                    │   ├─ bench.sh         (perf)          │
                    │   ├─ changed-files.sh                 │
                    │   └─ check-adapter-sync.sh            │
                    │                                       │
                    │  Repository                           │
                    │   ├─ src/sourcetrail_remake/  (Python │
                    │   │   ├─ cli/  core/  db/  indexer/   │
                    │   │   ├─ refactor/ search/ ui/ )      │
                    │   ├─ tests/{unit,integration,ui,      │
                    │   │           compatibility,perf,fix.}│
                    │   ├─ poc/              (Phase 0 only) │
                    │   └─ src/lib*/, CMakeLists.txt ...    │
                    │       ── C++ legacy (read-only)       │
                    │                                       │
                    │  observability                        │
                    │   %APPDATA%/Sourcetrail_Remake/logs/  │
                    │   docs/generated/{test-runs,bench}/   │
                    └──────────────────┬────────────────────┘
                                       │ exit code 0 / non-zero
                    ┌──────────────────▼──────────────────┐
                    │   CI / Quality gates                │
                    │   ├─ .github/workflows/             │
                    │   │   harness-gate.yml (lint/type/  │
                    │   │     struct/docs/adapter/size)   │
                    │   │   ci.yml          (Phase 0 D2)  │
                    │   ├─ (legacy) .travis.yml           │
                    │   └─ (legacy) appveyor.yml          │
                    └──────────────────┬──────────────────┘
                                       │ green → reviewable
                    ┌──────────────────▼──────────────────┐
                    │   PR review loop  → merge gate      │
                    │   → cleanup / drift-control jobs    │
                    └─────────────────────────────────────┘
```

## 3. 요소별 역할 / 입력 / 출력

| 요소 | 역할 | 입력 | 출력 |
|---|---|---|---|
| **Human reviewer** | 승인·예외·고위험 결정. | PR, 에스컬레이션. | approve / request changes / reject. |
| **Codex CLI Adapter** | Codex 진입. `AGENTS.md` SOP 안내, `.codex/config.toml` 권한·샌드박스 강제. | 사용자 task. | shell action / patch / PR. |
| **Claude Code Adapter** | Claude 진입. `CLAUDE.md` 안내, `.claude/skills/` 절차 자동화, `.claude/hooks/` 게이트 강제. | 사용자 task. | tool calls / patch / PR. |
| **Shared Harness Core** | 양쪽이 공유하는 단일 진실 원천. | 어댑터 호출. | 정책 문서, 스크립트 exit code, 검증 결과. |
| **docs/** | 결정·계획·규칙의 기록 시스템. | 사람·에이전트 편집. | 두 어댑터 모두 읽음. |
| **docs/plan/** | 31주 대관 계획. | 사람만 편집(ADR 필요). | 모든 phase plan의 출발점. |
| **scripts/** | 기계 검증 진입점. **권고를 게이트로 바꿈.** | 변경된 파일, 리포 상태. | exit 0 / non-zero. |
| **Repository (Python)** | `src/sourcetrail_remake/` + `tests/` + `poc/`. | 에이전트 편집. | 빌드/테스트 대상. |
| **Repository (C++ legacy)** | `src/lib*/`, `CMakeLists.txt` 등. | (수정 금지) | 참조용. |
| **observability** | Python 앱/인덱서 로그 + pytest/bench 산출물. | 앱·테스트 실행. | 에이전트 grep 가능. |
| **CI / quality gates** | 동일 게이트를 PR에서 강제. | PR 이벤트. | 머지 가능 여부. |
| **PR review loop** | 자기 리뷰 → (선택) 다른 에이전트 리뷰 → 사람 리뷰. | PR. | 머지 또는 수정. |
| **cleanup / drift jobs** | 정기 점검(`docs/drift-control.md`). | 시간 트리거. | cleanup PR / 부채 트래커 갱신. |

## 4. 어댑터 ↔ 코어 책임 분리

| 결정 사항 | 어디에 둔다 |
|---|---|
| "무엇을 검증하나" (lint/type/구조/테스트/compat 항목) | **공용 코어** (`scripts/`, `docs/references/architecture-rules.md`). |
| "어떻게 호출되나" (Codex sandbox, Claude hook timing) | **어댑터** (`.codex/`, `.claude/`). |
| 빌드·테스트 명령 본문 (uv/pytest) | **공용** (`docs/references/build-and-test.md` 단일 진실). |
| 도구별 자율성 토글 | **어댑터** (Codex approval, Claude settings.json). |
| Golden Rules·Style·Security 정책 | **공용** (`docs/golden-rules.md`, `docs/security.md`). |
| 작업 단위 실행 계획 | **공용** (`docs/exec-plans/active/`). |
| 31주 대관 계획 | **공용** (`docs/plan/`). |
| C++ legacy 보호 | **공용 + 어댑터 양쪽** (G7 + .codex protected paths + Claude hook). |

## 5. 데이터 흐름 (1개 작업 기준)

1. 사용자가 task 부여 → 어댑터 진입(AGENTS.md or CLAUDE.md).
2. `docs/README.md` + `docs/plan/00-overview.md`로 컨텍스트 수집, 해당 phase plan 확인.
3. 1000+ LOC면 `docs/exec-plans/active/_template.md`로 새 plan.
4. 에이전트가 `src/sourcetrail_remake/`만 수정 (C++ legacy는 G7 — 사람 승인).
5. `bash scripts/verify-all.sh` → lint(ruff) / type(mypy) / structure / docs / adapter-sync.
6. 테스트 `bash scripts/run-tests.sh -m <marker>`. DB 영향 시 `bash scripts/compat-check.sh`.
7. 통과 시 PR (`.github/PULL_REQUEST_TEMPLATE.md`).
8. CI가 동일 게이트 재실행.
9. 사람 승인 후 머지. 실행 plan은 `docs/exec-plans/completed/`로 회고와 함께 이동.
10. 정기 cleanup job(`docs/drift-control.md`)이 부채·드리프트 점검.

## 6. 진입점 빠른 링크

- **운영 시작**: `docs/README.md`
- **31주 대관**: `docs/plan/00-overview.md`
- **빌드/테스트 단일 진실**: `docs/references/build-and-test.md`
- **구조 규칙**: `docs/references/architecture-rules.md`
- **Codex SOP**: `docs/sop/codex.md`
- **Claude SOP**: `docs/sop/claude.md`
- **사람 승인 SOP**: `docs/sop/human-approval.md`
- **워크트리 SOP**: `docs/sop/worktree.md`
- **SourcetrailDB 호환 SOP**: `docs/sop/sourcetrail-compat.md`
- **품질 점수**: `docs/quality-score.md`
- **자율성 레벨**: `docs/autonomy-levels.md`
- **드리프트 통제**: `docs/drift-control.md`
- **실패 패턴**: `docs/failure-modes.md`
- **31주 로드맵**: `docs/roadmap-31w.md`
- **산출물 인덱스**: `docs/index-of-deliverables.md`
