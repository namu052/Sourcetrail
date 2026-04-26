# 02 · 아키텍처 — 기술 스택 및 SourcetrailDB 호환 전략

---

## 1. 기술 스택 (확정)

### UI 레이어
| 컴포넌트 | 선택 | 라이선스 | 근거 |
|---------|------|----------|------|
| **UI 프레임워크** | PyQt6 | GPL v3 | QScintilla 바인딩 필수 호환 |
| **에디터 위젯** | QScintilla (PyQt6-QScintilla) | GPL v3 | Scintilla 기반, 가장 성숙, Python 렉서 내장 |
| **그래프 렌더링** | QGraphicsView/Scene | (Qt 포함) | 네이티브 2D 엔진, 성능 우수 |
| **테마/스타일링** | Qt Style Sheets (QSS) | — | 중앙 집중식 스타일링 |

### 분석 레이어
| 컴포넌트 | 선택 | 버전 | 역할 |
|---------|------|------|------|
| **시맨틱 분석** | Jedi | ≥ 0.19.1 | goto/references/completion, 타입 추론 |
| **AST 파서** | Parso | ≥ 0.8.4 | 에러 복원 파서, Jedi 의존성이기도 함 |
| **리팩토링** | Rope | ≥ 1.13 | Smart Rename (F5) |
| **다국어 파싱 대비** | Tree-sitter + tree-sitter-python | ≥ 0.23 | F16 Custom Language 확장용 |
| **퍼지 매칭** | rapidfuzz | ≥ 3.9 | Fuzzy Lookup (F6) |
| **외부 타입 체커** (옵션) | mypy / pyright | 외부 CLI | F19 Type Hint 정밀도 향상 |

### 데이터 레이어
| 컴포넌트 | 선택 | 근거 |
|---------|------|------|
| **DB** | SQLite (stdlib `sqlite3`) | SourcetrailDB 100% 호환 필수 |
| **스키마** | **SourcetrailDB v25** 완전 호환 | 원본 Sourcetrail GUI 열람 보장 |
| **직렬화** | JSON / YAML (PyYAML) | 설정, 레이아웃, 스니펫, MFL |

### 개발 도구
| 항목 | 선택 |
|------|------|
| Python 버전 | **3.12** (고정) |
| 의존성 관리 | **uv** (빠른 설치, lock 파일) |
| 린터/포매터 | ruff (통합) |
| 타입 체커 | mypy (strict 모드) |
| 테스트 | pytest + pytest-qt + pytest-cov |
| 패키징 | PyInstaller + Inno Setup |
| 문서 | Sphinx (API) + Markdown (사용자 매뉴얼) |

---

## 2. 모듈 구조

```
src/sourcetrail_remake/
├── __init__.py
├── __main__.py                # 진입점
│
├── cli/                       # CLI 명령어
│   ├── index.py               # srm-index: 프로젝트 인덱싱
│   └── gui.py                 # srm-gui: GUI 실행
│
├── core/                      # 도메인 모델 + 공통 서비스
│   ├── config.py              # 앱 설정
│   ├── event_bus.py           # 패널 간 동기화 시그널
│   ├── project.py             # 프로젝트 모델
│   ├── environment.py         # venv/poetry 감지
│   └── types.py               # 공용 타입 (NodeId, EdgeId, ...)
│
├── db/                        # SourcetrailDB 호환 레이어
│   ├── schema.py              # 테이블/enum 정의
│   ├── writer.py              # 인덱서용 writer
│   ├── reader.py              # UI용 reader
│   ├── extension.py           # Python 특화 확장 테이블
│   └── compat.py              # 호환성 검증
│
├── indexer/                   # 코드 분석
│   ├── service.py             # IndexerService (최상위)
│   ├── jedi_resolver.py       # Jedi 래퍼
│   ├── parso_walker.py        # Parso AST 순회
│   ├── type_hints.py          # F19 TypeHintResolver
│   ├── duck.py                # F20 DuckTypeCandidateFinder
│   ├── decorators.py          # F25 DecoratorTracker
│   ├── dynamic.py             # F26 DynamicImportDetector
│   ├── jupyter.py             # F23 JupyterIndexer
│   ├── unsolved.py            # Unsolved 트래커
│   └── frameworks/            # F21 플러그인
│       ├── base.py
│       ├── django.py
│       ├── flask.py
│       ├── fastapi.py
│       └── sqlalchemy.py
│
├── refactor/                  # 리팩토링
│   └── rename.py              # F5 Rope 래퍼
│
├── search/                    # 검색 엔진
│   ├── service.py             # SearchService (멀티파일)
│   ├── fuzzy.py               # F6 퍼지 매칭
│   └── references.py          # F7 역참조
│
└── ui/
    ├── main_window.py
    ├── graph/                 # 그래프 뷰 (QGraphicsView)
    │   ├── view.py
    │   ├── scene.py
    │   ├── nodes.py           # NodeRenderer
    │   ├── edges.py           # EdgeRenderer
    │   ├── layout.py          # Sugiyama + force
    │   ├── hover_preview.py
    │   ├── import_graph.py    # F24
    │   └── export.py          # F17
    ├── panels/                # 도킹 패널
    │   ├── context.py         # F1
    │   ├── symbol.py          # F2
    │   ├── relation.py        # F3
    │   ├── relation_manager.py # 다중 Relation
    │   ├── search_results.py  # F11
    │   ├── references.py      # F7
    │   ├── bookmark.py        # F9
    │   └── clip.py            # F10
    ├── editor/                # QScintilla 통합
    │   ├── code_editor.py
    │   ├── semantic.py        # F4 SemanticHighlighter
    │   ├── decoration.py      # F4 Syntax Decoration
    │   ├── overview.py        # F12 Overview Scroller
    │   ├── folding.py         # F13
    │   └── revision.py        # F14
    ├── dialogs/
    │   ├── rename.py          # F5 RenameDialog
    │   ├── dir_compare.py     # F18
    │   └── indexing_mode.py   # F27
    ├── palette/               # F6 Fuzzy Lookup
    ├── layouts/               # F8 Layout Manager
    ├── navigation/            # 탭 바, 히스토리, 검색바
    ├── controls/              # 심도 슬라이더, 줌, 북마크
    └── themes/                # Light/Dark/Custom
```

