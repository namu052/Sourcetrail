# Phase 1 — MVP Core: 인덱서 + 그래프 뷰

| 메타 | 값 |
|------|-----|
| 기간 | 6주 (Week 3-8) |
| 누적 | 8주 |
| 상태 | 📋 계획됨 |
| 마일스톤 | M1 — Image Parity |
| 선행 조건 | Phase 0 완료, PoC 3종 성공 |

## 목표

첨부 이미지의 **모든 P0 기능** 을 실제로 구현하여, 이미지와 동등한 UX를 시각적으로 재현한다.

## 다루는 기능

**P0 (필수)**
- 심볼별 멀티 탭 (`app.models.session···ession.is_expired` 형태)
- 뒤로/앞으로/홈 버튼 + 히스토리 드롭다운
- Fully Qualified Name 검색바 + 퍼지 자동완성
- 클래스 컨테이너 노드 (▶ 접기, 카운트 배지)
- 타입별 색상 (🟠 함수/메서드, 🔵 필드, 🔳 unsolved)
- 엣지 구분 (실선 오렌지 = call, 점선 블루 = member access)
- **Unsolved symbol 명시적 노드** ← Python 특화 핵심
- 좌측 심도(depth) 슬라이더, 좌하단 줌 ±, 우상단 북마크 ★

## 산출물 (Deliverables)

| # | 산출물 | 위치 |
|---|--------|------|
| D1.1 | `IndexerService` | `src/sourcetrail_remake/indexer/service.py` |
| D1.2 | `DatabaseWriter` (SourcetrailDB 호환) | `src/sourcetrail_remake/db/writer.py` |
| D1.3 | `UnsolvedSymbolTracker` | `src/sourcetrail_remake/indexer/unsolved.py` |
| D1.4 | CLI: `srm-index` | `src/sourcetrail_remake/cli/index.py` |
| D1.5 | `MainWindow` + 도킹 골격 | `src/sourcetrail_remake/ui/main_window.py` |
| D1.6 | `GraphView` + `GraphScene` | `src/sourcetrail_remake/ui/graph/` |
| D1.7 | `NodeRenderer`, `EdgeRenderer` | `src/sourcetrail_remake/ui/graph/renderers.py` |
| D1.8 | 레이아웃 엔진 (Sugiyama + force) | `src/sourcetrail_remake/ui/graph/layout.py` |
| D1.9 | 탭 바, 히스토리, 검색바 | `src/sourcetrail_remake/ui/navigation/` |
| D1.10 | 심도 슬라이더, 줌, 북마크 | `src/sourcetrail_remake/ui/controls/` |

## 주간 작업 계획

### Week 3-4: 인덱서 코어

**Week 3**
- D11: `IndexerService` 스켈레톤, Jedi `Project` 래퍼
- D12: Parso AST 순회 → top-level symbol 추출
- D13: Jedi `Script.get_names()` + `goto()` + `get_references()` 통합
- D14: `DatabaseWriter` SourcetrailDB 호환 SQLite writer (테이블 생성, INSERT)
- D15: Node/Edge 매핑 테이블 (Jedi NameType → SourcetrailDB node_type)

**Week 4**
- D16: **UnsolvedSymbolTracker** — Jedi `infer()`가 빈 결과를 반환할 때 placeholder 노드 생성
- D17: Source location 기록 (occurrence 테이블)
- D18: Shallow 모드 구현 (이름 기반 빠른 매칭)
- D19: Deep 모드 구현 (Jedi 완전 분석)
- D20: CLI `srm-index <src> --db <path> [--shallow|--deep]` + 백그라운드 `QThread`
- D20: Django / Flask / Requests 인덱싱 smoke test

### Week 5-6: 그래프 뷰 렌더러

**Week 5**
- D21: `MainWindow` + `QDockWidget` 기본 도킹 레이아웃
- D22: `GraphView` (QGraphicsView 상속) + `GraphScene`
- D23: `NodeRenderer` — 클래스 컨테이너 노드 (둥근 사각형 + ▶ 토글 + 카운트 배지)
- D24: 멤버 노드 렌더링 (타입별 색상, 선택 시 강조)
- D25: **Unsolved 노드** — 회색 해치 패턴 (QBrush + QPainter 커스텀)

**Week 6**
- D26: `EdgeRenderer` — 실선/점선, 방향 화살표
- D27: 엣지 bundling (동일 목적지 다중 엣지 묶기)
- D28: 레이아웃 엔진 — Sugiyama 계층형 기본 + force-directed 보정
- D29: 노드 펼침/접기 애니메이션
- D30: 단위 테스트 — 노드/엣지 렌더링, 레이아웃 결정성

