---
name: run-verification
description: 공용 검증 게이트(scripts/verify-all.sh + uv run pytest)를 실행하고 실패를 분류해 다음 행동을 안내한다.
---

# Skill: run-verification

## When to use

- 코드 수정 직후.
- PR 작성 직전.
- CI 실패 재현 시.

## Procedure

1. 변경 파일 확인: `bash scripts/changed-files.sh`.
2. 게이트 실행: `bash scripts/verify-all.sh`.
3. 종료 코드 0 → §3 테스트 단계로.
4. 0 아님 → §4 분류표로 원인 식별.
5. 환경이 갖춰져 있으면 테스트:
   ```bash
   bash scripts/run-tests.sh -m unit
   bash scripts/run-tests.sh -m integration
   bash scripts/run-tests.sh -m ui          # pytest-qt 필요
   ```
6. (해당 시) 호환성 / 벤치:
   ```bash
   bash scripts/compat-check.sh tests/fixtures/sample-minimal/
   bash scripts/bench.sh
   ```

## 실패 분류

| 단계 | 신호 | 다음 행동 |
|---|---|---|
| `lint` | `ruff check` 위반 | 안전: `uv run ruff check --fix`. 위험: `uv run ruff check --unsafe-fixes`는 사람 승인. |
| `lint` | `ruff format --check` 실패 | `uv run ruff format <file>` 후 재시도. |
| `type-check` | `mypy` 에러 | 타입 보강. `# type: ignore`는 한 줄만 + 사유 주석 필수 (G1). |
| `structure-check` | "Domain must not import frameworks" | `core/` 격리 위반. 의존을 Application으로 옮김. |
| `structure-check` | "Infrastructure must not depend on UI" | UI를 import하지 않게 — `core.event_bus.pyqtSignal`로 우회. |
| `structure-check` | "framework imports allowed only in indexer/frameworks/" | `django`/`flask` 등을 `frameworks/<name>.py`로 이동. |
| `structure-check` | "possible secret" | 즉시 commit 취소, 키 회전, `docs/security.md`. |
| `structure-check` | "C++ legacy touched" warn | 의도면 PR 라벨 `legacy-cpp-touch` + 사유. 비의도면 변경 되돌림. |
| `docs-freshness` | "exec-plan stale" | 매칭 plan의 `last_updated` 갱신 또는 `completed/`로 이동. |
| `adapter-sync` | "AGENTS/CLAUDE drift" | 양쪽 Harness Entry의 첫 링크가 `docs/README.md`인지 확인. |
| `adapter-sync` | "deprecated C++ build command in allowlist" | `.codex/config.*.toml`에서 `cmake`/`bash script/buildonly.sh` 제거. |
| `pytest` | 실패 단언 | 회귀면 가까운 `tests/<area>/test_*.py`에 케이스 추가 후 fix. flaky면 `tests/` 회의 + tech-debt 등재. |
| `pytest` | `qtbot` import 실패 | `uv sync --all-extras`로 `pytest-qt` 설치. |
| `compat-check` | placeholder 표시 (Phase 0 이전) | OK. Phase 0 D8에 PoC 1로 실제 구현. |
| `compat-check` | 호환성 실패 | `docs/sop/sourcetrail-compat.md` 절차로 원인 파악 — 절대 우회 금지 (G14). |

## Anti-patterns

- 실패 → `--no-verify`로 우회. **금지** (G1, G3, G14 등).
- "내 변경과 무관한 실패니까 무시" — 무관성 증명 전엔 절대.
- 같은 게이트를 3회 이상 같은 방식으로 재시도. 다르게 접근하거나 사람 에스컬레이션.
- `pip install`로 의존성 추가 — G13 위반. 항상 `uv add`.

## Verification

- exit 0 + `docs/quality-score.md`의 핵심 항목(Build/test green, Lint, Structure, Type) 만점.
