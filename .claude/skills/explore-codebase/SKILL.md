---
name: explore-codebase
description: Sourcetrail_Remake (Python) 모듈맵을 우선 탐색해 컨텍스트를 빠르게 수집한다. 신규 작업 시작 시 / 큰 변경 직전에 사용.
---

# Skill: explore-codebase

## When to use

- 새 task가 어느 모듈에 속하는지 모를 때.
- 1000+ LOC 변경을 시작하기 직전.
- 버그가 어디서 비롯되는지 후보를 좁힐 때.
- C++ legacy 영역 vs Python 영역 구분이 필요할 때.

## Procedure

1. **항상 먼저** [`docs/README.md`](../../../docs/README.md) 우선순위로 읽고 [`docs/plan/00-overview.md`](../../../docs/plan/00-overview.md)로 phase 컨텍스트 확인.

2. 작업이 속할 모듈을 다음 매트릭스에서 고른다:

### Python (Sourcetrail_Remake — 작업 대상)

| 영역 | 위치 | 레이어 | 의존 (in) | 의존 (out) |
|---|---|---|---|---|
| 진입점 | `src/sourcetrail_remake/__main__.py`, `cli/` | App | core, indexer, ui(GUI인 경우만) | — |
| 도메인 모델 | `src/sourcetrail_remake/core/{project,types}.py` | Domain | (없음) | — |
| 공통 서비스 | `core/{event_bus,config,environment,logging}.py` | App glue | Domain | PyQt(EventBus만) |
| DB | `src/sourcetrail_remake/db/{schema,writer,reader,extension,compat}.py` | Infra | Domain | sqlite3 |
| 인덱서 | `src/sourcetrail_remake/indexer/{service,jedi_resolver,parso_walker,type_hints,duck,decorators,dynamic,jupyter,unsolved}.py` + `frameworks/` | App+Infra | Domain, db | jedi, parso |
| 리팩토링 | `refactor/rename.py` | App+Infra | Domain | rope |
| 검색 | `search/{service,fuzzy,references}.py` | App+Infra | Domain, db | rapidfuzz |
| UI 메인 | `ui/main_window.py` | Presentation | core, indexer/service, search/service | PyQt6 |
| 그래프 뷰 | `ui/graph/{view,scene,nodes,edges,layout,hover_preview,import_graph,export}.py` | Presentation | core | PyQt6 |
| 패널 | `ui/panels/{context,symbol,relation,relation_manager,search_results,references,bookmark,clip}.py` | Presentation | core (event_bus 경유) | PyQt6 |
| 에디터 | `ui/editor/{code_editor,semantic,decoration,overview,folding,revision}.py` | Presentation | core | PyQt6, QScintilla |
| 다이얼로그 | `ui/dialogs/{rename,dir_compare,indexing_mode}.py` | Presentation | core | PyQt6 |
| 팔레트/레이아웃 | `ui/{palette,layouts,navigation,controls,themes}/` | Presentation | core | PyQt6 |
| 테스트 | `tests/{unit,integration,ui,compatibility,performance}/` | — | 모두 | pytest, pytest-qt |
| PoC | `poc/{01_jedi_to_sqlite,02_editor_hello,03_graph_hello}/` | 격리 | — | (Phase 0만) |

### C++ Legacy (읽기 전용 reference)

| 위치 | 비고 |
|---|---|
| `src/lib*/`, `src/app/`, `src/indexer/`, `src/external/`, `src/test/` | 무수정 — Golden Rule G7 |
| `CMakeLists.txt`, `cmake/`, `script/`, `.travis.yml`, `appveyor.yml` | 무수정 |
| `java_indexer/`, `ide_plugins/`, `bin/`, `deployment/`, `setup/`, `testing/` | 무수정 |

3. 모듈을 정한 뒤 다음 도구로 좁힌다:

```
Glob:  src/sourcetrail_remake/<module>/**/*.py
Grep:  "<symbol>"  --type py
Read:  관련 모듈 → 테스트 (tests/<area>/test_*.py) → 관련 plan (docs/plan/phase-N-*.md)
```

4. 레이어 경계를 넘어야 하면 [`docs/references/architecture-rules.md`](../../../docs/references/architecture-rules.md)를 다시 확인. **위반 의도라면 작업 전에 사람 승인.**

5. 결과는 `docs/exec-plans/active/<task>.md`의 §5 Critical files / §6 Reused existing assets에 기록.

## Anti-patterns

- 무작정 `Glob src/**/*.py` → C++ legacy의 *.cpp까지 휩쓸기. 항상 `src/sourcetrail_remake/**/*.py`로 한정.
- `lib_gui`/`lib_cxx` 같은 C++ 경로를 Python 작업 컨텍스트로 끌어옴 — G7 위반.
- `docs/plan/phase-X-*.md`를 안 읽고 시작.
- 한 번에 5개 이상 파일 Read → §1 우선순위를 안 본 신호.

## Verification

- 작성한 plan이 §5에 **3~10개의 구체 경로**를 가진다.
- §6에 **재사용 가능한 기존 모듈/유틸 1개 이상** 명시.
- 변경 영역이 모두 §2의 Python 매트릭스에 속하고, C++ legacy는 0건.
