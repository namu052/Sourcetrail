# Tech Debt Tracker

발견된 기술부채를 표 한 장에 모은다. 새 부채는 발견 즉시 추가, 해결되면 `Resolved` 표시 후 30일 뒤 삭제.

## 우선순위 정의

| Severity | 의미 | 대응 |
|---|---|---|
| `S1` | 보안/데이터 손실/빌드 깨짐 위험. | 다음 PR 또는 즉시. |
| `S2` | 자주 부딪히는 마찰. 새 기능 개발 속도를 떨어뜨림. | 분기 내. |
| `S3` | 알아둘 가치는 있으나 당장은 무해. | 백로그. |

## 부채 항목

| ID | Severity | 영역 | 설명 | 발견일 | last_seen | 발견자 | 해결 PR | 상태 |
|---|---|---|---|---|---|---|---|---|
| _(예시)_ TD-001 | S2 | `lib/data/storage` | `IntermediateStorage::merge` 의 nested loop이 큰 프로젝트에서 O(n²) 패턴. | 2026-04-25 | 2026-04-25 | @example | — | Open |

## 운영 규칙

1. **발견 즉시 등재**. 코드만 고치고 부채는 묻어두지 않는다.
2. `last_seen`은 PR 작업 중 부채를 다시 마주칠 때마다 갱신.
3. 해결 PR이 머지되면 `Resolved (PR #123)`으로 상태 변경, 30일 뒤 삭제.
4. 90일 이상 `last_seen` 갱신 없는 항목은 `scripts/docs-freshness.sh`가 경고 → 사람이 판단:
   - 여전히 유효 → `last_seen` 갱신.
   - 더는 무관 → `Stale` 표시 후 삭제.
5. S1은 작성 시 `docs/sop/human-approval.md`에 따라 사람 알림.

## 수치화 (drift-control 참조)

`docs/drift-control.md`의 정기 점검 job이 다음 메트릭을 산출:

- 총 항목 수 (S1/S2/S3별).
- 평균 해결 시간.
- 30일/90일 정체 항목 수.

이 수치는 `docs/quality-score.md`의 입력으로 쓰인다.
