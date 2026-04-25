---
title: Phase 0 Setup and PoC
status: Active
last_updated: 2026-04-25
---

# Phase 0 — 프로젝트 셋업 & 기술 PoC

| 메타 | 값 |
|------|-----|
| 기간 | 2주 (Week 1-2) |
| 누적 | 2주 |
| 상태 | 📋 계획됨 |
| 마일스톤 | M0 — Foundation |

## 목표

개발 기반 마련 + 핵심 기술 3종의 실현 가능성 검증.

- 레포 구조·CI·문서 골격 완성
- SourcetrailDB SQLite 스키마 **완전 역공학**
- 핵심 기술 스택(Jedi, PyQt6+QScintilla, QGraphicsView)에서 PoC 성공

## 산출물 (Deliverables)

| # | 산출물 | 위치 |
|---|--------|------|
| D0.1 | 레포 구조 및 빌드 시스템 | `pyproject.toml`, `src/sourcetrail_remake/` |
| D0.2 | Windows CI 파이프라인 | `.github/workflows/ci.yml` |
| D0.3 | 개발자 문서 3종 | `docs/DEVELOPMENT.md`, `docs/ARCHITECTURE.md`, `docs/db-schema.md` |
| D0.4 | SourcetrailDB 스키마 역공학 보고서 | `docs/db-schema.md` (완성본) |
| D0.5 | PoC 1: Jedi → SourcetrailDB | `poc/01_jedi_to_sqlite/` |
| D0.6 | PoC 2: PyQt6 + QScintilla Hello Editor | `poc/02_editor_hello/` |
| D0.7 | PoC 3: QGraphicsView Hello Graph (이미지 모사) | `poc/03_graph_hello/` |
| D0.8 | Phase 1 세부 WBS | `docs/exec-plans/active/phase-1-wbs.md` |

## 주간 작업 계획

### Week 1 — 기반 구축

| 일 | 작업 | 상세 |
|----|------|------|
| D1 | 레포 구조 설계 | `src/sourcetrail_remake/{indexer,ui,db,core,cli}/`, `tests/`, `poc/`, `docs/` |
| D1 | `pyproject.toml` 작성 | uv 기반, Python 3.12 고정 |
| D2 | 의존성 고정 | PyQt6, QScintilla, Jedi, Parso, Rope, rapidfuzz, pytest, pytest-qt, ruff, mypy |
| D2 | GitHub Actions CI | Windows runner, 린트+타입체크+테스트 |
| D2 | pre-commit 설정 | `.pre-commit-config.yaml` (ruff, black, mypy, end-of-file-fixer) |
| D3 | 개발자 문서 초안 | `DEVELOPMENT.md` (빌드/실행/테스트), `ARCHITECTURE.md` (레이어 다이어그램) |
| D4-D5 | SourcetrailDB 스키마 역공학 Part 1 | 테이블 스키마 (node, edge, symbol, file) |

### Week 2 — 검증 & PoC

| 일 | 작업 | 상세 |
|----|------|------|
| D6-D7 | SourcetrailDB 스키마 역공학 Part 2 | enum 값 전체, source_location, occurrence, local_symbol, component_access, meta, error |
| D7 | 원본 Sourcetrail Windows 빌드 설치 | 호환성 baseline 확보 |
| D8 | **PoC 1**: Jedi → SQLite → 원본 GUI 열람 | 단일 Python 파일 → DB 생성 → 원본 Sourcetrail GUI에서 열기 성공 |
| D9 | **PoC 2**: PyQt6 + QScintilla Hello Editor | Python 렉서, 파일 열기/저장, 기본 하이라이팅 |
| D10 | **PoC 3**: QGraphicsView 3-노드 그래프 | 이미지의 SessionManager/Session/unsolved 수동 렌더링, 실선/점선 엣지 |
| D10 | Phase 1 WBS 확정 | 주 단위 작업 분해 |

## 레포 구조 (결정)

```
Sourcetrail_Remake/
├── .github/workflows/ci.yml
├── .pre-commit-config.yaml
├── pyproject.toml
├── README.md
├── LICENSE (GPL v3)
├── docs/
│   ├── DEVELOPMENT.md
│   ├── ARCHITECTURE.md
│   ├── db-schema.md
│   └── exec-plans/
├── src/
│   └── sourcetrail_remake/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli/              # srm-index, srm-gui
│       ├── core/             # 도메인 모델, 설정
│       ├── db/               # SourcetrailDB 호환 writer/reader
│       ├── indexer/          # Jedi/Parso 래퍼
│       └── ui/
│           ├── main_window.py
│           ├── graph/        # QGraphicsView 그래프 뷰
│           ├── panels/       # Context/Symbol/Relation/Search
│           └── editor/       # QScintilla 통합
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
└── poc/
    ├── 01_jedi_to_sqlite/
    ├── 02_editor_hello/
    └── 03_graph_hello/
```

