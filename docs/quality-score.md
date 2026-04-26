# PR Quality Score

PR이 머지 가능한지 판단하기 위한 **수치 기준**. CI 자동 산출, 사람 리뷰는 점수 임계 미달일 때 게이트.

## 1. 점수 구성 (총 100)

| 카테고리 | 가중치 | 산출 |
|---|---|---|
| Build & test green | 25 | `harness-gate` + `ci` 모두 통과 = 25, 하나라도 실패 = 0. |
| Lint & format | 8 | `scripts/lint.sh` (ruff check + format --check) 통과 = 8. |
| Type check | 7 | `scripts/type-check.sh` (mypy strict) 통과 = 7. |
| Structure rules | 10 | `scripts/structure-check.sh` 통과 = 10. |
| Test coverage delta | 12 | 변경 라인의 80%+ 커버 = 12, 60~79% = 6, <60% = 0. |
| **SourcetrailDB compat** | **15** | DB/스키마 영향 변경 시 `scripts/compat-check.sh` 통과 필수 = 15. 무관 변경이면 자동 만점. |
| PR size | 8 | <300 LOC = 8, 300~1000 = 4, >1000 = 0. |
| Exec-plan linkage | 8 | `docs/exec-plans/active/`에 매칭 plan + 본문 링크 = 8. |
| Self-review checklist | 7 | PR 본문 모든 체크 = 7. |

## 2. 임계

| 점수 | 머지 가능성 |
|---|---|
| ≥ 85 | 자동 머지 가능 (사람 승인은 정책상 필요한 경우만). |
| 70~84 | 사람 1명 승인 필요. |
| 50~69 | 사람 2명 승인 + 회고 노트. |
| < 50 | 머지 차단. PR 분할 또는 보강 후 재제출. |

## 3. 산출 위치

- CI(`.github/workflows/harness-gate.yml`)가 PR 코멘트로 표 출력.
- 동시에 `docs/generated/quality-scores/<pr-number>.md`에 저장 (자동 생성, 30일 보존).

## 4. 점수와 무관하게 막는 것

- **Golden Rules 위반** (`docs/golden-rules.md`) — 점수와 무관하게 머지 차단.
- **시크릿 노출 의심** — 즉시 차단.
- **G7 (C++ legacy) 무단 변경** — `legacy-cpp-touch` 라벨 + 사유 없이 차단.
- **G14 (SourcetrailDB compat) 실패** — 점수 만점이어도 차단.
- **`docs/sop/human-approval.md`가 사람 승인 필수로 지정한 경로 변경** — 사람 승인 없이 절대 머지 불가.

## 5. 부채 점수 연동

`docs/drift-control.md` §4의 `debt_score`가 < 60이면 다음 PR의 quality_score에 -10 페널티 (정리 PR 인센티브).
