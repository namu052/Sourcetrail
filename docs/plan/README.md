---
title: Sourcetrail_Remake 구현 계획 (대관)
status: Active
owner: maintainer
last_updated: 2026-04-25
---

# docs/plan/ — 대관적 구현 계획

이 디렉터리는 **Sourcetrail_Remake (Python desktop app, 31주)**의 대관적 계획을 담는다.
출처: `.claude/worktrees/elastic-lamport-8f3120/docs/plan/`에서 본 디렉터리로 이전 (2026-04-25). worktree 사본은 archive로 유지.

## 위치 정책

| 종류 | 위치 |
|---|---|
| **대관 계획** (이 파일들) | `docs/plan/` — 변경 빈도 낮음, 단일 진실 원천 |
| **실행 단위 plan** (phase별 작업 wbs, 일일 작업) | `docs/exec-plans/active/` — 진행 중인 것만 |
| **회고** | `docs/exec-plans/completed/` — 머지 후 |
| **부채 등재** | `docs/exec-plans/tech-debt-tracker.md` |

## 읽기 순서

| 독자 | 권장 순서 |
|---|---|
| Skim (5분) | [`00-overview.md`](00-overview.md) → 각 phase 제목만 |
| 기술 검토 (30분) | `00` → [`02-architecture.md`](02-architecture.md) → [`03-risks.md`](03-risks.md) |
| 기능 이해 (20분) | `00` → [`01-requirements.md`](01-requirements.md) |
| Phase 착수자 | `00` → 해당 phase → `02-architecture` |

## 인덱스

### 횡단 문서 (4개)

| 파일 | 내용 |
|---|---|
| [`00-overview.md`](00-overview.md) | 8개 확정 사항, 31주 일정, 마일스톤 |
| [`01-requirements.md`](01-requirements.md) | 27개 기능 (P0~P5), 비기능 요구사항, 의도적 제외 |
| [`02-architecture.md`](02-architecture.md) | 기술 스택, 모듈 구조(Python), 레이어 다이어그램, SourcetrailDB 100% 호환 전략 |
| [`03-risks.md`](03-risks.md) | 19개 리스크 (4 critical), G1~G6 게이트 |

### Phase별 (7개)

| Phase | 기간 | 누적 | 마일스톤 | 파일 |
|---|---|---|---|---|
| **Phase 0** | 2주 (W1~2) | 2주 | M0 Foundation | [`phase-0-setup.md`](phase-0-setup.md) |
| **Phase 1** | 6주 (W3~8) | 8주 | M1 Image Parity (Alpha) | [`phase-1-mvp-indexer-graph.md`](phase-1-mvp-indexer-graph.md) |
| **Phase 2** | 8주 (W9~16) | **16주 (MVP)** | M2 MVP (Beta) | [`phase-2-context-panels.md`](phase-2-context-panels.md) |
| **Phase 3** | 6주 (W17~22) | 22주 | M3 Productivity | [`phase-3-editor-features.md`](phase-3-editor-features.md) |
| **Phase 4** | 6주 (W23~28) | 28주 | M4 Differentiation (RC) | [`phase-4-python-specific.md`](phase-4-python-specific.md) |
| **Phase 5** | 3주 (W29~31) | **31주 (v1.0)** | M5 v1.0.0 | [`phase-5-packaging.md`](phase-5-packaging.md) |
| **Phase 6** | 지속 | — | — | [`phase-6-testing-docs.md`](phase-6-testing-docs.md) |

## 본 계획과 하네스의 관계

본 계획의 정책·검증 항목은 하네스(`docs/`, `scripts/`, `.codex/`, `.claude/`, `.github/`)에 다음처럼 매핑된다:

| 계획 항목 | 하네스 |
|---|---|
| 27개 기능, 우선순위 | `docs/exec-plans/active/`의 phase별 plan에 매핑 |
| Python 스택, 레이어 | `docs/references/{build-and-test,architecture-rules}.md` |
| SourcetrailDB 호환 | `docs/sop/sourcetrail-compat.md`, `scripts/compat-check.sh` |
| 19개 리스크 + G1~G6 게이트 | `docs/roadmap-31w.md`, `docs/failure-modes.md` |
| 80% 커버리지 | `docs/quality-score.md`, `scripts/run-tests.sh` |
| Windows-only | `docs/security.md`(서명/Defender), `.github/workflows/` |
| 1인 풀타임 번아웃 (R-03) | `docs/reliability.md` |

## 변경 절차

이 디렉터리의 파일은 **머지 빈도가 낮은 대관 계획**이다. 변경 시:

1. `docs/sop/human-approval.md` 절차에 따라 maintainer 승인.
2. 변경 사유를 `docs/design-docs/`에 ADR로 기록.
3. 영향 받는 phase의 `docs/exec-plans/active/`도 함께 갱신.
