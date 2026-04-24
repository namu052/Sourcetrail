# Phase 0 · 프로젝트 셋업 · 역공학 · PoC

| 메타 | 값 |
|------|-----|
| 기간 | **2주 (Week 1-2)** |
| 누적 | 2주 |
| 마일스톤 | **M0 — Foundation** |
| 선행 조건 | 없음 (프로젝트 시작) |
| 목표 | 개발 기반 구축 + 핵심 기술 불확실성 제거 |

---

## 목표

1. **레포 기반 구축** — 구조, CI, 린트, 문서 골격
2. **SourcetrailDB 역공학** — 100% 호환 구현을 위한 스키마 완전 문서화
3. **기술 PoC 3종** — Jedi 인덱싱 / QScintilla 에디터 / QGraphicsView 그래프

Phase 0을 통과하면 **기술 리스크가 충분히 낮아져 Phase 1을 자신있게 시작** 할 수 있어야 한다.

---

## 산출물 (Deliverables)

| # | 산출물 | 위치 |
|---|--------|------|
| D0.1 | 레포 구조 및 빌드 시스템 | `pyproject.toml`, `src/sourcetrail_remake/` |
| D0.2 | Windows CI 파이프라인 | `.github/workflows/ci.yml` |
| D0.3 | pre-commit 설정 | `.pre-commit-config.yaml` |
| D0.4 | 개발자 문서 | `docs/DEVELOPMENT.md`, `docs/ARCHITECTURE.md` |
| D0.5 | **SourcetrailDB 스키마 역공학 보고서** | `docs/db-schema.md` |
| D0.6 | **PoC 1**: Jedi → SourcetrailDB → 원본 GUI 열람 | `poc/01_jedi_to_sqlite/` |
| D0.7 | **PoC 2**: PyQt6 + QScintilla Hello Editor | `poc/02_editor_hello/` |
| D0.8 | **PoC 3**: QGraphicsView Hello Graph (이미지 모사) | `poc/03_graph_hello/` |
| D0.9 | Phase 1 세부 WBS | `docs/plan/phase-1-wbs-detail.md` |

---

## 주간 작업 계획

### Week 1 — 기반 구축 (D1-D5)

| 일 | 작업 | 산출물 |
|----|------|--------|
| **D1** | 레포 구조 설계, `pyproject.toml` 작성 | 디렉터리 트리 |
| D1 | Python 3.12 + uv 환경 셋업 | `uv.lock` |
| **D2** | 의존성 고정 (PyQt6, QScintilla, Jedi, Parso, Rope, ...) | `pyproject.toml` 완료 |
| D2 | GitHub Actions CI (Windows runner) | `.github/workflows/ci.yml` |
| D2 | pre-commit 설정 (ruff, mypy, ...) | `.pre-commit-config.yaml` |
| **D3** | 개발자 문서 초안 | `DEVELOPMENT.md`, `ARCHITECTURE.md` |
| D3 | 원본 Sourcetrail Windows 빌드 다운로드/설치 | 호환성 baseline |
| **D4-D5** | SourcetrailDB 역공학 Part 1 | `db-schema.md` 테이블 스키마 |

### Week 2 — 역공학 완료 & PoC (D6-D10)

| 일 | 작업 | 산출물 |
|----|------|--------|
| **D6-D7** | SourcetrailDB 역공학 Part 2 | enum 전체, 확장 테이블 설계 |
| **D8** | PoC 1: Jedi → SQLite → 원본 GUI 열람 | `poc/01_jedi_to_sqlite/` |
| **D9** | PoC 2: PyQt6 + QScintilla Hello Editor | `poc/02_editor_hello/` |
| **D10** | PoC 3: QGraphicsView 3-노드 그래프 | `poc/03_graph_hello/` |
| D10 | Phase 1 WBS 확정 | `phase-1-wbs-detail.md` |

---

## 레포 구조 (결정)

