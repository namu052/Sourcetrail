---
title: Sourcetrail_Remake 31주 로드맵
status: Active
owner: maintainer
last_updated: 2026-04-25
related_specs: [docs/plan/00-overview.md, docs/plan/01-requirements.md]
---

# 31-Week Roadmap

기간: 2026-04-25(W0) → 31주. 1인 풀타임. 본 로드맵은 [`docs/plan/00-overview.md`](plan/00-overview.md)와 1:1 매핑되며, 매 phase 종료 시 진척/지연/이월 갱신.

## 개요 (timeline)

```
주차 │ 1 2 │ 3 4 5 6 7 8 │ 9 ······ 16 │ 17 ···· 22 │ 23 ···· 28 │ 29 30 31 │
─────┼─────┼─────────────┼─────────────┼────────────┼────────────┼──────────┤
P0   │ ███ │             │             │            │            │          │ 셋업 & PoC (M0)
P1   │     │ ███████████ │             │            │            │          │ MVP 인덱서+그래프 (M1 Alpha)
P2   │     │             │ █████████   │            │            │          │ Context/Symbol/Relation/Editor (M2 Beta MVP)
P3   │     │             │             │ ██████     │            │          │ Rename/Search/Layouts (M3)
P4   │     │             │             │            │ ██████     │          │ Python 특화 (M4 RC)
P5   │     │             │             │            │            │ ███      │ 패키징 (M5 v1.0)
P6   │ ═════════════════════ 전 기간 지속 (테스트 & 문서) ═══════════════════ │
```

## Phase별 상세

### Phase 0 — Foundation (W1~2)

| 영역 | 작업 | 산출물 | 완료 기준 | 위험 | 의존 |
|---|---|---|---|---|---|
| 코드 | 레포 구조, `pyproject.toml`, `uv.lock` | `src/sourcetrail_remake/`, `tests/`, `poc/` | `uv run python -m sourcetrail_remake` 빈 QMainWindow | R-06 QScintilla 휠 부재 | — |
| CI | Windows runner | `.github/workflows/ci.yml` | lint+type+empty test green | — | — |
| 문서 | DB schema 역공학 | `docs/db-schema.md` | enum 100% 매핑 | R-14 | — |
| PoC | Jedi → SQLite → 원본 GUI 열람 (PoC 1) | `poc/01_jedi_to_sqlite/` | **G1 통과** (G14 핵심) | R-02 | — |
| PoC | PyQt6 + QScintilla 에디터 (PoC 2) | `poc/02_editor_hello/` | 위젯 표시 + Python 렉서 | R-06 | — |
| PoC | QGraphicsView 3-노드 (PoC 3) | `poc/03_graph_hello/` | 60fps + unsolved 해치 | R-04 | — |
| 하네스 | (이미 완료) Python용으로 재포팅 | `docs/`, `scripts/`, `.codex/`, `.claude/`, `.github/` | `verify-all.sh` exit 0 | — | — |

**리스크 게이트 G1 (W2)**: PoC 1 성공? 실패 시 Parso 단독 접근 재설계.

### Phase 1 — MVP Indexer + Graph (W3~8) → M1 Alpha

| 영역 | 작업 | 산출물 | 완료 기준 | 위험 |
|---|---|---|---|---|
| Indexer | Jedi/Parso 통합, IndexerService (QThread) | `src/sourcetrail_remake/indexer/{service,jedi_resolver,parso_walker}.py` | 1만 LoC < 1분 (Shallow) | R-04 |
| DB | Writer/Reader, SourcetrailDB v25 호환 | `src/sourcetrail_remake/db/{schema,writer,reader,extension}.py` | compat-check 5종 통과 | R-02 |
| UI | MainWindow + GraphView (P0 전체) | `src/sourcetrail_remake/ui/{main_window.py,graph/}` | 첨부 이미지 시각 동일 | R-04, R-08, R-17 |
| UI | 네비게이션 바, 컨트롤 | `ui/navigation/`, `ui/controls/` | 탭/뒤로/앞으로/홈/검색바/북마크 | — |
| 인덱싱 모드 | F27 Shallow/Deep/Hybrid | `indexer/service.py:mode` | GUI 토글 동작 | — |
| 테스트 | unit + integration 80% 커버리지 | `tests/unit/`, `tests/integration/` | `pytest --cov-fail-under=80` | — |

**리스크 게이트 G2 (W8)**: 10만 LoC 그래프 60fps? 실패 시 LoD + 뷰포트 컬링 강화.

### Phase 2 — SI DNA Panels (W9~16) → M2 Beta MVP

| 영역 | 작업 | 산출물 | 완료 기준 | 위험 |
|---|---|---|---|---|
| F1 ContextWindow | 라이브 정의 프리뷰 | `ui/panels/context.py` | 심볼 선택 0.2s 내 | R-09 (event loop) |
| F2 SymbolWindow | 파일 아웃라인 | `ui/panels/symbol.py` | 10만 줄 파일 1s 내 | — |
| F3 RelationWindow | Tree/Outline + 다중 + Lock | `ui/panels/relation.py`, `relation_manager.py` | Lock + 다중 정상 | R-09 |
| F4 Editor 강화 | Semantic + Syntax decoration | `ui/editor/{semantic,decoration}.py` | 스코프별 차등 색상 | R-05 |
| EventBus | 패널 간 동기화 | `core/event_bus.py` | 무한 루프 0 (디바운스) | R-09 |

**리스크 게이트 G3 (W16)**: dogfooding 가능? 실패 시 Phase 3로 이월, MVP 연기.

