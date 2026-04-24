---
name: prepare-pr
description: PR_TEMPLATE을 채우고 자기 리뷰 + 품질 점수 + (해당 시) SourcetrailDB 호환 결과를 첨부해 PR을 준비한다.
---

# Skill: prepare-pr

## When to use

- 검증(`run-verification` 스킬) 통과 직후.
- PR 본문 작성 전.

## Procedure

1. **자기 리뷰**:
   - `git diff origin/master...HEAD --stat`로 범위 확인.
   - 1000+ LOC면 plan(`docs/exec-plans/active/`) 링크 필수. 없으면 `create-exec-plan`으로 작성.
   - `docs/golden-rules.md` G1~G15 위반 self-check.
   - C++ legacy 변경이 있으면 `legacy-cpp-touch` 라벨 + 사유 명시.

2. **품질 점수 산출**:
   - `docs/quality-score.md` §1 표대로 자체 채점.
   - <85점이면 사람 승인 필요.
   - DB 호환에 영향 가능한 변경이면 `bash scripts/compat-check.sh`도 자체 실행 후 결과 첨부.

3. **본문 작성**: `.github/PULL_REQUEST_TEMPLATE.md` 사용. 다음 절은 반드시:
   - **Summary** — 1~3줄.
   - **Why** — exec-plan + 관련 phase (`docs/plan/phase-N-*.md`) 링크.
   - **Test plan** — 어떤 마커로 어떻게 검증 (`pytest -m unit -k ...` 등).
   - **Risk & rollback** — `git revert`로 충분한지.
   - **Quality score** — §2 결과.
   - **Compat check** (DB/스키마 영향 시) — `bash scripts/compat-check.sh` 결과.

4. **푸시 + PR**:
   ```bash
   git push -u origin feature/<slug>
   gh pr create --fill
   ```

5. CI 모니터링. 실패 시 `run-verification`으로 회귀.

## Anti-patterns

- "테스트는 통과했지만 UI는 안 봤음" — `tests/ui/`로 회귀 자동화. 시각적 변경은 `docs/observability.md` §5의 시나리오 중 관련 것 수동 확인.
- exec-plan 없이 큰 PR. → CI가 `needs-human-review` 라벨 자동.
- `--force` 푸시. **절대 금지** (`docs/security.md`).
- DB 스키마 변경인데 `compat-check.sh` 누락. → G14 위반 위험.

## Verification

- PR 생성 + CI(`harness-gate`, `ci`) 트리거.
- PR 본문에 §3의 5~6개 절 모두 채워짐.
- 라벨 `quality-score:<점수>`, `size:*`, (해당 시) `needs-human-review`/`legacy-cpp-touch` 자동 부여.