```
Sourcetrail_Remake/
├── .github/workflows/ci.yml
├── .pre-commit-config.yaml
├── pyproject.toml
├── uv.lock
├── README.md
├── LICENSE                        # GPL v3
├── CHANGELOG.md
├── CONTRIBUTING.md
│
├── docs/
│   ├── DEVELOPMENT.md
│   ├── ARCHITECTURE.md
│   ├── db-schema.md               # ← Phase 0 핵심 산출물
│   ├── plan/                      # ← 현재 이 폴더
│   ├── exec-plans/
│   │   ├── active/
│   │   └── completed/
│   └── user-manual/               # Phase 5에 작성
│
├── src/
│   └── sourcetrail_remake/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli/
│       ├── core/
│       ├── db/
│       ├── indexer/
│       ├── refactor/
│       ├── search/
│       └── ui/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── ui/
│   ├── compatibility/
│   ├── performance/
│   └── fixtures/
│
├── poc/
│   ├── 01_jedi_to_sqlite/
│   ├── 02_editor_hello/
│   └── 03_graph_hello/
│
└── scripts/
    ├── bench.py
    ├── compatibility_check.py
    └── build_installer.ps1        # Phase 5
```

---

## 의존성 명세 (pyproject.toml)

```toml
[project]
name = "sourcetrail-remake"
version = "0.1.0"
description = "Python code analysis tool — Sourcetrail graph + Source Insight UX"
requires-python = ">=3.12,<3.13"
license = { text = "GPL-3.0-only" }
dependencies = [
    # UI
    "PyQt6>=6.7,<7",
    "PyQt6-QScintilla>=2.14",
    # 분석
    "jedi>=0.19.1,<0.20",
    "parso>=0.8.4",
    "rope>=1.13",
    # 확장 파서 (Phase 5)
    "tree-sitter>=0.23",
    "tree-sitter-python>=0.23",
    # 유틸
    "rapidfuzz>=3.9",
    "PyYAML>=6",
    "nbformat>=5.10",              # F23 Jupyter
    "watchdog>=4",                 # 파일 모니터링
]

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "pytest-qt>=4.4",
    "pytest-cov>=5",
    "ruff>=0.6",
    "mypy>=1.11",
    "pre-commit>=3.8",
    "sphinx>=7",
    "sphinx-rtd-theme",
]

[project.scripts]
srm = "sourcetrail_remake.__main__:main"
srm-index = "sourcetrail_remake.cli.index:main"
srm-gui = "sourcetrail_remake.cli.gui:main"

[tool.ruff]
target-version = "py312"
line-length = 100

[tool.mypy]
python_version = "3.12"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--strict-markers --cov=sourcetrail_remake --cov-report=term-missing"
```

---

## CI 파이프라인 (Phase 0 버전)

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  lint:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --all-extras
      - run: uv run ruff check
      - run: uv run ruff format --check
      - run: uv run mypy src/

  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --all-extras
      - run: uv run pytest
      # 커버리지 게이트는 Phase 1 이후 적용 (--cov-fail-under=80)
```

---

## SourcetrailDB 스키마 역공학 범위

**반드시 100% 호환**되어야 할 테이블:

| 테이블 | 목적 | 주요 컬럼 |
|--------|------|----------|
| `meta` | DB 버전, 인덱서 정보 | key, value |
| `node` | 심볼 노드 | id, type, serialized_name |
| `edge` | 관계 | id, type, source_node_id, target_node_id |
| `symbol` | 심볼 메타 | id, definition_kind |
| `file` | 소스 파일 | id, path, language, ... |
| `source_location` | 위치 | id, file_id, start_line, start_column, end_line, end_column, type |
| `occurrence` | 출현 | element_id, source_location_id |
| `local_symbol` | 파일 스코프 심볼 | id, name |
| `component_access` | 접근 수준 | node_id, type (public/protected/private) |
| `error` | 인덱싱 에러 | id, message, fatal, indexed, translation_unit |
| `node_file` | 노드-파일 매핑 | node_id, file_id |

### enum 매핑 (원본 C++ 헤더 참조)

- `NodeType` (class, function, method, field, ...)
- `EdgeType` (USAGE, CALL, INHERITANCE, IMPORT, ...)
- `SymbolDefinitionKind` (explicit, implicit)
- `SourceLocationType` (token, scope, signature, ...)
- `AccessKind` (public, protected, private, default)

### Sourcetrail_Remake 추가 테이블 (확장)

**원본 스키마 미훼손 원칙에 따라 별도 테이블**:

```sql
CREATE TABLE edge_extension (
    edge_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
    metadata TEXT,
    FOREIGN KEY (edge_id) REFERENCES edge(id) ON DELETE CASCADE
);

CREATE TABLE node_extension (
    node_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
    confidence REAL,
    metadata TEXT,
    FOREIGN KEY (node_id) REFERENCES node(id) ON DELETE CASCADE
);
```

---

## PoC 수락 기준

### PoC 1 — Jedi → SourcetrailDB → 원본 GUI 열람
**목표**: 핵심 호환성 리스크(R-02) 조기 제거.

- [ ] 샘플 Python 파일 (~100줄, 클래스 3, 함수 10) 준비
- [ ] Jedi로 심볼 추출 → SQLite 테이블에 기입
- [ ] **원본 Sourcetrail Windows GUI에서 에러 없이 DB 열림**
- [ ] 그래프 뷰에서 노드/엣지 정상 렌더링
- [ ] 최소 1개 unsolved symbol 생성 확인

### PoC 2 — PyQt6 + QScintilla Hello Editor
**목표**: 에디터 위젯 통합 리스크(R-06) 제거.

- [ ] `QsciScintilla` 위젯 표시
- [ ] 파일 열기/저장 동작
- [ ] Python 렉서 하이라이팅 (키워드/문자열/주석)
- [ ] 줄 번호 마진, 폴딩 마진 표시
- [ ] 마우스 커서 아래 식별자 좌표/텍스트 획득 가능

### PoC 3 — QGraphicsView Hello Graph
**목표**: 그래프 렌더링 가능성(R-04) 확인.

- [ ] 첨부 이미지의 3-컨테이너 노드 (SessionManager / Session / unsolved) 수동 렌더링
- [ ] 멤버 노드 5종 (get_session, cleanup_expired, last_active, is_expired, unsolved)
- [ ] 실선 오렌지 / 점선 블루 엣지 구분
- [ ] 회색 해치 패턴 (unsolved 노드)
- [ ] 줌 ± 및 팬 조작 작동
- [ ] 60fps 유지 (상대적으로 적은 노드지만 기준 확인)

---

## 개발 환경 준비 체크리스트

**시작 전 필요 사항**:
- [ ] Windows 10/11 머신
- [ ] Python 3.12 설치 및 `python --version` 확인
- [ ] `uv` 설치 (`pip install uv` 또는 공식 스크립트)
- [ ] Git 설정 완료 (user.name, user.email)
- [ ] GitHub 레포 접근 권한
- [ ] **원본 Sourcetrail Windows 빌드** 다운로드 (호환성 테스트용)
- [ ] Windows SDK 또는 Visual Studio Build Tools (QScintilla 휠 빌드 실패 대비)
- [ ] IDE (VS Code / PyCharm) 설정

**에디터 권장 확장**:
- Python (Pylance)
- ruff (VS Code 확장)
- mypy
- GitLens
- Markdown All in One

---

## Phase 0 DoD (Definition of Done)

- [ ] `uv run python -m sourcetrail_remake` 으로 빈 `QMainWindow` 기동
- [ ] Windows CI가 **lint + type-check + empty tests** 모두 green
- [ ] `docs/db-schema.md`에 **모든 테이블 + enum 100% 문서화**
- [ ] PoC 3종 모두 스크린샷과 함께 수락 기준 통과
- [ ] `phase-1-wbs-detail.md` 작성 완료 (주 단위 → 일 단위 분해)
- [ ] **리스크 게이트 G1 통과**: PoC 1 성공 (원본 GUI 열람 성공)
- [ ] Phase 0 회고 문서 작성

---

## Phase 0 리스크

| 리스크 | 등급 | 대응 |
|--------|------|------|
| R-06 QScintilla 빌드 실패 | 🟡 | Python 3.11로 다운그레이드 검토 |
| R-14 SourcetrailDB 문서 부재 | 🟢 | 원본 C++ 소스 직접 리딩 |
| PoC 1 실패 (R-02 연관) | 🔴 | 즉시 원본 Sourcetrail 소스 심층 분석, 필요 시 Phase 0 연장 |

---

## 회고 (Phase 종료 후 작성)

> 이 섹션은 Phase 0 종료 시 채운다.

**잘 된 점**:
-

**어려웠던 점**:
-

**다음 Phase로 이월된 항목**:
-

**타임라인 대비 실적**:
- 계획: 2주 / 실제: ?주

**배운 점 (Phase 1에 반영)**:
-
