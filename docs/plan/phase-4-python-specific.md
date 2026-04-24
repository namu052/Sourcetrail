# Phase 4 · Python 특화 기능 (P5 차별화)

| 메타 | 값 |
|------|-----|
| 기간 | **6주 (Week 23-28)** |
| 누적 | 28주 |
| 마일스톤 | **M4 — Differentiation** (RC2 릴리스) |
| 선행 조건 | Phase 3 RC1 완료, G4 통과 |

---

## 목표

원본 Sourcetrail 의 일반 기능을 뛰어넘는 **Python 전용 지능형 기능**을 구현한다.
"이 도구를 쓰려고 Python 프로젝트를 이동할 이유"를 만든다.

---

## 다루는 기능 (P5)

### F19 — Type Hint Inference Boost
- PEP 484/585/604 타입 힌트 적극 활용
- Jedi + `typing` 모듈 기반 추론
- 힌트 있는 심볼은 solved, 없는 것은 unsolved 유지
- 힌트 품질 메트릭 (프로젝트 커버리지 %)

### F20 — Duck Typing Analyzer
- mypy / pyright 통합 (옵션)
- 구조적 호환성 추론 (`Protocol`, `Structural subtyping`)
- 비교 뷰 (Jedi 단독 vs + mypy) — 얼마나 많은 unsolved가 solved로 전환되는지

### F21 — Framework Plugins (Django / Flask / FastAPI / SQLAlchemy)
- URL ↔ View 매핑 그래프 (Django)
- Blueprint 라우트 맵 (Flask)
- Dependency Injection 체인 (FastAPI)
- Model ↔ Table 매핑 (SQLAlchemy)
- 플러그인 아키텍처 — ABC 기반

### F22 — Virtualenv / Poetry / uv Auto-detection
- 프로젝트 루트에서 `.venv/`, `poetry.lock`, `uv.lock`, `Pipfile.lock` 스캔
- 환경 자동 선택 UI
- 환경 변경 시 재인덱싱

### F23 — Jupyter Notebook (.ipynb) 지원
- 셀별 파싱 (nbformat)
- 셀 간 심볼 참조 추적
- 매직 커맨드 처리 (`%%time`, `%matplotlib` 등)

### F24 — Import Graph
- 모듈 간 의존 그래프 (순환 import 감지)
- 레이어 위반 경고 (사용자 정의 레이어)
- 노드 = 모듈, 엣지 = import

### F25 — Decorator Analyzer
- `@property`, `@staticmethod`, `@classmethod`, `@cached_property`
- 커스텀 데코레이터 (`@app.route`, `@pytest.fixture` 등) 메타데이터 추출
- 그래프에 아이콘 표시

### F26 — Dynamic Import Tracker
- `importlib.import_module` 호출 탐지
- `__import__` 호출 탐지
- 문자열 상수 기반 추론 ("best effort")

### F27 — Shallow / Deep / Hybrid 인덱싱 모드
- Shallow: 이름 + 선언만 (1만 LoC < 1분)
- Deep: Jedi 완전 분석 (1만 LoC < 3분)
- **Hybrid**: 수정된 파일만 Deep, 나머지 Shallow (기본 모드)

---

## 산출물 (Deliverables)

| # | 산출물 | 위치 |
|---|--------|------|
| D4.1 | `TypeHintExtractor` | `src/sourcetrail_remake/indexer/type_hint.py` |
| D4.2 | `MypyIntegration` (optional) | `src/sourcetrail_remake/indexer/mypy_bridge.py` |
| D4.3 | `PyrightIntegration` (optional) | `src/sourcetrail_remake/indexer/pyright_bridge.py` |
| D4.4 | `FrameworkPlugin` ABC | `src/sourcetrail_remake/indexer/plugins/__init__.py` |
| D4.5 | `DjangoPlugin` | `src/sourcetrail_remake/indexer/plugins/django.py` |
| D4.6 | `FlaskPlugin` | `src/sourcetrail_remake/indexer/plugins/flask.py` |
| D4.7 | `FastAPIPlugin` | `src/sourcetrail_remake/indexer/plugins/fastapi.py` |
| D4.8 | `SQLAlchemyPlugin` | `src/sourcetrail_remake/indexer/plugins/sqlalchemy.py` |
| D4.9 | `EnvDetector` | `src/sourcetrail_remake/indexer/env_detect.py` |
| D4.10 | `JupyterParser` | `src/sourcetrail_remake/indexer/jupyter.py` |
| D4.11 | `ImportGraphBuilder` | `src/sourcetrail_remake/indexer/import_graph.py` |
| D4.12 | `DecoratorAnalyzer` | `src/sourcetrail_remake/indexer/decorator.py` |
| D4.13 | `DynamicImportTracker` | `src/sourcetrail_remake/indexer/dynamic_import.py` |
| D4.14 | `HybridIndexer` (파일 변경 감지) | `src/sourcetrail_remake/indexer/hybrid.py` |
| D4.15 | Framework 뷰 (URL↔View 맵 등) | `src/sourcetrail_remake/ui/panels/framework_view.py` |

---

## 주간 작업 계획

### Week 23: Type Hint & Environment

- D111: `TypeHintExtractor` — `ast.AnnAssign`, `FunctionDef.returns`, `arg.annotation` 파싱
- D112: Jedi 추론 결과와 힌트 병합 (힌트 우선)
- D113: 힌트 커버리지 메트릭 (파일별 %, 프로젝트 전체 %)
- D114: `EnvDetector` — `.venv`, `poetry.lock`, `uv.lock` 순차 탐지
- D115: 환경 선택 다이얼로그 + 재인덱싱 훅

### Week 24: Duck Typing (mypy/pyright 통합)

- D116: `MypyIntegration` — subprocess 호출, JSON 출력 파싱 (`--output-format=json`)
- D117: `PyrightIntegration` — subprocess 호출, LSP-style 결과 파싱
- D118: 옵션 플래그 (`--with-mypy`, `--with-pyright`)
- D119: unsolved → solved 변환 통계 뷰
- D120: 느린 경우 QThread + 캔슬 가능

### Week 25: Framework Plugins (1) — Django / Flask

- D121: `FrameworkPlugin` ABC — `detect(project_root)`, `extract(nodes, edges)`
- D122: `DjangoPlugin` — `urls.py` 파싱, `path()` / `re_path()` 인식
- D123: URL ↔ View 그래프 노드/엣지 생성
- D124: `FlaskPlugin` — `@app.route`, `@blueprint.route` 데코레이터 추출
- D125: Framework 뷰 패널 UI (라우트 트리)

### Week 26: Framework Plugins (2) — FastAPI / SQLAlchemy

- D126: `FastAPIPlugin` — `@router.get/post/...`, `Depends()` 체인
- D127: Dependency 그래프 (누가 무엇에 의존하는가)
- D128: `SQLAlchemyPlugin` — `declarative_base()`, `Column`, `relationship`
- D129: Model ↔ Table 맵 + ER 다이어그램 (간이)
- D130: 플러그인 자동 탐지 (import 기반)

### Week 27: Jupyter & Import Graph & Decorator

- D131: `JupyterParser` — `nbformat.read()`, code cell 만 추출
- D132: 매직 커맨드 필터 (`%%` / `!` 시작 라인 제거)
- D133: `ImportGraphBuilder` — 모듈 단위 그래프, `networkx` 순환 감지
- D134: 레이어 정의 파일 (`.srm-layers.yml`) → 위반 검출
- D135: `DecoratorAnalyzer` — 커스텀 데코레이터 메타데이터 추출

### Week 28: Dynamic Import & Hybrid Mode & RC2

- D136: `DynamicImportTracker` — `importlib.import_module(X)` 의 `X` 문자열 상수 추출
- D137: 동적 import 결과를 unsolved edge로 표기 (점선 회색)
- D138: `HybridIndexer` — 마지막 인덱싱 이후 변경된 파일만 Deep, 나머지 Shallow 재사용
- D139: 파일 변경 감지 (`mtime` 비교)
- D140: 부하 테스트 — 30만 LoC 프로젝트 Hybrid 인덱싱
- D140: **RC2 릴리스 태그**
- D140: **리스크 게이트 G5 통과**: 성능 + 차별화 기능 모두 작동

---

## 주요 클래스 계약

```python
# Week 23
class TypeHintExtractor:
    def extract(self, file: Path) -> list[TypeHint]: ...

@dataclass
class TypeHint:
    symbol: NodeId
    hint: str  # "int" / "Optional[str]" / "list[Model]"
    source_line: int

# Week 25
class FrameworkPlugin(ABC):
    name: str  # "django", "flask", ...
    @abstractmethod
    def detect(self, project_root: Path) -> bool: ...
    @abstractmethod
    def extract(self, writer: DatabaseWriter) -> PluginResult: ...

# Week 28
class HybridIndexer:
    def index(self, project_root: Path, previous_db: Optional[Path]) -> IndexResult:
        """
        - previous_db 없음 → 전체 Deep
        - previous_db 있음 → 변경 파일만 Deep, 나머지 이전 결과 재사용
        """
        ...
```

---

## 성능 목표 (Phase 4)

| 항목 | 목표 |
|------|------|
| Hybrid 재인덱싱 (1 파일 변경) | < 3초 |
| Django URL→View 그래프 | < 1초 |
| mypy 통합 (1만 LoC) | < 10초 (별도 스레드) |
| Jupyter 셀 파싱 (100 셀) | < 2초 |
| 30만 LoC 초기 Deep 인덱싱 | < 15분 |

---

## Phase 4 DoD

- [ ] Type Hint 추출 + 커버리지 메트릭 표시
- [ ] mypy / pyright 통합 옵션 동작
- [ ] Django / Flask / FastAPI / SQLAlchemy 플러그인 각각 데모 프로젝트에서 동작
- [ ] Virtualenv / Poetry / uv 자동 탐지
- [ ] .ipynb 파일 인덱싱 지원
- [ ] Import 그래프 + 순환 감지
- [ ] 데코레이터 분석 + 그래프 아이콘 표시
- [ ] 동적 import 탐지 (best-effort)
- [ ] Hybrid 인덱싱 기본 모드로 설정
- [ ] 30만 LoC 프로젝트 초기 인덱싱 < 15분
- [ ] 단위 테스트 커버리지 80%
- [ ] **RC2 릴리스 태그**
- [ ] **리스크 게이트 G5 통과**: Differentiation 기능 모두 작동

---

## Phase 4 리스크

| 리스크 | 등급 | 대응 |
|--------|------|------|
| R-10 프레임워크 엣지 케이스 | 🟡 | 플러그인 별 feature flag, 실패해도 기본 인덱싱 유지 |
| R-11 mypy 느림 | 🟡 | 옵션으로만 제공, 기본 off, QThread 캔슬 |
| 동적 import 오탐 | 🟢 | "best-effort" 명시, 회색 점선으로 불확실성 표현 |
| Jupyter nbformat 버전 | 🟢 | v4 이상만 지원 명시 |

---

## 수락 시나리오 (Phase 4 종료)

**시나리오 1**: Django 프로젝트 전용 뷰
1. Django 프로젝트 인덱싱 (Hybrid 모드, 자동 감지)
2. Framework 뷰 패널에 URL 트리 표시
3. `/api/users/<id>/` 클릭 → 해당 `UserDetailView` 에디터에서 열림
4. 그래프 뷰에 URL → View → Serializer → Model 체인 시각화

**시나리오 2**: Type Hint 커버리지
1. 프로젝트 로드 후 "Type Coverage" 메뉴
2. 파일별 힌트 커버리지 표 (0% - 100%)
3. 커버리지 낮은 파일에서 unsolved 노드가 많음을 확인
4. 힌트 추가 후 재인덱싱 → unsolved 감소 확인

**시나리오 3**: Hybrid 재인덱싱 속도
1. Django 프로젝트 초기 Deep 인덱싱 (10분)
2. 한 파일 수정 후 저장
3. 백그라운드 Hybrid 재인덱싱 시작 → 3초 이내 완료
4. 그래프 뷰 자동 새로고침

---

## 회고 (Phase 종료 후 작성)

**잘 된 점**:
-

**어려웠던 점**:
-

**다음 Phase로 이월된 항목**:
-

**타임라인 대비 실적**:
- 계획: 6주 / 실제: ?주

**성능 벤치마크 (Phase 4 종료 시)**:
- Hybrid 재인덱싱 (1 파일): ?초
- 30만 LoC 초기 Deep: ?분
- mypy 통합 오버헤드: ?%

**차별화 검증**:
- 원본 Sourcetrail 에 없는 기능 수: ?개
- 사용자 "이게 차별점이다" 피드백:
