# Observability

**Sourcetrail_Remake** 맥락에서 관측 가능성은 **앱/인덱서 로그 + 인덱싱 결과 DB + Catch2-style pytest 로그 + 성능 벤치 결과**를 일관되게 수집·질의 가능하게 만드는 것이다.

## 1. 데이터 흐름

```
┌─────────────────────────┐  EventBus(QObject)  ┌──────────────────────────┐
│  GUI process            │ ───────────────────► │  IndexerService          │
│  (PyQt6 main thread)    │ ◄─────────────────── │  (QThread)               │
│  panels / graph / editor│                      │  Jedi/Parso/Rope wrappers│
└──────────┬──────────────┘                      └────────────┬─────────────┘
           │ logging                                          │ logging
           ▼                                                  ▼
   %APPDATA%/Sourcetrail_Remake/logs/app-<ts>.log    .../logs/indexer-<ts>.log
           │                                                  │
           └──────────────────────┬───────────────────────────┘
                                  ▼
                       scripts/collect-logs.sh (Phase 1)
                                  ▼
                  docs/generated/observability/<run-id>/
                                  ▼
                   에이전트(Claude/Codex)가 grep / 요약
```

테스트 / 벤치 출력:

```
uv run pytest --junitxml=docs/generated/test-runs/<ts>.xml
uv run pytest -m performance --benchmark-json=docs/generated/bench/<ts>.json
```

## 2. 로그 위치 / 포맷

| 종류 | 위치 | 포맷 |
|---|---|---|
| GUI 앱 | `%APPDATA%/Sourcetrail_Remake/logs/app-<YYYYMMDD-HHMMSS>.log` | structured (`time level logger msg key=value`) |
| 인덱서 (백그라운드) | `.../logs/indexer-<ts>.log` | 동일 |
| 인덱싱 결과 DB | 사용자 지정 `.srctrldb` (작업 단위) | SourcetrailDB v25 호환 |
| 사용자 설정 / 세션 | `%APPDATA%/Sourcetrail_Remake/{config.json, sessions/, layouts/, snippets/}` | JSON / YAML |
| 크래시 로그 | `.../logs/crash-<ts>.log` | full traceback + qt platform info |

로그 회전: 30일 또는 200MB 초과 시 압축. 자동 (Phase 1에 추가).

## 3. 작업 단위 격리 (worktree)

`docs/sop/worktree.md` 참조. 각 작업:

1. `git worktree add .claude/worktrees/<task-slug> origin/master`
2. 그 worktree에서 `uv sync` (가상환경은 `.venv/`로 worktree-local).
3. 인덱싱 결과 DB는 `.claude/worktrees/<slug>/.tmp-srctrldb/`로 격리.
4. 작업 종료 시 worktree 제거.

## 4. UI / DOM 점검

PyQt6 데스크톱 — DOM 없음. 대안:

- **헤드리스 smoke**: `uv run python -c "from sourcetrail_remake.ui.main_window import MainWindow; ..."` (Phase 1+).
- **위젯 회귀 (pytest-qt)**: `tests/ui/`에서 `qtbot.addWidget(w); qtbot.waitUntil(...)`.
- **스크린샷 회귀**: 향후 `pytest-qt` + `qApp.primaryScreen().grabWindow(w.winId()).save(...)` (Phase 5 검토).

## 5. 사용자 여정 테스트 (10개 시나리오)

분기 1회 수동 검수. Phase별 우선순위.

| # | 시나리오 | 통과 기준 | 첫 적용 Phase |
|---|---|---|---|
| 1 | 신규 Python 프로젝트 추가 → Shallow 인덱싱 → 그래프 표시 | 1만 LoC < 1분, 노드/엣지 표시 | Phase 1 |
| 2 | 그래프에서 노드 클릭 → ContextWindow 0.2s 내 정의 표시 | < 200ms | Phase 2 |
| 3 | 다중 RelationWindow 오픈 + 개별 Lock | Lock 동작 정확 | Phase 2 |
| 4 | Symbol Window 트리 정렬 토글 | 이름/라인/타입 정렬 1s 내 | Phase 2 |
| 5 | F5 Smart Rename: Django 샘플 ForeignKey 필드 | 회귀율 < 1%, undo 가능 | Phase 3 |
| 6 | F6 Fuzzy Lookup: 10만 심볼 | < 50ms | Phase 3 |
| 7 | F19 Type Hint: typed/untyped 비교 → unsolved 50% 감소 | 측정 가능 | Phase 4 |
| 8 | F21 Django ORM 관계 (FK/M2M) → 녹색 점선 엣지 | 시각 확인 | Phase 4 |
| 9 | F23 Jupyter 셀 인덱싱 → 그래프에 셀 노드 | `.ipynb` ↔ `.py` 크로스 | Phase 4 |
| 10 | 인스톨러 → Windows 11 클린 머신 → 인덱싱 1회 성공 | < 200MB, 오탐 0 | Phase 5 |

## 6. 에이전트 질의 예시

```
"마지막 인덱서 실행에서 Jedi unresolved 비율은?"
→ grep -E 'unresolved' %APPDATA%/Sourcetrail_Remake/logs/indexer-*.log | tail -50
   또는: tests/integration/run-stats.json 읽기

"마지막 pytest run에서 실패한 테스트는?"
→ ls -t docs/generated/test-runs/*.xml | head -1 → junit XML 파싱

"이 변경 후 인덱싱 처리량 회귀?"
→ jq '.benchmarks[] | select(.name | contains("indexer"))' docs/generated/bench/*.json | tail -10

"FastAPI 라우트가 안 잡히는 케이스 보여줘"
→ grep -E 'fastapi.*unresolved|frameworks.fastapi' .../logs/indexer-*.log
```

## 7. 임시 환경 → 검증 → 폐기

```bash
# 1. 임시 환경
git worktree add .claude/worktrees/feat-x origin/master
cd .claude/worktrees/feat-x
uv sync --all-extras

# 2. 검증
bash scripts/lint.sh
bash scripts/type-check.sh
bash scripts/run-tests.sh -m unit
bash scripts/run-tests.sh -m integration

# 3. (옵션) 호환성
bash scripts/compat-check.sh tests/fixtures/sample-django/

# 4. 정리
cd -
git worktree remove .claude/worktrees/feat-x
```

자동 정리 (`scripts/worktree-clean.sh`, Phase 1+)는 7일 이상 commit 없는 worktree를 경고.

## 8. 성능 메트릭 회귀 추적

`tests/performance/`의 pytest-benchmark 결과는 `docs/generated/bench/`에 시계열로 적재.
Phase 1부터 매 PR에서 다음 SLA 확인 (회귀 시 PR 차단 또는 warn):

| 지표 | 목표 (`docs/plan/01-requirements.md`) |
|---|---|
| 1만 LoC 인덱싱 (Shallow) | < 1분 |
| 1만 LoC 인덱싱 (Deep) | < 3분 |
| 그래프 첫 표시 | < 500ms |
| Fuzzy Lookup (10만 심볼) | < 50ms |
| UI 60fps (1천 노드) | 60fps |
| 메모리 (대형 프로젝트) | < 2GB |
