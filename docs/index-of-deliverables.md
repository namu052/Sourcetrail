---
title: 공용 하네스 산출물 인덱스 (v1 — Python)
status: Active
owner: maintainer
last_updated: 2026-04-25
---

# Index of Deliverables (v1, Python)

본 하네스가 만든 모든 자산. `scripts/check-adapter-sync.sh`가 이 표의 1열 경로 존재 여부를 검사한다.

> v0(C++ 전제)는 `docs/exec-plans/completed/2026-04-25-harness-bootstrap.md` 참조.

## 어댑터 (얇음)

| 경로 | 용도 | SoT? | 관리 |
|---|---|---|---|
| `AGENTS.md` | Codex 진입 허브 | ❌ (링크) | 사람 |
| `CLAUDE.md` | Claude 진입 허브 | ❌ (링크) | 사람 |
| `.codex/README.md` | Codex 프로파일 가이드 | ✅ | 공용 |
| `.codex/config.toml` | 균형 (L2, 기본) | ✅ | 사람 |
| `.codex/config.balanced.toml` | 균형 명시 사본 | ✅ | 사람 |
| `.codex/config.conservative.toml` | 보수 (L1) | ✅ | 사람 |
| `.codex/config.semi-autonomous.toml` | 반자율 (L3) | ✅ | 사람 |
| `.claude/skills/explore-codebase/SKILL.md` | 모듈맵 탐색 (Python + C++ legacy 격리) | ✅ | 공용 |
| `.claude/skills/create-exec-plan/SKILL.md` | exec-plan 작성 (phase 필드) | ✅ | 공용 |
| `.claude/skills/run-verification/SKILL.md` | 검증 게이트 호출 (uv 도구) | ✅ | 공용 |
| `.claude/skills/prepare-pr/SKILL.md` | PR 준비 (Compat 포함) | ✅ | 공용 |
| `.claude/hooks/README.md` | hook 초안 (uv/G7/G13 차단) | ✅ | 사람 (적용 승인) |

## 공용 코어 — 아키텍처 / 인덱스

| 경로 | 용도 | SoT? | 관리 |
|---|---|---|---|
| `ARCHITECTURE.md` | 다이어그램 + 어댑터 ↔ 코어 책임 (Python primary + C++ legacy) | ✅ | 공용 |
| `docs/README.md` | docs 트리 인덱스 | ✅ | 공용 |
| `docs/index-of-deliverables.md` | 본 인덱스 | ✅ | 공용 |

## 공용 코어 — 대관 계획 (`docs/plan/`)

| 경로 | 용도 | SoT? | 관리 |
|---|---|---|---|
| `docs/plan/README.md` | plan 트리 가이드 | ✅ | 공용 |
| `docs/plan/00-overview.md` | 8개 확정 사항 + 31주 일정 | ✅ | 사람 (ADR 필요) |
| `docs/plan/01-requirements.md` | 27개 기능 + 비기능 요구사항 | ✅ | 사람 |
| `docs/plan/02-architecture.md` | 기술 스택, 모듈, SourcetrailDB 호환 | ✅ | 사람 |
| `docs/plan/03-risks.md` | 19개 리스크 + G1~G6 게이트 | ✅ | 사람 |
| `docs/plan/phase-0-setup.md` | Phase 0 (W1~2) | ✅ | 사람 |
| `docs/plan/phase-1-mvp-indexer-graph.md` | Phase 1 (W3~8) | ✅ | 사람 |
| `docs/plan/phase-2-context-panels.md` | Phase 2 (W9~16) | ✅ | 사람 |
| `docs/plan/phase-3-editor-features.md` | Phase 3 (W17~22) | ✅ | 사람 |
| `docs/plan/phase-4-python-specific.md` | Phase 4 (W23~28) | ✅ | 사람 |
| `docs/plan/phase-5-packaging.md` | Phase 5 (W29~31) | ✅ | 사람 |
| `docs/plan/phase-6-testing-docs.md` | Phase 6 (지속) | ✅ | 사람 |

## 공용 코어 — 기록 시스템

| 경로 | 용도 | SoT? | 관리 |
|---|---|---|---|
| `docs/design-docs/index.md` | 설계 결정 (ADR) + 템플릿 | ✅ | 공용 |
| `docs/product-specs/index.md` | 제품 스펙 + 템플릿 | ✅ | 사람 |
| `docs/exec-plans/active/_template.md` | 진행 중 plan 템플릿 (phase 필드 포함) | ✅ | 공용 |
| `docs/exec-plans/active/2026-04-25-harness-pivot-to-python.md` | 본 작업 자체 plan | 진행 중 | 공용 |
| `docs/exec-plans/completed/_template.md` | 완료 plan 회고 템플릿 | ✅ | 공용 |
| `docs/exec-plans/completed/2026-04-25-harness-bootstrap.md` | v0 (C++ 전제) 산출물 회고 | 보존 | 공용 |
| `docs/exec-plans/tech-debt-tracker.md` | 부채 등재 | ✅ | 공용 |

## 공용 코어 — 정책 / 참조