### Week 7: 네비게이션

- D31: 탭 바 (`QTabBar`) — 심볼별 멀티 탭, 원형 아이콘
- D32: 히스토리 스택 + 뒤로/앞으로/홈 버튼
- D33: 히스토리 드롭다운 (가운데 버튼 클릭)
- D34: 검색바 (FQN 표시)
- D35: 퍼지 자동완성 (rapidfuzz 기반 popup)

### Week 8: 제어 위젯 & 통합

- D36: 좌측 심도 슬라이더 (1-10단계, BFS 확장 깊이)
- D37: 좌하단 줌 ±
- D38: 우상단 북마크 ★ (추가/제거/목록)
- D39: 노드 확장/축소 인터랙션 (클릭 + 키보드 +/-)
- D40: **Phase 1 통합 테스트** — 이미지 재현 검증, 성능 벤치마크

## 데이터 플로우 (Phase 1 범위)

```
[CLI: srm-index]
    ↓
[IndexerService]
    ├── Jedi Script/Project
    ├── Parso AST
    └── UnsolvedSymbolTracker
    ↓
[DatabaseWriter (SourcetrailDB 호환 SQLite)]
    ↓
[DB File *.srctrldb]
    ↓
[DatabaseReader]
    ↓
[GraphDataProvider]
    ↓
[GraphScene/View]
    ├── NodeRenderer
    └── EdgeRenderer
```

## 주요 클래스 계약 (초안)

```python
# src/sourcetrail_remake/indexer/service.py
class IndexerService:
    def __init__(self, project_root: Path, mode: Literal["shallow", "deep"]):
        ...
    def index(self, writer: DatabaseWriter, progress: Callable[[int, int], None]) -> IndexResult:
        ...

# src/sourcetrail_remake/db/writer.py
class DatabaseWriter:
    def __init__(self, db_path: Path): ...
    def record_symbol(self, ...) -> NodeId: ...
    def record_reference(self, source: NodeId, target: NodeId, kind: EdgeType) -> EdgeId: ...
    def record_unsolved(self, context: str, name: str) -> NodeId: ...
    def record_file(self, path: Path) -> FileId: ...
    def record_source_location(self, ...) -> LocationId: ...

# src/sourcetrail_remake/ui/graph/scene.py
class GraphScene(QGraphicsScene):
    def load_symbol(self, symbol_id: NodeId, depth: int) -> None:
        """심볼을 중심으로 depth 반경 내 그래프 렌더링."""
```

## 성능 목표 (Phase 1)

| 항목 | 목표 |
|------|------|
| 인덱싱 속도 | 1만 LoC < 1분 (Shallow), < 3분 (Deep) |
| 그래프 첫 표시 | < 500ms |
| 노드 선택 반응 | < 100ms |
| 줌/팬 프레임률 | 60fps (1000개 노드 기준) |

## Phase 1 DoD

- [ ] 중규모 프로젝트(~1만 LoC) 인덱싱 < 1분 (Shallow)
- [ ] 첨부 이미지와 **시각적으로 동등한 그래프 뷰** 재현
- [ ] Unsolved symbol이 회색 해치 노드로 명시적 표시
- [ ] 탭/히스토리/검색/줌/심도 모두 작동
- [ ] **생성한 DB를 원본 Sourcetrail GUI에서 열람 가능** (호환성 검증)
- [ ] 단위 테스트 커버리지 70% 이상 (Phase 1 기준, 최종 80% 목표는 Phase 2)
- [ ] Phase 1 종료 시점 스크린샷 기록

## 위험 & 완화

| 위험 | 대응 |
|------|------|
| Jedi의 동적 추론 실패 빈번 | Unsolved 트래커가 적극적으로 placeholder 생성, 나쁜 UX가 아닌 "정직한 상태"로 표현 |
| 레이아웃 알고리즘 품질 | 1차는 Sugiyama 단순 구현, Phase 5에서 개선 여지 |
| 10만+ LoC 시 성능 저하 | Phase 1은 1만 LoC 기준, 대형 프로젝트 최적화는 Phase 5 |
| SourcetrailDB 호환 실패 | Phase 0 PoC 1에서 이미 검증됨 — 회귀 테스트 매주 실행 |

## 회고 (Phase 종료 후 작성)

- 잘 된 점:
- 어려웠던 점:
- 다음 Phase로 이월된 항목:
- 타임라인 대비 실적:
