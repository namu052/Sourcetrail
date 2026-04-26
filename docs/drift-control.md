# Drift Control

공용 하네스 + Sourcetrail_Remake 코드베이스가 시간이 지나며 무너지지 않게. SoT는 **검사 가능한 신호**.

## 1. 정기 점검 job

| 주기 | Job | 산출물 |
|---|---|---|
| 매 PR | `verify-all.sh`, `harness-gate.yml`, `ci.yml` (Phase 0+) | exit code |
| 일간 (TBD) | `docs-freshness.sh` 풀 스윕 + `tech-debt-tracker.md` `last_seen` 자동 갱신 | 경고 리포트 |
| 주간 (TBD) | `check-adapter-sync.sh` + 부채 요약 + bench 회귀 추적 | `docs/generated/drift/<date>.md` |
| 매 phase 종료 | `compat-check.sh` 풀 (모든 fixture) + 회고 문서 | `docs/exec-plans/completed/<phase>-retro.md` |
| 분기 | golden-rules / security / autonomy 정책 사람 검토 | 머지된 PR (없으면 그 자체가 신호) |

## 2. Drift 감지 규칙

| 신호 | 임계 | 자동 조치 |
|---|---|---|
| `exec-plans/active/` 정체 | 30일 | docs-freshness 경고 |
| `exec-plans/active/`에 머지된 PR과 매칭 plan 잔존 | — | docs-freshness 경고 |
| AGENTS.md ↔ CLAUDE.md Harness Entry 첫 링크 불일치 | — | `check-adapter-sync.sh` fail |
| `pyproject.toml` ↔ `docs/references/build-and-test.md` 버전 어긋남 | — | docs-freshness 경고 |
| `pyproject.toml` 있는데 `uv.lock` 없음 | — | docs-freshness 경고 |
| `.codex/config.*.toml`에 deprecated C++ 명령 잔존 | — | `check-adapter-sync.sh` fail |
| `# LOCAL HELPER:` 주석 + 비슷한 utility가 `core/`에 존재 | 발견 즉시 | structure-check warn |
| 부채 트래커 항목 90일 정체 | 90일 | docs-freshness 경고 |
| 보호 경로가 사람 승인 없이 변경된 흔적 | 발견 즉시 | CODEOWNERS + structure-check warn |
| `compat-check.sh` 호환성 실패 | 매 phase 종료 시 | **PR 차단** (G14) |
| Bench 결과 회귀 (이전 대비 +20%) | PR | warn → 상위 +50%면 fail |
| C++ legacy 무단 변경 (`legacy-cpp-touch` 라벨 없이) | 발견 즉시 | structure-check warn (실수 의심), CODEOWNERS 차단 |

## 3. Cleanup PR 분류

| 종류 | 자동 머지 가능? | 트리거 |
|---|---|---|
| `format` (ruff format 적용) | ❌ (사람 검토) | lint warn |
| `docs/exec-plans/active → completed/ 이동` | ✅ (label `safe-cleanup`) | 머지된 PR 매칭 |
| `dead code 제거` | ❌ (사람 검토) | 정기 스윕 |
| `tech-debt-tracker.md`의 Resolved 30일 경과 항목 삭제 | ✅ | 일간 job |
| `docs/generated/` 30일 경과 산출물 삭제 | ✅ | 일간 job |
| `uv.lock` minor 업데이트 (보안 취약점 없는 patch) | ❌ (수동 검토 권장) | dependabot 또는 주간 |
| Golden rule / security / sop / docs/plan 변경 | ❌ (사람 승인 + RULE_OVERRIDE) | 수동 |

## 4. 부채 수치화 공식

`docs/quality-score.md`의 입력으로 들어가는 부채 점수:

```
debt_score = 100
            - 5  * count(S1)
            - 2  * count(S2)
            - 0.5 * count(S3)
            - 1  * count(S2 with last_seen > 90d)
            - 3  * count(S1 with last_seen > 30d)
            - 5  * count(compat_check_failure_within_phase)
            - 2  * count(perf_regression_within_phase)
```

- 80 이상: 건강.
- 60~79: 주의 (분기 회고).
- < 60: 정리 sprint 필요 (사람 결정).

## 5. 도구별 분기 드리프트

| 신호 | 검사 |
|---|---|
| AGENTS.md만 갱신, CLAUDE.md 미갱신 | `check-adapter-sync.sh` |
| `.codex/config.toml` ↔ `.codex/config.balanced.toml` 불일치 | `check-adapter-sync.sh` (warn) |
| `.claude/skills/` 추가됐는데 `docs/sop/claude.md` 미언급 | 사람 검토 (정기 스윕) |
| `.codex/config.*.toml`에 cmake/ninja/script-buildonly 잔존 | `check-adapter-sync.sh` fail |

## 6. 운영 책임

- 일간/주간 job 결과는 `docs/generated/drift/`에 저장 (30일 보존).
- 임계 초과 신호는 `tech-debt-tracker.md`에 자동 등재 (Phase 1+에 자동화 PR로).
- 분기마다 `docs/exec-plans/active/`에 "drift-cleanup-Q<n>.md" plan을 maintainer가 작성.
- 매 phase 종료 시 `compat-check.sh` 결과 + bench 추이를 `docs/exec-plans/completed/phase-N-retro.md`에 첨부.