| 경로 | 용도 | SoT? | 관리 |
|---|---|---|---|
| `docs/references/build-and-test.md` | uv/pytest/ruff/mypy 단일 진실 + C++ legacy §7 | ✅ | 공용 |
| `docs/references/architecture-rules.md` | UI→App→Domain→Infra + C++ legacy 격리 | ✅ | 공용 |
| `docs/golden-rules.md` | G1~G15 (G7 legacy, G13 uv, G14 compat 포함) | ✅ | 사람 |
| `docs/quality-score.md` | PR 점수 100 (Compat 15점 포함) | ✅ | 공용 |
| `docs/security.md` | Windows 특화 (서명/Defender) | ✅ | 사람 |
| `docs/reliability.md` | G1~G6 + 번아웃 정책 | ✅ | 사람 |
| `docs/observability.md` | %APPDATA% 로그 + Python 시나리오 10개 | ✅ | 공용 |
| `docs/autonomy-levels.md` | L1/L2/L3 (uv 명령 기준) | ✅ | 사람 |
| `docs/drift-control.md` | 정기 점검 + cleanup + Compat 회귀 | ✅ | 공용 |
| `docs/failure-modes.md` | 15개 패턴 (Jedi/PyQt/uv.lock 등) | ✅ | 공용 |
| `docs/roadmap-31w.md` | 31주 로드맵 (`plan/`과 정합) | 시한부 (31주) | 사람 |
| `docs/sop/codex.md` | Codex SOP (uv 도구) | ✅ | 공용 |
| `docs/sop/claude.md` | Claude SOP (uv 도구) | ✅ | 공용 |
| `docs/sop/human-approval.md` | 사람 승인 SOP (보호 경로 갱신) | ✅ | 사람 |
| `docs/sop/worktree.md` | 워크트리 SOP (uv-local .venv) | ✅ | 공용 |
| `docs/sop/sourcetrail-compat.md` | SourcetrailDB 100% 호환 SOP (G14) | ✅ | 사람 |

## 공용 코어 — 검증 스크립트

| 경로 | 용도 | SoT? | 관리 |
|---|---|---|---|
| `scripts/verify-all.sh` | 게이트 진입점 (lint/type/struct/docs/adapter) | ✅ | 공용 |
| `scripts/lint.sh` | ruff check + format --check | ✅ | 공용 |
| `scripts/type-check.sh` | mypy strict (NEW) | ✅ | 공용 |
| `scripts/structure-check.sh` | Python import + 보호 경로 + secrets + legacy | ✅ | 공용 |
| `scripts/docs-freshness.sh` | exec-plans 정체 + pyproject/uv.lock/plan 정합 | ✅ | 공용 |
| `scripts/run-tests.sh` | uv run pytest 래퍼 | ✅ | 공용 |
| `scripts/compat-check.sh` | SourcetrailDB 호환 (NEW, Phase 0 D8 placeholder) | ✅ | 공용 |
| `scripts/bench.sh` | pytest-benchmark (NEW) | ✅ | 공용 |
| `scripts/changed-files.sh` | 변경 파일 헬퍼 (언어 중립) | ✅ | 공용 |
| `scripts/check-adapter-sync.sh` | 어댑터 ↔ 어댑터 ↔ 인덱스 동기 + deprecated C++ 명령 검사 | ✅ | 공용 |

## CI

| 경로 | 용도 | SoT? | 관리 |
|---|---|---|---|
| `.github/workflows/harness-gate.yml` | PR 게이트 (uv setup + 5개 게이트 + size/legacy 라벨) | ✅ | 사람 |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR 본문 템플릿 (Compat + G7 체크) | ✅ | 공용 |
| `.github/CODEOWNERS` | 사람 승인 매핑 (Python + C++ legacy 양쪽) | ✅ | 사람 |

## C++ Legacy (보존, 수정 금지 — G7)

기존 Sourcetrail 자산은 본 하네스가 건드리지 않는다:

| 경로 | 비고 |
|---|---|
| `script/` | C++ Sourcetrail 빌드 wrapper |
| `src/lib*/`, `src/app/`, `src/indexer/`, `src/external/`, `src/test/` | C++ 생산 코드 |
| `cmake/`, `CMakeLists.txt` | C++ 빌드 시스템 |
| `.clang-format` | C++ 스타일 |
| `.travis.yml`, `appveyor.yml` | 기존 CI |
| `java_indexer/`, `ide_plugins/`, `bin/`, `setup/`, `deployment/`, `testing/` | C++ 런타임/배포 |
| `docs/documentation/`, `docs/readme/` | 원본 Sourcetrail 사용자 문서 |
| `README.md`, `DOCUMENTATION.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SPONSORS.md`, `AUTHORS.txt`, `LICENSE.txt` | 원본 메타 |

## 카운트

- 어댑터: 12
- 공용 코어 — 아키텍처/인덱스: 3
- 공용 코어 — 대관 계획 (`docs/plan/`): 12
- 공용 코어 — 기록 시스템: 7
- 공용 코어 — 정책/참조: 16
- 공용 코어 — 검증 스크립트: 10
- CI: 3
- **합계: 63 산출물** (v1)