---

## 3. 레이어 다이어그램

```
┌─────────────────────────────────────────────────────┐
│                   Presentation (UI)                  │
│  ┌──────┐ ┌────────┐ ┌────────┐ ┌──────┐ ┌────────┐ │
│  │Graph │ │Context │ │Symbol  │ │Editor│ │Dialogs │ │
│  │View  │ │Window  │ │Window  │ │      │ │        │ │
│  └──────┘ └────────┘ └────────┘ └──────┘ └────────┘ │
│         ↑           ↑           ↑                    │
│         └───── EventBus (QObject signals) ───────   │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                  Application Layer                   │
│  ┌────────────┐ ┌──────────┐ ┌──────────────┐       │
│  │IndexerSvc  │ │SearchSvc │ │RenameSvc     │       │
│  │(QThread)   │ │          │ │(Rope)        │       │
│  └────────────┘ └──────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                    Domain Layer                      │
│  ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌──────────┐  │
│  │Project  │ │Symbol    │ │Relation │ │Bookmark  │  │
│  └─────────┘ └──────────┘ └─────────┘ └──────────┘  │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                Infrastructure Layer                  │
│  ┌────────────────┐ ┌─────────┐ ┌──────────┐        │
│  │DatabaseWriter  │ │Jedi     │ │Parso     │        │
│  │Reader (SQLite) │ │Resolver │ │Walker    │        │
│  └────────────────┘ └─────────┘ └──────────┘        │
│  ┌────────────────┐ ┌─────────┐                      │
│  │Framework Plug. │ │Rope     │                      │
│  └────────────────┘ └─────────┘                      │
└─────────────────────────────────────────────────────┘
```

**의존성 방향**: UI → Application → Domain → Infrastructure (단방향).
Infrastructure는 Domain을 참조하지 않음.

---

## 4. 데이터 플로우

### 4.1 인덱싱 플로우
```
사용자 "Index" 버튼
    ↓
ProjectService.create_index_job()
    ↓
IndexerService (QThread)
    ├─ EnvironmentInspector (venv 감지)
    ├─ ParsoWalker (top-level 심볼 추출)
    ├─ JediResolver (goto, references, types)
    ├─ TypeHintResolver (F19)
    ├─ DecoratorTracker (F25)
    ├─ DynamicImportDetector (F26)
    ├─ JupyterIndexer (F23, .ipynb만)
    ├─ FrameworkPlugins (F21: Django, Flask, FastAPI, SQLAlchemy)
    └─ UnsolvedSymbolTracker
    ↓
DatabaseWriter (SQLite, SourcetrailDB 호환)
    ├─ node / edge / symbol / file / source_location / occurrence
    └─ [확장] edge_extension (Python 특화 정보)
    ↓
.srctrldb 파일
    ↓
EventBus.emit(indexing_completed)
    ↓
UI 업데이트
```

### 4.2 사용자 인터랙션 플로우
```
그래프 노드 클릭
    ↓
GraphScene.on_node_clicked()
    ↓
EventBus.symbol_selected.emit(node_id)
    ↓
[여러 패널이 동시 반응]
    ├─ ContextWindow → DatabaseReader.get_definition() → 프리뷰 렌더링
    ├─ SymbolWindow → 해당 심볼의 부모 파일 심볼 트리 표시
    ├─ RelationWindow (unlocked) → 해당 심볼 중심 관계 재렌더링
    └─ Editor → 정의 파일 열기 + 해당 라인 점프
```

