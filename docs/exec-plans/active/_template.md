---
title: <작업 한 줄 제목>
status: In Progress
owner: <git handle>
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
related_specs: [docs/product-specs/<file>.md]
related_designs: [docs/design-docs/<file>.md]
autonomy_level: L1 | L2 | L3   # docs/autonomy-levels.md 참조
---

# 1. Context

왜 이 작업을 지금 하는가? 어떤 사용자/시스템 문제를 푸는가?
3~6 문장.

# 2. Goal

완료 시 무엇이 달라지는가? **검증 가능한 표현**으로.

# 3. Non-goals

명시적으로 하지 않는 것.

# 4. Approach

큰 단계 3~7개. 각 단계는 검증 가능한 산출물 1개와 매칭.

| # | 단계 | 산출물 | 검증 방법 |
|---|---|---|---|
| 1 | … | … | … |
| 2 | … | … | … |

# 5. Critical files

수정/생성할 파일 경로 (변동 시 갱신).

# 6. Reused existing assets

재사용하는 기존 함수·스크립트·문서 경로.

# 7. Risks & mitigations

| 위험 | 영향 | 완화책 |
|---|---|---|
| … | … | … |

# 8. Verification

- [ ] `bash scripts/verify-all.sh` 통과
- [ ] (해당 시) UI/E2E 시나리오 경로
- [ ] (해당 시) 회귀 테스트 추가 위치

# 9. Rollback plan

문제 발생 시 되돌리는 방법 (git revert 외 추가 정리 필요한지).

# 10. Status log

| 날짜 | 변경 |
|---|---|
| YYYY-MM-DD | created |
