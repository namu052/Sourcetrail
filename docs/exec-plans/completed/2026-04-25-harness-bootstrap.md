---
title: 공용 하네스 부트스트랩 (C++ 전제 v0)
status: Completed (Superseded)
owner: maintainer
created: 2026-04-25
completed: 2026-04-25
merged_pr: (uncommitted, superseded by harness-pivot-to-python)
related_specs: []
related_designs: []
autonomy_level: L2
note: |
  본 plan은 C++ Sourcetrail 유지보수 전제로 만들어진 v0 하네스 산출물(45개)을 다룬다.
  같은 날 사용자가 Sourcetrail_Remake (Python 신규 프로젝트)로 방향을 확정하면서
  본 산출물 전부가 Python용으로 재포팅 중. 후속: docs/exec-plans/active/2026-04-25-harness-pivot-to-python.md
---

# 1. Context

본 리포(Sourcetrail)에 공용 하네스 골격을 처음 도입한다.
`docs/roadmap-12w.md`의 W1~W2 산출물에 해당.

# 2. Goal

- `bash scripts/verify-all.sh` 실행 가능하고 새 변경 없는 상태에서 exit 0.
- AGENTS.md / CLAUDE.md가 docs/README.md를 1번 링크로 참조.
- `.codex/` 4종 + `.claude/skills/` 4종 + hook 초안 등재.

# 3. Non-goals

- 기존 Sourcetrail 코드/빌드 변경.
- Next.js/FastAPI 가정 적용.

# 4. Approach

| # | 단계 | 산출물 | 검증 방법 |
|---|---|---|---|
| 1 | 공용 코어 docs 골격 | `docs/`, `ARCHITECTURE.md` | `tree docs/` 인덱스 일치 |
| 2 | 어댑터 (AGENTS/CLAUDE Harness Entry + .codex + .claude/skills) | 위 파일들 | `head AGENTS.md CLAUDE.md` |
| 3 | 검증 스크립트 + GitHub Actions | `scripts/`, `.github/workflows/harness-gate.yml` | `bash scripts/verify-all.sh` exit 0 |
| 4 | 자율성 / 드리프트 / 로드맵 문서 | `docs/{autonomy-levels,drift-control,failure-modes,roadmap-12w}.md` | 자기 일관성 |
| 5 | 어댑터 동기 검사 + 산출물 인덱스 | `scripts/check-adapter-sync.sh`, `docs/index-of-deliverables.md` | `bash scripts/check-adapter-sync.sh` exit 0 |

# 5. Critical files

본 PR에서 새로 만든 모든 파일은 `docs/index-of-deliverables.md` 참조.

# 6. Reused existing assets

- `.clang-format` (lint 게이트)
- `script/build.sh`, `script/buildonly.sh` (빌드/테스트 본문, 재구현 금지)
- `bin/test/` 작업 디렉터리 규약
- 기존 `.travis.yml` / `appveyor.yml` (C++ 빌드는 그대로 위임)

# 7. Risks & mitigations

| 위험 | 영향 | 완화책 |
|---|---|---|
| 글로벌 `~/.claude/settings.json` hook과 충돌 | 작업 방해 | `.claude/hooks/README.md`는 초안만, 적용은 `update-config` 스킬로 사람 승인 후 |
| Windows에서 bash 미가용 | 검증 불가 | Git Bash / WSL 가정 명시 (`docs/roadmap-12w.md` 위험 절) |
| `clang-format` 미설치 | 로컬 lint skip | CI에서 강제 (`harness-gate.yml`) |

# 8. Verification

- [x] `bash scripts/verify-all.sh` exit 0
- [x] `head -20 AGENTS.md && head -20 CLAUDE.md`로 첫 링크 확인
- [x] `docs/index-of-deliverables.md` 모든 항목 존재
- [ ] 환경 갖춰지면 `bash script/build.sh release` (영향 0)

# 9. Rollback plan

본 PR 단일 머지 → 회귀 시 `git revert <merge-sha>`. `script/`, `src/`, `CMakeLists.txt`는 미수정이므로 빌드 영향 없음.

# 10. Status log

| 날짜 | 변경 |
|---|---|
| 2026-04-25 | created |
| 2026-04-25 | bundles A~E completed; verify-all green |
