# Product Specs

기능·사용자 가치·외부 계약(파일 형식, 명령어, 프로토콜)을 정의한다.
**왜 만드는지**가 아니라 **무엇을 보장하는지**를 기록한다 (왜는 `design-docs/`).

## 등재 규칙

1. 파일명: `<area>-<feature>.md` (예: `indexer-cxx-language-support.md`, `cli-config-command.md`).
2. 외부 계약(명령 인자, 파일 포맷, 네트워크 프로토콜) 변경은 **반드시 여기에 먼저 PR**을 낸 뒤 코드 변경.
3. 폐기 시: `Status: Deprecated`로 표시 후 30일 뒤 `references/archived/`로 이동.

## 인덱스

| Area | Spec | Status | Owner |
|---|---|---|---|
| _(예시)_ indexer | C/C++ 언어 패키지 | Active | core |
| _(예시)_ cli | `Sourcetrail config` 명령 | Active | core |

## 템플릿

````markdown
---
title: <기능 이름>
area: indexer | gui | cli | ide-plugin | storage | …
status: Draft | Active | Deprecated
owner: <git handle 또는 팀>
last_updated: YYYY-MM-DD
---

# 1. Summary

한두 문장 요약.

# 2. User value

이 기능이 누구에게 어떤 가치를 주는가?

# 3. External contract

- **명령 / API / 파일 포맷**:
- **입력**:
- **출력**:
- **에러 모드**:

# 4. Acceptance criteria

- [ ] …
- [ ] …

# 5. Out of scope

명시적으로 제외하는 것.

# 6. Verification

이 기능이 정상 동작함을 보이는 테스트 / 시나리오 경로.
````
