# Design Docs

설계 결정과 트레이드오프 기록. **무엇을** 만들었는지가 아니라 **왜 그렇게** 만들었는지를 남긴다.

## 등재 규칙

1. 파일명: `YYYY-MM-DD-<short-slug>.md` (예: `2026-04-25-indexer-process-isolation.md`).
2. 결정이 바뀌면 새 문서를 추가하고, 기존 문서 상단에 `**Superseded by**: <new path>` 추가. **기존 문서를 수정하지 않는다** (히스토리 보존).
3. 모든 문서는 아래 템플릿을 따른다.

## 인덱스

| 날짜 | 제목 | 상태 | 슈퍼시드 |
|---|---|---|---|
| _(예시)_ 2026-04-25 | indexer 프로세스 격리 결정 | Active | — |

> 새 문서를 만들 때 이 표 위에 한 줄 추가.

## 템플릿

````markdown
---
title: <짧은 결정 제목>
status: Draft | Active | Superseded
owner: <git handle 또는 팀>
last_updated: YYYY-MM-DD
supersedes: <이전 문서 경로 또는 비움>
---

# 1. Context

이 결정이 필요한 배경. 어떤 문제를 풀려는가? 어떤 제약이 있는가?

# 2. Decision

선택한 방향을 한 문단으로.

# 3. Considered alternatives

| 대안 | 장점 | 단점 | 채택 여부 |
|---|---|---|---|
| A | … | … | ✅ |
| B | … | … | ❌ |

# 4. Consequences

- **긍정**: …
- **부정**: …
- **추적 필요**: (있으면 `exec-plans/tech-debt-tracker.md`에도 등재)

# 5. References

- 관련 코드 경로 (e.g. `src/lib/data/storage/PersistentStorage.cpp`).
- 관련 product-spec / exec-plan 링크.
````