---

## 5. SourcetrailDB 100% 호환 전략

### 5.1 호환성 원칙
**원본 Sourcetrail Windows GUI에서 에러 없이 열람 가능해야 한다.**

### 5.2 스키마 준수 범위

반드시 원본과 동일하게 유지할 테이블·컬럼·enum:

| 테이블 | 상태 |
|--------|------|
| `meta` | 그대로 유지 (DB 버전, 인덱서 정보) |
| `node` | 그대로 (id, type, serialized_name) |
| `edge` | 그대로 (id, type, source_node_id, target_node_id) |
| `symbol` | 그대로 (id, definition_kind) |
| `file` | 그대로 |
| `source_location` | 그대로 |
| `occurrence` | 그대로 |
| `local_symbol` | 그대로 |
| `component_access` | 그대로 |
| `error` | 그대로 |
| `node_file` | 그대로 |

enum 값 (`node_type`, `edge_type`, `symbol_definition_kind`, `source_location_type`, `access_kind`)은 원본 C++ 헤더 파일과 **1:1 일치**.

### 5.3 Python 특화 확장 전략 — **확장 테이블 방식**

Phase 4에서 추가되는 Python 특화 엣지 종류(Django ORM, FastAPI route, dynamic import 등)는 원본 `edge_type` enum에 없다.

**원칙**: 원본 스키마 **미훼손**.

**구현**: `edge_extension` 별도 테이블에 확장 정보 저장.

```sql
-- 우리가 추가하는 확장 테이블 (원본 Sourcetrail은 이 테이블을 무시)
CREATE TABLE IF NOT EXISTS edge_extension (
    edge_id INTEGER NOT NULL,
    kind TEXT NOT NULL,          -- 'django_fk', 'fastapi_route', 'dynamic_import', 'duck_candidate'
    metadata TEXT,               -- JSON
    FOREIGN KEY (edge_id) REFERENCES edge(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_edge_extension_edge_id ON edge_extension(edge_id);

-- Unsolved symbol 추가 메타 (노드 특화)
CREATE TABLE IF NOT EXISTS node_extension (
    node_id INTEGER NOT NULL,
    kind TEXT NOT NULL,          -- 'unsolved', 'duck_typing_candidate', 'jupyter_cell'
    confidence REAL,             -- 0.0-1.0
    metadata TEXT,               -- JSON
    FOREIGN KEY (node_id) REFERENCES node(id) ON DELETE CASCADE
);
```

엣지 매핑:
- Django ORM 관계 → 원본 `edge_type = USAGE` + `edge_extension.kind = 'django_fk'`
- FastAPI route → 원본 `edge_type = CALL` + `edge_extension.kind = 'fastapi_route'`
- Dynamic import → 원본 `edge_type = IMPORT` + `edge_extension.kind = 'dynamic_import'`

### 5.4 호환성 검증 자동화

```
scripts/compatibility_check.py

1. 샘플 프로젝트 인덱싱 → .srctrldb 생성
2. 원본 Sourcetrail CLI 또는 GUI headless로 DB 로드
3. 로드 성공 여부 확인
4. 노드/엣지 개수 일치 여부 확인
5. 레포트 생성
```

매 Phase 종료 시, 릴리스 전 필수 실행.

---

## 6. 이벤트 버스 설계

```python
# src/sourcetrail_remake/core/event_bus.py
class EventBus(QObject):
    # 심볼 관련
    symbol_selected = pyqtSignal(object)         # NodeId
    symbol_hovered = pyqtSignal(object)          # NodeId
    symbol_deselected = pyqtSignal()

    # 파일/에디터
    file_opened = pyqtSignal(object)             # Path
    file_closed = pyqtSignal(object)
    cursor_moved = pyqtSignal(object, int, int)  # Path, line, col

    # 인덱싱
    indexing_started = pyqtSignal(object)        # ProjectId
    indexing_progress = pyqtSignal(int, int)     # current, total
    indexing_completed = pyqtSignal(object)
    indexing_failed = pyqtSignal(str)

    # 패널 제어
    relation_lock_toggled = pyqtSignal(int, bool) # window_id, locked
    context_follow_toggled = pyqtSignal(bool)
    layout_changed = pyqtSignal(str)              # 'A' | 'B' | 'C' | 'D'

    # 북마크/클립
    bookmark_added = pyqtSignal(object)
    clip_added = pyqtSignal(str)
```

**핵심 철학**: Source Insight의 "항상 동기화" UX를 **패널 간 느슨한 결합 + 시그널 기반 이벤트**로 구현.

---

## 7. 인덱싱 모드 아키텍처 (F27)