## 의존성 (결정)

```toml
[project]
name = "sourcetrail-remake"
version = "0.1.0"
requires-python = ">=3.12,<3.13"
license = { text = "GPL-3.0-only" }
dependencies = [
    "PyQt6>=6.7",
    "PyQt6-QScintilla>=2.14",
    "jedi>=0.19.1",
    "parso>=0.8.4",
    "rope>=1.13",
    "rapidfuzz>=3.9",
    "tree-sitter>=0.23",
    "tree-sitter-python>=0.23",
]

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "pytest-qt>=4.4",
    "pytest-cov>=5",
    "ruff>=0.6",
    "mypy>=1.11",
    "pre-commit>=3.8",
]
```

## SourcetrailDB 스키마 역공학 범위

반드시 **100% 호환**되어야 할 테이블과 컬럼:

| 테이블 | 목적 |
|--------|------|
| `meta` | DB 버전, 인덱서 정보 |
| `node` | 심볼 노드 (class, function, variable, ...) |
| `edge` | 관계 (call, inheritance, usage, ...) |
| `symbol` | 심볼 메타데이터 (definition kind) |
| `file` | 소스 파일 정보 |
| `source_location` | 파일 내 위치 (line, column range) |
| `occurrence` | 심볼의 파일 내 출현 (source_location + node 연결) |
| `local_symbol` | 파일 스코프 심볼 (지역 변수 등) |
| `component_access` | public/protected/private |
| `error` | 인덱싱 에러 |
| `node_file` | 노드-파일 매핑 |

enum 값 (`node_type`, `edge_type`, `symbol_definition_kind` 등)은 원본 헤더 파일과 1:1 일치시킬 것.

## PoC 수락 기준 (Definition of Done)

### PoC 1 — Jedi → SourcetrailDB
- [ ] 샘플 Python 파일 (~100 줄, 클래스 3개, 함수 10개)에서 모든 심볼 추출
- [ ] SQLite DB 생성 후 원본 Sourcetrail GUI에서 **에러 없이 열림**
- [ ] 그래프 뷰에서 노드/엣지 정상 렌더링
- [ ] 최소 1개의 unsolved symbol 레코드 생성 확인

### PoC 2 — PyQt6 + QScintilla
- [ ] 파일 열기/저장 동작
- [ ] Python 렉서 적용 (키워드/문자열/주석 색상)
- [ ] 줄 번호, 폴딩 마진 표시
- [ ] 마우스 커서 아래 식별자 좌표 획득 (추후 Context Window 연동 기반)

### PoC 3 — QGraphicsView Hello Graph
- [ ] SessionManager/Session/unsolved 3-컨테이너 노드 렌더링
- [ ] 멤버 노드 5종 (get_session, cleanup_expired, last_active, is_expired, unsolved)
- [ ] 실선 오렌지 / 점선 블루 엣지 구분
- [ ] 줌 ± 및 팬 조작 작동

## Phase 0 종료 기준 (DoD)

- [ ] `uv run python -m sourcetrail_remake` 으로 빈 `QMainWindow` 기동
- [ ] Windows CI가 린트+타입체크+빈 테스트 통과
- [ ] `docs/db-schema.md`에 모든 테이블/enum 문서화
- [ ] PoC 3종 스크린샷 `docs/poc-results.md`에 기록
- [ ] `phase-1-wbs.md` 작성 완료

## 위험 & 완화

| 위험 | 대응 |
|------|------|
| SourcetrailDB 스키마 문서 부재 | 원본 C++ 소스 직접 리딩 + 샘플 DB 역공학 병행 |
| QScintilla 바인딩 이슈 (PyQt6-QScintilla) | PyPI 버전 고정, Windows 휠 우선 |
| Jedi 0.19+ 호환성 | 가상환경에서 격리 테스트, 최소 지원 버전 명시 |
| 1인 풀타임 번아웃 예방 | 주 40시간 상한, 주말 작업 금지 |

## 착수 전 체크리스트

- [ ] Python 3.12 설치 (Windows)
- [ ] uv 설치 (`pip install uv` 또는 공식 설치 스크립트)
- [ ] Git 설정 확인
- [ ] 원본 Sourcetrail Windows 빌드 다운로드 (호환성 테스트용)
- [ ] Windows SDK (QScintilla 휠 빌드 실패 대비)

## 회고 (Phase 종료 후 작성)

> Phase 0 종료 시 이 섹션을 채우고 파일을 `completed/`로 이동.

- 잘 된 점:
- 어려웠던 점:
- 다음 Phase로 이월된 항목:
- 타임라인 대비 실적:
