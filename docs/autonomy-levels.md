# Autonomy Levels

에이전트의 자율성을 3단계로 분리. 도구 프로파일과 1:1 매핑.

| Level | Codex 프로파일 | Claude 권장 | 한 줄 정의 |
|---|---|---|---|
| **L1 — Read & Suggest** | `.codex/config.conservative.toml` | `default` perm + 보수 hook | 탐색·리뷰·제안. 변경 0. |
| **L2 — Patch & Verify** | `.codex/config.toml` (균형) | `default` perm + 표준 hook | 변경 가능, 모든 명령에 검증. PR 직전까지. |
| **L3 — Autonomous Loop** | `.codex/config.semi-autonomous.toml` | `acceptEdits` 한정 + 강한 hook | worktree 격리 + 자동 검증 + 자동 PR. |

## 레벨별 세부

### L1 — Read & Suggest

| 항목 | 값 |
|---|---|
| 허용 권한 | 읽기, `uv run ruff check`, `uv run mypy --no-error-summary`, structure-check, docs-freshness, git status/diff/log |
| 필수 검증 | (없음 — 변경 0) |
| 금지 | 모든 쓰기, 모든 빌드, 모든 머지/푸시, `uv add`, `uv sync`, `uv run pytest` |
| 승인 요구 | 모든 명령에 사람 승인 (untrusted) |
| 적합 | 신규 코드베이스 학습, 보안 리뷰, 부채 탐색, 사고 분석, **C++ legacy 영역 탐색** |

### L2 — Patch & Verify (기본값)

| 항목 | 값 |
|---|---|
| 허용 권한 | 워크스페이스 쓰기, `uv sync`/`uv add`/`uv run pytest`/`uv run ruff`/`uv run mypy`/`uv run python`, 검증 게이트, 커밋 (push 제외 자동) |
| 필수 검증 | `bash scripts/verify-all.sh` 통과 후에만 PR. DB 영향 시 `compat-check.sh` 추가. |
| 금지 | 보호 경로 변경 (사람 승인), `--force`, `--no-verify`, `--amend`, network, `pip install` |
| 승인 요구 | 보호 경로, 1000+ LOC, 새 의존성 (`uv add`), C++ legacy, golden rule 우회 |
| 적합 | 일상 코딩, 버그 fix, 기능 추가, 리팩터, phase 작업 |

### L3 — Autonomous Loop

| 항목 | 값 |
|---|---|
| 허용 권한 | L2 + worktree 자동 생성/제거, `feature/*` 푸시, `gh pr create` |
| 필수 검증 | `verify-all.sh` + `run-tests.sh` 관련 마커 + 자기 점수 ≥ 85. DB 영향 시 `compat-check.sh` 통과 필수. |
| 금지 | L2 금지 + master/main 직접 푸시, 릴리스 태그, 보호 경로 변경 (어떤 형태로도) |
| 승인 요구 | PR 머지는 항상 사람. 머지 전 자동화는 모두 OK. |
| 적합 | 잘 정의된 cleanup, 라벨 기반 자동 fix, 정기 부채 정리, format/import sort PR |

## 승격/강등 규칙

- 새 기여자(에이전트 포함) → L1로 시작.
- L1 1주 무사고 + 사람 검토 통과 → L2.
- L2 4주 무사고 + 평균 품질 점수 ≥ 90 → 특정 영역에 한해 L3.
- 사고 발생 시 즉시 L1로 강등. 회고 plan 후 사람 승인으로 복귀.
- G14 (compat) 위반 시 즉시 L1, 30일 관찰.

## 자동화 가능성

| 항목 | 자동화 |
|---|---|
| 프로파일 강제 | Codex profile / Claude settings |
| 보호 경로 차단 | `scripts/structure-check.sh` + Claude PreToolUse hook |
| 푸시 대상 제한 | git pre-push hook 또는 Codex shell deny |
| 머지는 항상 사람 | GitHub branch protection |
| compat 자동 게이트 | CI |