### Shallow 모드
- Parso AST만 사용 (top-level 이름 기반 매칭)
- Jedi 호출 최소화 → 속도 극대화
- 정확도: 이름 기반 매칭만, 참조 해결 시 미해결 발생 많음

### Deep 모드
- Jedi 완전 분석 (`goto()`, `infer()`, `get_references()`)
- 느리지만 정확
- 모든 참조 해결 시도

### Hybrid 모드 (권장 기본값)
- 초기 인덱싱은 Shallow
- 사용자가 탐색한 서브트리만 on-demand로 Deep 재분석
- 결과 캐싱

```python
class IndexerService:
    def __init__(self, mode: Literal['shallow', 'deep', 'hybrid']):
        ...

    def index(self) -> None:
        if self.mode == 'shallow':
            self._index_shallow()
        elif self.mode == 'deep':
            self._index_deep()
        else:  # hybrid
            self._index_shallow()
            # Deep 분석은 on-demand로 별도 호출

    def refine_subtree(self, root_node_id: NodeId) -> None:
        """Hybrid 모드에서 특정 서브트리만 Deep 재분석."""
```

---

## 8. 프레임워크 플러그인 아키텍처 (F21)

```python
# src/sourcetrail_remake/indexer/frameworks/base.py
from abc import ABC, abstractmethod

class FrameworkPlugin(ABC):
    name: ClassVar[str]

    @abstractmethod
    def detect(self, project_root: Path, env: Environment) -> bool:
        """프로젝트에 이 프레임워크가 있는지 판단."""

    @abstractmethod
    def enhance(self, indexed_symbol: IndexedSymbol, writer: DatabaseWriter) -> None:
        """Jedi 분석 후 추가 엣지/메타데이터 기입."""
```

내장 플러그인:
- `DjangoPlugin` — models, urls
- `FlaskPlugin` — @app.route, @blueprint.route
- `FastAPIPlugin` — @app.get/post, Depends
- `SQLAlchemyPlugin` — relationship, Mapped

**확장성**: `entry_points = "sourcetrail_remake.plugins"` 로 서드파티 플러그인 허용 (Phase 5 F16과 연결).

---

## 9. 성능 최적화 전략

| 지점 | 전략 |
|------|------|
| 인덱싱 | QThread 백그라운드, 증분 파싱 |
| 그래프 렌더링 | QGraphicsView 뷰포트 컬링, LoD (zoom level별 단순화) |
| DB 쿼리 | SQLite WAL 모드, 인덱스 추가, prepared statement 재사용 |
| 파일 모니터링 | watchdog (optional), 변경 시 해당 파일만 재인덱싱 |
| Fuzzy Lookup | 인메모리 trie 또는 rapidfuzz 내부 인덱스 |
| Context Window | Jedi 결과 LRU 캐시 |
| 심볼 DB 로드 | lazy loading (필요한 노드만 DB에서 읽기) |

---

## 10. 보안 & 안정성

- **경로 입력 검증**: 프로젝트 루트 경로의 탈출 공격 방지 (`..` 정규화)
- **SQL 안전성**: 모든 쿼리 파라미터화 (문자열 연결 금지)
- **예외 처리**: 백그라운드 스레드 예외는 EventBus로 UI에 전달
- **크래시 복구**: 세션 상태 자동 저장 (레이아웃, 열린 탭, 북마크)
- **하드코딩 시크릿 금지**: 설정은 사용자 홈 디렉터리 (`%APPDATA%/Sourcetrail_Remake/`)

---

## 11. 배포 아키텍처

```
PyInstaller (One-folder 모드)
    ↓
dist/Sourcetrail_Remake/
    ├─ sourcetrail_remake.exe
    ├─ PyQt6/ (DLLs)
    ├─ PyQt6/Qsci/ (QScintilla)
    ├─ jedi/, parso/, rope/ (순수 Python)
    ├─ _internal/
    └─ ...
    ↓
Inno Setup
    ↓
Sourcetrail_Remake_Setup_1.0.0.exe (~150MB)
    ├─ 시작 메뉴 바로가기
    ├─ 파일 연관 (.srctrldb)
    ├─ Microsoft VC++ Redistributable 번들
    └─ 제거 프로그램
```

---

## 12. 확장 포인트 (v1.1+ 대비)

현재 v1.0.0 범위에는 없으나 아키텍처가 지원해야 할 미래 확장:

- **LSP 서버 모드**: 별도 프로세스로 LSP 응답 제공 → VS Code 확장 연동
- **웹 UI**: Qt → PySide6 with QtWebEngine 또는 별도 Flask 백엔드
- **추가 언어**: Tree-sitter 플러그인으로 Go/Rust/TypeScript
- **AI 설명**: LLM 통합 (선택적, 로컬 또는 API 키 사용)

이들은 현재 플러그인 아키텍처(F16, F21 패턴)를 재활용 가능하도록 설계.
