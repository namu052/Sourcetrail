---
name: create-exec-plan
description: docs/exec-plans/active/_template.md 기반으로 작업 단위 실행 계획을 작성한다. 1000+ LOC 변경 또는 phase 작업에 필수.
---

# Skill: create-exec-plan

## When to use

- 1000+ LOC 변경.
- 둘 이상 모듈에 영향.
- 외부 의존성 추가 (`uv add`) / 빌드 옵션 변경.
- 사람 승인이 필요한 모든 작업 (`docs/sop/human-approval.md` §1).
- 새 phase 착수 (`docs/plan/phase-N-*.md`의 일일 작업 분해).

## Procedure

1. 슬러그 정하기: `<area>-<verb>-<short>` (예: `db-add-extension-tables`, `indexer-jedi-resolver-mvp`).
2. 파일 생성: `docs/exec-plans/active/YYYY-MM-DD-<slug>.md`.
3. [`_template.md`](../../../docs/exec-plans/active/_template.md) 복사 후 채움.
4. **§4 Approach 표는 검증 가능한 단위로**. 단계당 산출물 1개 + 검증 방법 1개.
5. **§5 Critical files**는 `explore-codebase` 스킬 결과 그대로 (Python 모듈맵 기준).
6. **§6 Reused assets**는 `core/`, 기존 모듈, `scripts/`, `docs/plan/`을 우선 참고.
7. **§9 Rollback plan**이 비어 있으면 plan 미완. 단순 `git revert`로 충분한지 확인.

## Frontmatter 필수

```yaml
---
title: <한 줄>
status: In Progress
owner: <git handle>
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
related_specs: [docs/plan/01-requirements.md, docs/product-specs/<file>.md]
related_designs: [docs/plan/02-architecture.md, docs/design-docs/<file>.md]
autonomy_level: L1 | L2 | L3
phase: pre-Phase-0 | Phase-0 | Phase-1 | ... | Phase-6 | cross-phase
---
```

`phase` 필드는 `docs/roadmap-31w.md`와 매칭. 어느 phase에도 속하지 않으면 `cross-phase`.

## 머지 후

- 머지된 PR과 매칭되는 plan은 다음 PR에서 `docs/exec-plans/completed/`로 이동.
- `_template.md`(completed)에 따라 회고 작성: outcome / shipped / verification done / lessons.

## Anti-patterns

- "TBD"로 가득 찬 plan 머지. → `docs/docs-freshness.sh`가 30일 정체로 경고.
- 한 plan이 여러 PR로 늘어남. → 작은 PR 원칙 위반. plan을 분할.
- `docs/plan/`의 대관 계획을 plan으로 복붙. → 대관은 SoT, 실행 plan은 일일 작업 단위.
- `phase` frontmatter 누락. → roadmap 추적 불가.

## Verification

- 본 스킬 실행 결과 plan 파일 1개가 `active/`에 생성된다.
- 파일이 `bash scripts/docs-freshness.sh`를 통과한다.
- `phase` 값이 `docs/roadmap-31w.md`의 phase 표 중 하나와 일치한다.
