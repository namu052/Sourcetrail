# docs/ — 공용 하네스 기록 시스템

이 트리는 **Codex CLI와 Claude Code가 함께 읽는 단일 진실 원천**이다.
도구별 어댑터(`AGENTS.md`, `CLAUDE.md`)는 짧은 진입 + 링크만 제공하고, 실질 정책은 모두 여기에 있다.

> 우선순위: 에이전트는 새 작업을 시작할 때 **위에서 아래** 순서로 읽는다.

## 1. 우선순위 (작업 시작 시 읽는 순서)

| 순위 | 디렉터리 / 파일 | 왜 |
|---|---|---|
| 1 | [`exec-plans/active/`](exec-plans/active/) | 지금 진행 중인 작업 컨텍스트. 다른 무엇보다 먼저 본다. |
| 2 | [`plan/00-overview.md`](plan/00-overview.md) | 31주 대관 계획 + 8개 확정 사항 (Sourcetrail_Remake Python 프로젝트 정체성). |
| 3 | [`product-specs/index.md`](product-specs/index.md) | 무엇을 만드는지 (요구사항·계약). |
| 4 | [`design-docs/index.md`](design-docs/index.md) | 왜 그렇게 설계했는지 (결정·트레이드오프, ADR). |
| 5 | [`references/build-and-test.md`](references/build-and-test.md) | uv/pytest/ruff/mypy 단일 진실 원천. |
| 6 | [`references/architecture-rules.md`](references/architecture-rules.md) | UI→App→Domain→Infra + C++ legacy 격리. |
| 7 | [`sop/`](sop/) | 도구별·운영 SOP (codex/claude/human-approval/worktree/sourcetrail-compat). |

## 2. 디렉터리 지도

| 경로 | 목적 | source of truth | 관리 주체 | 신선도 규칙 | 폐기 기준 |
|---|---|---|---|---|---|
| `plan/` | 31주 대관 계획 (00-overview, 01-requirements, 02-architecture, 03-risks, phase-0~6). | ✅ | 사람 (변경은 ADR + maintainer 승인). | phase 종료 시 진척 갱신. | 12개월 이상 미참조 시 `references/archived/`로. |
| `design-docs/` | 설계 결정·트레이드오프 기록 (ADR). | ✅ | 사람 + 공용 에이전트. | 결정이 바뀌면 새 문서를 추가(기존 수정 금지, "Superseded by"로 링크). | 90일 이상 참조 0회 + Superseded 표시되면 `references/archived/`로 이동. |
| `product-specs/` | 외부에 보이는 요구사항·계약. | ✅ | 사람. | 스펙 변경 시 PR로 갱신, 구버전은 git 히스토리에 남김. | 기능이 폐기되면 `Status: Deprecated`로 표시 후 30일 뒤 이동. |
| `exec-plans/active/` | 진행 중 작업 단위 실행 계획. | ✅ (작업 동안) | 작업 담당 에이전트. | 30일 정체 시 `scripts/docs-freshness.sh`가 경고. | 머지 시 `completed/`로 이동. 7일 내 미머지 + 무활동이면 `cancelled/`로 이동(별도 폴더 필요 시). |
| `exec-plans/completed/` | 완료된 작업 회고·학습. | 참고용. | 작업 담당 에이전트. | 변경 금지 (역사 보존). | 1년 이상은 `completed/archive/`로 이동 가능. |
| `exec-plans/tech-debt-tracker.md` | 기술부채 등재. | ✅ | 모든 에이전트가 발견 즉시 추가, 사람이 우선순위. | 항목별 `last_seen` 갱신. | 해결 PR 머지 시 `Resolved` 표시 후 30일 뒤 삭제. |
| `references/` | 빌드·테스트·아키텍처 등 안정적 사실. | ✅ | 공용 에이전트. | 의존성 버전 변경 시 즉시 갱신. | 기술 스택에서 빠지면 즉시 삭제. |
| `sop/` | 운영 절차. | ✅ | 사람 + 공용 에이전트. | 운영 사고/회고 후 갱신. | 절차가 폐기되면 즉시 삭제. |
| `generated/` | 자동 생성 문서 (테스트 커버리지 리포트, 의존 그래프 등). | ❌ (생성 결과) | 자동화 (`scripts/`). | 매 PR / nightly 재생성. | 30일 지난 산출물은 자동 삭제. |
| `golden-rules.md` | 절대 위반 금지 규칙. | ✅ | 사람 승인 필수. | 분기 1회 검토. | 폐기 금지 (대체 문서 발행 후 삭제). |
| `quality-score.md` | PR 품질 점수 정의. | ✅ | 공용 에이전트. | 게이트 변경 시 즉시 갱신. | — |
| `security.md`, `reliability.md` | 운영 정책. | ✅ | 사람 + 보안 담당. | 사고 후 즉시 갱신. | — |
| `observability.md` | 로그/메트릭/트레이스 흐름. | ✅ | 공용 에이전트. | 로그 포맷 변경 시 갱신. | — |
| `autonomy-levels.md` | L1/L2/L3 자율성 정의. | ✅ | 사람. | 정책 변경 시. | — |
| `drift-control.md` | 정기 점검 / cleanup 분류. | ✅ | 공용 에이전트. | 분기 1회. | — |
| `failure-modes.md` | 흔한 실패 패턴 카탈로그. | ✅ | 공용 에이전트. | 새 사고 발생 시 항목 추가. | — |
| `roadmap-12w.md` | 12주 구축 로드맵. | 시한부 (12주). | 사람. | 주차별 갱신. | 12주 종료 후 `completed/`로 이동. |
| `index-of-deliverables.md` | 하네스 산출물 인덱스. | ✅ | 공용 에이전트. | 신규/삭제 산출물마다. | — |

## 3. 신선도 (자동 검사)

`scripts/docs-freshness.sh`가 다음을 검사:

- `exec-plans/active/*.md`의 `last_updated` 필드가 30일 이상 정체 → 경고.
- `exec-plans/active/`에 머지된 PR과 매칭되는 plan이 남아 있으면 → 경고.
- `references/*.md`에서 참조하는 외부 버전(예: Clang 11)과 `CMakeLists.txt`가 어긋나면 → 경고.

## 4. 등재 규칙

- 모든 문서는 frontmatter(`status`, `owner`, `last_updated`)를 포함한다.
- 새 디렉터리를 만들기 전 이 README의 "디렉터리 지도"에 등재한다.
- AGENTS.md / CLAUDE.md에 정책 본문을 복붙하지 않는다 — **여기를 가리키게 한다**.

## 5. Sourcetrail 기존 자산과의 관계

기존 `docs/documentation/`, `docs/readme/`(원본 Sourcetrail 사용자 문서)는 **수정·이동 금지**.
하네스 문서는 `docs/` 직속 또는 위에 나열한 신규 하위 폴더에만 추가한다.
