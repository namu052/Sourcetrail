# Phase 4 — Python 특화 기능

| 메타 | 값 |
|------|-----|
| 기간 | 6주 (Week 23-28) |
| 누적 | 28주 |
| 상태 | 📋 계획됨 |
| 마일스톤 | M4 — Differentiation |
| 선행 조건 | Phase 3 완료, Smart Rename/Search 안정 |

## 목표

Source Insight, 원본 Sourcetrail, Understand 등 **경쟁 도구가 제공하지 못하는 Python 생태계 특화 가치**를 확보한다.

Python의 동적 특성을 정직하게 인정(unsolved)하면서도, 타입 힌트·프레임워크 메타데이터·가상환경 정보 등을 결합해 **unsolved를 점진적으로 solved로 승격**시키는 것이 이 Phase의 철학.

## 다루는 기능

- **F19 — Type Hint 기반 정밀도 향상**
- **F20 — Duck Typing 추정 뷰**
- **F21 — Django/Flask/FastAPI ORM 관계 인식**
- **F22 — 가상환경(venv) / Site-Packages 인식**
- **F23 — Jupyter Notebook 통합**
- **F24 — Import Graph 뷰**
- **F25 — Decorator / Metaclass 추적**
- **F26 — Dynamic Import 탐지**
- **F27 — Shallow / Deep / Hybrid 인덱싱 모드 (GUI 토글)**

## 산출물 (Deliverables)

| # | 산출물 | 위치 |
|---|--------|------|
| D4.1 | `TypeHintResolver` | `src/sourcetrail_remake/indexer/type_hints.py` |
| D4.2 | mypy/pyright 외부 통합 | `src/sourcetrail_remake/indexer/external_checker.py` |
| D4.3 | `DuckTypeCandidateFinder` | `src/sourcetrail_remake/indexer/duck.py` |
| D4.4 | `DjangoPlugin`, `FlaskPlugin`, `FastAPIPlugin`, `SQLAlchemyPlugin` | `src/sourcetrail_remake/indexer/frameworks/` |
| D4.5 | `EnvironmentInspector` (venv/poetry/pipenv 감지) | `src/sourcetrail_remake/core/environment.py` |
| D4.6 | `JupyterIndexer` | `src/sourcetrail_remake/indexer/jupyter.py` |
| D4.7 | `ImportGraphView` | `src/sourcetrail_remake/ui/graph/import_graph.py` |
| D4.8 | `DecoratorTracker` | `src/sourcetrail_remake/indexer/decorators.py` |
| D4.9 | `DynamicImportDetector` | `src/sourcetrail_remake/indexer/dynamic.py` |
| D4.10 | 인덱싱 모드 GUI 토글 | `src/sourcetrail_remake/ui/dialogs/indexing_mode.py` |

## 주간 작업 계획

### Week 23-24: Type Hint 통합 (F19 + F20)

**Week 23 — Type Hint Resolver**
- D116: `TypeHintResolver` — `typing` 모듈 힌트 해석 (PEP 484)
- D117: PEP 526 변수 어노테이션, PEP 604 `X | Y`
- D118: Generic / TypeVar / Protocol 처리
- D119: **Unsolved → Solved 승격 로직**: 타입 힌트가 있으면 회색 해치 제거
- D120: 노드에 **타입 배지** 추가 (`: str`, `: Optional[Session]`)

**Week 24 — 외부 체커 & Duck Typing**
- D121: mypy 결과 JSON 파싱 → 참조 엣지 보완
- D122: pyright 결과 파싱 (옵션)
- D123: `DuckTypeCandidateFinder` — 정적 추론 실패 시 후보 심볼 수집
- D124: 후보 노드는 opacity 50%로 렌더링
- D125: 후보 선택 UI (정답이 명확한 경우 확정)

### Week 25-26: Framework 인식 (F21)

**Week 25 — Django & SQLAlchemy**
- D126: `DjangoPlugin` — `models.ForeignKey`, `ManyToManyField`, `OneToOneField` 탐지
- D127: ORM 관계를 **녹색 점선 엣지** 로 시각화 (새 edge_kind 추가, 호환성 확장 테이블에 저장)
- D128: `Meta.db_table` / `__tablename__` → 노드 뱃지
- D129: `SQLAlchemyPlugin` — `relationship()`, `ForeignKey`, `Mapped[...]`
- D130: Django `urls.py` 라우팅 → endpoint 노드 (path → view 연결)

**Week 26 — Flask & FastAPI**
- D131: `FlaskPlugin` — `@app.route`, `@blueprint.route` 탐지
- D132: `FastAPIPlugin` — `@app.get/post/put/delete`, `@router.*`
- D133: Path parameter, query parameter, 의존성 주입(`Depends`) 관계 시각화
- D134: Endpoint → HTTP method 배지
- D135: OpenAPI 스키마 힌트 (FastAPI 자동 생성 문서 연동 가능성 — 시간 되면)

### Week 27: 환경 통합 (F22)

