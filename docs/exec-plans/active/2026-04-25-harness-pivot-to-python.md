---
title: 하네스 피벗 — C++ 전제 v0 → Python (Sourcetrail_Remake) 전제 v1
status: In Progress
owner: maintainer
created: 2026-04-25
last_updated: 2026-04-25
related_specs: [docs/plan/01-requirements.md, docs/plan/02-architecture.md]
related_designs: []
autonomy_level: L2
phase: pre-Phase-0
---

# 1. Context

`docs/plan/`의 11개 파일이 새 방향을 확정했다: 기존 C++ Sourcetrail은 **읽기 전용 reference로 보존**, 같은 레포에 **Python 데스크톱 앱 Sourcetrail_Remake (PyQt6 + QScintilla, Windows 전용, 31주, 1인 풀타임)**을 신규 구축. 따라서 같은 날 만든 v0 하네스 45개 산출물 거의 전부가 C++ 전제(CMake/Catch2/clang-format/`bin/test/`)로 굳어 있어 새 프로젝트에서 즉시 무용지물. **Phase 0 코딩 착수 전에** 하네스를 Python 전제로 재포팅한다.

# 2. Goal

Phase 0 D1(레포 구조 작성, `pyproject.toml`)에 착수했을 때 하네스가 즉시 도움이 되도록:

- `bash scripts/verify-all.sh` exit 0 (Python 도구 부재 시 graceful skip).
- `docs/references/build-and-test.md`가 uv/pytest/ruff/mypy를 단일 진실 원천으로.
- `docs/references/architecture-rules.md`가 Python UI→App→Domain→Infra 단방향을 강제하고 C++ legacy 영역은 무수정 기대치로 분리.
- `.codex/config.toml` 4종의 shell allowlist가 Python 명령으로 갱신.
- `.claude/skills/` 4개의 모듈맵이 Python 트리(`src/sourcetrail_remake/cli/core/db/indexer/refactor/search/ui`)로.
- `docs/plan/`의 11개 대관 계획이 `docs/index-of-deliverables.md`에 등재.

# 3. Non-goals

- Phase 0의 실제 Python 코딩 (`pyproject.toml` 작성, `src/sourcetrail_remake/__init__.py` 생성 등). 본 plan은 하네스만.
- 기존 C++ 코드 수정/삭제. 보존 결정.
- Next.js/FastAPI 가정 (요구사항 아님).

# 4. Approach (7 묶음)

| # | 단계 | 산출물 | 검증 |
|---|---|---|---|
| 1 | Plan 이전 + active/completed 정리 | `docs/plan/{00..03,phase-0..6}.md`, `docs/plan/README.md`, `docs/exec-plans/active/2026-04-25-harness-pivot-to-python.md`, completed 이동 | `ls docs/plan/`, `ls docs/exec-plans/{active,completed}/` |
| 2 | 핵심 정책 docs 재포팅 | `docs/references/build-and-test.md`, `architecture-rules.md`, `docs/golden-rules.md`, `docs/observability.md` | 내용에 cmake/catch2/bin/test 흔적 0 (외 legacy 섹션 제외) |
| 3 | 검증 스크립트 재작성 | `scripts/lint.sh`(ruff), `type-check.sh`(NEW mypy), `structure-check.sh`(Python import + legacy 보호), `run-tests.sh`(uv pytest), `compat-check.sh`(NEW placeholder), `bench.sh`(NEW), `docs-freshness.sh`, `check-adapter-sync.sh`, `verify-all.sh` | `bash scripts/verify-all.sh` exit 0 |
| 4 | 어댑터 재포팅 | `.codex/config.{toml,balanced,conservative,semi-autonomous}.toml`, `.codex/README.md`, `.claude/skills/{explore-codebase,create-exec-plan,run-verification,prepare-pr}/SKILL.md`, `.claude/hooks/README.md`, `AGENTS.md`/`CLAUDE.md` Harness Entry | shell allowlist에 cmake 0건, 모듈맵에 lib_cxx 0건 |
| 5 | 운영 문서 재포팅 | `docs/{drift-control,failure-modes,quality-score,security,reliability}.md`, `docs/sop/{codex,claude,human-approval,worktree}.md`, `docs/sop/sourcetrail-compat.md`(NEW) | 정합성 |
| 6 | 로드맵 31주 + CI + index | `docs/roadmap-31w.md`(NEW, 기존 roadmap-12w.md 대체), `docs/autonomy-levels.md` 미세, `.github/workflows/harness-gate.yml`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/CODEOWNERS`, `ARCHITECTURE.md`, `docs/index-of-deliverables.md` 전체 재작성 | 산출물 카운트 일치 |
| 7 | 최종 검증 | — | `bash scripts/verify-all.sh` exit 0, `bash scripts/check-adapter-sync.sh` exit 0, `docs/index-of-deliverables.md`의 모든 경로 존재 |

# 5. Critical files

본 plan에서 변경/생성하는 모든 파일은 묶음 6 종료 시 `docs/index-of-deliverables.md`(v1)에 카탈로그.

# 6. Reused existing assets

- 기존 `docs/exec-plans/{active,completed}/_template.md` 양식 재사용 (Python 프로젝트에도 그대로 적합).
- `scripts/changed-files.sh` 그대로 (언어 중립).
- `.gitignore` 보강은 Phase 0에서 (uv, pytest, mypy 캐시 추가).
- worktree의 11개 plan 파일이 `docs/plan/`의 source.

# 7. Risks & mitigations

| 위험 | 영향 | 완화책 |
|---|---|---|
| 하네스가 Phase 0 D1보다 늦게 끝남 | Phase 0 시작 지연 | 7 묶음을 단일 세션에 끝낸다. PR 분할 안 함. |
| C++ legacy 룰을 Python 룰로 잘못 덮어씀 | 기존 C++ 트리에 false positive | `structure-check.sh`가 `src/lib*/`, `src/app/`, `src/indexer/`, `src/external/`, `src/test/`를 Python 룰에서 제외 |
| `.codex/` allowlist에 `cmake` 잔존 | Codex가 C++ 빌드 시도 | check-adapter-sync.sh가 deprecated 명령 검사 |
| `docs/index-of-deliverables.md`가 v0(45개) 그대로 | 인덱스 검사가 미존재 경로 false fail | 묶음 6에서 v1으로 전체 재작성 |

# 8. Verification

- [ ] `bash scripts/verify-all.sh` exit 0
- [ ] `bash scripts/check-adapter-sync.sh` exit 0
- [ ] `docs/plan/`의 11개 파일이 `docs/index-of-deliverables.md`에 등재
- [ ] AGENTS.md / CLAUDE.md 첫 링크가 여전히 `docs/README.md`
- [ ] `src/lib_*`, `src/app`, `src/indexer`, `CMakeLists.txt` 무수정 (`git status`로 untracked 외 변경 0)

# 9. Rollback plan

본 작업은 모두 untracked / 새 디렉터리 생성. 회귀 시 `git clean -fd docs/ scripts/ .codex/ .claude/ .github/CODEOWNERS .github/PULL_REQUEST_TEMPLATE.md .github/workflows/`로 일괄 제거 가능 (단, `.gitignore` 미수정 가정).

# 10. Status log

| 날짜 | 변경 |
|---|---|
| 2026-04-25 | created. 묶음 1 진행 |