### Phase 3 — Productivity (W17~22) → M3

| 영역 | 작업 | 산출물 | 완료 기준 | 위험 |
|---|---|---|---|---|
| F5 Rename | Rope 래퍼 + 미리보기 | `refactor/rename.py`, `ui/dialogs/rename.py` | Django 회귀 < 1% | R-07 |
| F6 Fuzzy | rapidfuzz 팔레트 | `search/fuzzy.py`, `ui/palette/` | 10만 심볼 < 50ms | — |
| F7 References | DB 역참조 | `search/references.py`, `ui/panels/references.py` | 정확도 100% | — |
| F8 Layouts A~D | 4개 프리셋 | `ui/layouts/` | < 100ms 전환 | — |
| F9 Bookmarks+ | 메모/태그/세트 | `ui/panels/bookmark.py` | JSON export/import | — |
| F10 Clip | 다중 클립보드 | `ui/panels/clip.py` | Placeholder 동작 | — |
| F11 Search Project | Regex/Boolean | `search/service.py`, `ui/panels/search_results.py` | 10만 LoC < 2s | — |

**리스크 게이트 G4 (W22)**: Smart Rename 회귀 < 1%? 실패 시 LibCST 재작성.

### Phase 4 — Python Differentiation (W23~28) → M4 RC

| 영역 | 작업 | 산출물 | 완료 기준 | 위험 |
|---|---|---|---|---|
| F19 TypeHint | typing 해석 + mypy/pyright 옵션 | `indexer/type_hints.py` | unsolved 50% 감소 (G5) | R-11 |
| F20 Duck candidate | opacity 50% 표시 | `indexer/duck.py` | 후보 선택 UI | — |
| F21 Frameworks | Django/Flask/FastAPI/SQLAlchemy 플러그인 | `indexer/frameworks/` | 샘플 시각 확인 | R-10 |
| F22 venv 인식 | venv/poetry/conda 감지 | `core/environment.py` | 필터 토글 | — |
| F23 Jupyter | `.ipynb` 셀 인덱싱 | `indexer/jupyter.py` | `.py` ↔ `.ipynb` 크로스 | — |
| F24 ImportGraph | 모듈 import 전용 뷰 | `ui/graph/import_graph.py` | 순환 탐지 | — |
| F25 Decorator | `@property` 등 배지 | `indexer/decorators.py` | 배지 표시 | — |
| F26 Dynamic import | `importlib` 정적 탐지 | `indexer/dynamic.py` | 점선 회색 엣지 | — |

**리스크 게이트 G5 (W28)**: typed/untyped → unsolved 50% 감소? 실패 시 mypy/pyright 강도 조정.

### Phase 5 — Packaging (W29~31) → M5 v1.0.0

| 영역 | 작업 | 산출물 | 완료 기준 | 위험 |
|---|---|---|---|---|
| F12 Overview Scroller | minimap | `ui/editor/overview.py` | 스크롤 동기 | — |
| F13 Code Folding | 함수/클래스 접기 | `ui/editor/folding.py` | 세션 간 유지 | — |
| F14 Revision Marks | 라인 마진 색상 | `ui/editor/revision.py` | 세션 로컬 추적 | — |
| F15 MFL | 프로젝트 설정 YAML | `core/config.py` | git 체크인 흐름 | — |
| F16 Custom Language | Tree-sitter 플러그인 API | `indexer/frameworks/base.py` 확장 | API 문서 + 샘플 | — |
| F17 Graph Export | PNG/SVG/DOT | `ui/graph/export.py` | 3종 포맷 | — |
| F18 Dir Compare | 디렉터리 diff | `ui/dialogs/dir_compare.py` | 심볼 수준 diff | — |
| 패키징 | PyInstaller + Inno Setup | `scripts/build_installer.ps1` | < 200MB 인스톨러 | R-12, R-13 |

**리스크 게이트 G6 (W31)**: Windows VM에서 설치→실행→인덱싱 성공? 실패 시 release 연기.

### Phase 6 — Testing & Docs (전 기간 지속)

| 영역 | 작업 |
|---|---|
| 테스트 커버리지 80%+ | 매 phase 신기능과 함께 |
| 사용자 매뉴얼 | Phase 5에 집중 |
| Sphinx API docs | 자동 생성 (Phase 0 D2 이후) |
| compat-check fixture 추가 | Phase 4 새 프레임워크마다 |
| bench fixture 유지 | Phase 1+ 정기 갱신 |

## 마일스톤

| Milestone | 주차 | 기준 |
|---|---|---|
| M0 Foundation | 2 | PoC 3종 성공, CI green, db-schema 100% |
| M1 Image Parity (Alpha) | 8 | 첨부 이미지 동일 그래프 UX |
| M2 MVP (Beta) | 16 | SI 4종 패널 완비, dogfooding 가능 |
| M3 Productivity | 22 | Rename/Search/Layouts 실용 |
| M4 Differentiation (RC) | 28 | Django/Jupyter 우위 확보 |
| M5 v1.0.0 | 31 | 인스톨러 배포, 매뉴얼 완비 |

## 위험 / 가정

- 1인 풀타임 0.4~0.6 FTE 가정. 번아웃이 #1 리스크 (R-03).
- bash 스크립트는 Git Bash 또는 WSL 필요 (Windows 머신).
- MVP(W16)까지 범위 축소 금지. 그 후는 유연.
- 본 로드맵은 W4(Phase 1 첫 주말 회고), W8, W16, W22, W28, W31에 갱신.