- D136: `EnvironmentInspector` — `.venv` / `venv` / poetry / pipenv / conda 자동 감지
- D137: `requirements.txt`, `pyproject.toml`, `poetry.lock`, `Pipfile.lock` 파싱
- D138: site-packages 심볼을 별도 "External" 그룹으로 분류
- D139: External 심볼은 **흐린 배경 + 이탤릭** 으로 렌더링
- D140: 필터 토글: "Project only" / "Include External" / "External only"

### Week 28: Jupyter & Dynamic & 인덱싱 모드 (F23 + F25 + F26 + F27)

**Jupyter (F23)**
- D141: `JupyterIndexer` — `.ipynb` 파싱 (nbformat)
- D142: 셀 단위 심볼 추출, IPython magic (`%`, `!`) 무시
- D143: 노트북 셀 ↔ `.py` 파일 심볼 크로스 참조
- D144: 그래프에서 노트북 노드를 별도 아이콘으로 표시

**Decorator & Dynamic (F25 + F26)**
- D145: `DecoratorTracker` — `@property`, `@classmethod`, `@staticmethod` 배지
- D146: `@dataclass`, `@attrs`, Pydantic `BaseModel` — 자동 필드 확장
- D147: `DynamicImportDetector` — `importlib.import_module`, `__import__` 탐지
- D148: 정적 탐지 가능한 dynamic import는 **점선 회색 "dynamic" 엣지** 로 연결

**인덱싱 모드 GUI (F27)**
- D149: 프로젝트 설정 다이얼로그에 **Shallow / Deep / Hybrid 라디오 버튼**
- D150: Hybrid 모드 — 기본 Shallow, 탐색된 서브트리만 Deep 재분석 (on-demand)

## 프레임워크 플러그인 아키텍처

```python
# src/sourcetrail_remake/indexer/frameworks/base.py
class FrameworkPlugin(ABC):
    name: ClassVar[str]

    @abstractmethod
    def detect(self, project_root: Path) -> bool:
        """이 프레임워크가 프로젝트에 있는지 판단."""

    @abstractmethod
    def enhance(self, node: IndexedSymbol, writer: DatabaseWriter) -> None:
        """Jedi 분석 후 추가 엣지/메타데이터 기입."""
```

플러그인 방식이므로 Phase 5에서 **Custom Language Parser (F16)** 로 확장 가능.

## SourcetrailDB 호환성 유지 전략

Python 특화 신규 엣지 종류 (Django ORM, FastAPI route, dynamic import 등)는 원본 SourcetrailDB `edge_type` enum에 없으므로:

- **Option A**: 기존 enum 중 `USAGE`로 매핑하고, 확장 정보는 별도 `edge_extension` 테이블(우리가 추가)에 저장
- **Option B**: `edge_type` 값을 확장(신규 int 값 사용)하되, 원본 GUI는 이를 `UNKNOWN`으로 해석하게 함

**결정**: Option A — 100% 호환성 유지 필수 조건에 부합.

## 성능 목표 (Phase 4)

| 항목 | 목표 |
|------|------|
| Django 프로젝트 인덱싱 (예: Sentry 규모) | < 10분 |
| Type Hint 기반 unsolved 감소율 | 50% 이상 (힌트 잘 쓰는 프로젝트 기준) |
| Jupyter 노트북 100개 인덱싱 | < 30초 |
| External 필터 토글 | < 500ms (뷰 재렌더링) |

## Phase 4 DoD

- [ ] Django 샘플 프로젝트(예: djangoproject.com)에서 ORM 관계 시각화 성공
- [ ] FastAPI 샘플 프로젝트에서 라우트 → 핸들러 엣지 정확 연결
- [ ] 타입 힌트가 있는 프로젝트의 unsolved 심볼 비율 50% 이상 감소
- [ ] Jupyter 노트북 심볼이 그래프에 나타나고, `.py` 파일과 크로스 참조됨
- [ ] venv 감지 후 External 필터 작동
- [ ] dynamic import가 점선 회색 엣지로 표시
- [ ] Shallow/Deep/Hybrid 모드 모두 작동, 사용자가 GUI에서 토글 가능
- [ ] **원본 Sourcetrail GUI 호환성 회귀 테스트 통과** (확장 정보는 무시되되 깨지지 않음)
- [ ] 테스트 커버리지 80% 유지

## 위험 & 완화

| 위험 | 대응 |
|------|------|
| 프레임워크별 엣지 케이스 과다 | 첫 릴리스는 대표 패턴만, 예외는 이슈로 수집 |
| mypy/pyright 외부 프로세스 느림 | 선택적 기능, 기본 off |
| Jupyter 셀 간 변수 스코프 | 셀 순서대로 누적 스코프 구성, 실행 순서 다를 때는 경고 |
| 동적 import 오탐지 | 정적 탐지 가능한 경우만, 불확실한 건 unsolved 유지 |
| SourcetrailDB 호환성 위반 유혹 | PR 리뷰 체크리스트에 호환성 항목 추가 |

## 회고 (Phase 종료 후 작성)

- 잘 된 점:
- 어려웠던 점:
- 다음 Phase로 이월된 항목:
- 타임라인 대비 실적:
- RC 릴리스 후 피드백:
