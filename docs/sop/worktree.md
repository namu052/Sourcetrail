# SOP — Worktree (Sourcetrail_Remake / Python)

병렬 작업이 빌드 산출물·로그·DB·`.venv`를 섞지 않게 하는 표준 절차.

## 1. 위치

| 용도 | 경로 |
|---|---|
| 작업 worktree | `.claude/worktrees/<task-slug>/` |
| 가상환경 | `<worktree>/.venv/` (uv가 worktree-local로 생성) |
| 임시 인덱스 DB | `<worktree>/.tmp-srctrldb/` |
| 테스트 산출물 | `<worktree>/docs/generated/test-runs/<ts>.xml` |
| 벤치 산출물 | `<worktree>/docs/generated/bench/<ts>.json` |

> 경로 명 `.claude/worktrees/`는 도구 중립적으로 사용 (Codex도 동일). 역사적 이름.

## 2. 생성

```bash
TASK=indexer-jedi-resolver-mvp
git worktree add .claude/worktrees/$TASK origin/master
cd .claude/worktrees/$TASK
git checkout -b feature/$TASK

uv sync --all-extras    # worktree-local .venv 생성
```

## 3. 작업

```bash
bash scripts/verify-all.sh
bash scripts/run-tests.sh -m unit
bash scripts/run-tests.sh -m integration -k indexer
bash scripts/compat-check.sh tests/fixtures/sample-minimal/
```

## 4. PR

```bash
git push -u origin feature/$TASK
gh pr create --fill   # PR_TEMPLATE 자동 사용
```

## 5. 정리 (반드시)

```bash
cd <repo root>
git worktree remove .claude/worktrees/$TASK
git branch -D feature/$TASK   # 머지 완료 후만
```

## 6. 자동 정리

`scripts/worktree-clean.sh` (Phase 1+ TBD):
- 7일 이상 commit 없는 worktree → 경고
- 머지 완료된 브랜치의 worktree → 자동 제거

## 7. 함정

- **두 worktree에서 같은 가상환경 사용 금지**. uv는 기본적으로 worktree-local `.venv`를 만들지만, 글로벌 `UV_PROJECT_ENVIRONMENT` 설정 시 충돌 가능.
- **`%APPDATA%/Sourcetrail_Remake/`는 머신 단위 공유**. 한 worktree에서 사용자 설정 변경하면 다른 worktree도 영향. 테스트는 `tmp_path` fixture만.
- **`uv.lock`이 worktree마다 다르면 위험**. uv.lock은 단일 진실 — 변경 시 PR 분리.
- **`git worktree prune`은 신중히**. 동시 작업 중인 다른 세션을 끊을 수 있음.
- **C++ legacy 영역의 build/ 디렉터리**: 본 프로젝트가 사용하지 않으니 무시. CMake가 만든 캐시가 worktree에 남아있어도 Python 빌드와 무관.
