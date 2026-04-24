# Phase 1 · MVP 인덱서 + 그래프 뷰 (P0 기능)

| 메타 | 값 |
|------|-----|
| 기간 | **6주 (Week 3-8)** |
| 누적 | 8주 |
| 마일스톤 | **M1 — Image Parity** (Alpha 릴리스) |
| 선행 조건 | Phase 0 완료, PoC 3종 성공 |

---

## 목표

첨부 이미지의 **모든 P0 기능** 을 실제로 구현하여, 이미지와 **시각적으로 동일한 UX**를 재현한다.

> "눈으로 보기에 이미지의 화면이 나오는 상태" = Phase 1 종료.

---

## 다루는 기능 (P0 전체)

### 네비게이션 바
- 심볼별 멀티 탭 (`app.models.session···ession.is_expired`)
- 뒤로/앞으로/홈 버튼 + 히스토리 드롭다운
- 검색바 (Fully Qualified Name 표시)
- 퍼지 자동완성
- 북마크 ★
- 새로고침, 설정 메뉴

### 그래프 뷰
- 클래스 컨테이너 노드 (▶ 토글, 카운트 배지)
- 멤버 노드 (중첩)
- 타입별 색상 (🟠 함수/🔵 필드/🔳 unsolved)
- **Unsolved symbol 회색 해치 노드** ← Python 특화 핵심
- 엣지: 실선 오렌지(call), 점선 블루(member access)
- 엣지 bundling
- 현재 선택 심볼 강조

### 그래프 제어
- 좌측 심도(depth) 슬라이더
- 좌하단 줌 ±
- 노드 확장/축소

---

## 산출물 (Deliverables)

| # | 산출물 | 위치 |
|---|--------|------|
| D1.1 | `IndexerService` (Jedi 래퍼) | `src/sourcetrail_remake/indexer/service.py` |
| D1.2 | `JediResolver` | `src/sourcetrail_remake/indexer/jedi_resolver.py` |
| D1.3 | `ParsoWalker` | `src/sourcetrail_remake/indexer/parso_walker.py` |
| D1.4 | `UnsolvedSymbolTracker` | `src/sourcetrail_remake/indexer/unsolved.py` |
| D1.5 | `DatabaseWriter` (SourcetrailDB 호환) | `src/sourcetrail_remake/db/writer.py` |
| D1.6 | `DatabaseReader` | `src/sourcetrail_remake/db/reader.py` |
| D1.7 | CLI: `srm-index` | `src/sourcetrail_remake/cli/index.py` |
| D1.8 | `MainWindow` + 도킹 골격 | `src/sourcetrail_remake/ui/main_window.py` |
| D1.9 | `GraphView` / `GraphScene` | `src/sourcetrail_remake/ui/graph/` |
| D1.10 | `NodeRenderer`, `EdgeRenderer` | `src/sourcetrail_remake/ui/graph/nodes.py`, `edges.py` |
| D1.11 | 레이아웃 엔진 (Sugiyama + force) | `src/sourcetrail_remake/ui/graph/layout.py` |
| D1.12 | 탭 바 / 히스토리 / 검색바 | `src/sourcetrail_remake/ui/navigation/` |
| D1.13 | 심도/줌/북마크 컨트롤 | `src/sourcetrail_remake/ui/controls/` |

---

## 주간 작업 계획

### Week 3-4: 인덱서 코어

**Week 3**
- D11: `IndexerService` 스켈레톤, Jedi `Project` 세션 래퍼
- D12: Parso AST 순회 → top-level symbol 추출
- D13: Jedi `Script.get_names() + goto() + get_references()` 통합
- D14: `DatabaseWriter` SourcetrailDB 호환 SQLite 쓰기 (CREATE TABLE, INSERT 시퀀스)
- D15: Jedi NameType ↔ SourcetrailDB `node_type` 매핑 테이블

**Week 4**
- D16: **`UnsolvedSymbolTracker`** — Jedi `infer()` 빈 결과 시 placeholder 노드 생성
- D17: Source location 기록 (`source_location` + `occurrence` 테이블)
- D18: Shallow 모드 (이름 기반 빠른 매칭)
- D19: Deep 모드 (Jedi 완전 분석)
- D20: CLI `srm-index <src> --db <path> [--shallow|--deep]` + 백그라운드 QThread
- D20: Django / Flask / Requests 프로젝트 smoke test

### Week 5-6: 그래프 뷰 렌더러

**Week 5**
- D21: `MainWindow` + `QDockWidget` 기본 도킹 레이아웃
- D22: `GraphView` (QGraphicsView 상속) + `GraphScene`
- D23: `NodeRenderer` — 클래스 컨테이너 (둥근 사각형 + ▶ 토글 + 카운트 배지)
- D24: 멤버 노드 렌더링 (타입별 색상, 선택 시 강조)
- D25: **Unsolved 노드** — 회색 해치 패턴 (QBrush.DiagCrossPattern 또는 QPainter 커스텀)

**Week 6**
- D26: `EdgeRenderer` — 실선/점선, 방향 화살표, Bezier 곡선
- D27: 엣지 bundling (동일 source→target 다중 엣지 묶기)
- D28: 레이아웃 엔진 — Sugiyama 계층형 기본 + force-directed 미세조정
- D29: 노드 펼침/접기 애니메이션 (`QPropertyAnimation`)
- D30: 단위 테스트 — 노드/엣지 렌더링, 레이아웃 결정성(같은 입력 → 같은 위치)

### Week 7: 네비게이션

- D31: 탭 바 (`QTabBar`) — 심볼별 멀티 탭, 원형 아이콘
- D32: 히스토리 스택 (`list[HistoryEntry]`) + 뒤로/앞으로/홈 버튼
- D33: 히스토리 드롭다운 (가운데 버튼 클릭 시 `QMenu` 팝업)
- D34: 검색바 (FQN 표시, `QLineEdit`)
- D35: 퍼지 자동완성 (rapidfuzz 기반 `QCompleter` 대체 팝업)

### Week 8: 제어 위젯 & 통합 (Alpha 릴리스)

- D36: 좌측 심도 슬라이더 (1-10단계, BFS 확장 깊이)
- D37: 좌하단 줌 ±
- D38: 우상단 북마크 ★ (추가/제거/목록 팝오버)
- D39: 노드 확장/축소 인터랙션 (클릭 + 키보드 +/-)
- D40: **Phase 1 통합 테스트** — 첨부 이미지 재현 검증
- D40: **Alpha 릴리스 태그** (내부 검증용)

---

## 데이터 플로우 (Phase 1 범위)

```
사용자: srm-index my_project --db out.srctrldb --shallow
    ↓
IndexerService.__init__(mode='shallow')
    ↓
[Week 3 구현] ParsoWalker.walk(project_root)
    ├─ 각 .py 파일 파싱
    └─ top-level 심볼 추출
    ↓
[Week 3 구현] JediResolver.resolve_references(names)
    ├─ goto_definition()
    ├─ get_references()
    └─ infer() → 실패 시 UnsolvedSymbolTracker에 등록
    ↓
[Week 3 구현] DatabaseWriter.write_all()
    ├─ CREATE TABLE (SourcetrailDB 호환 스키마)
    ├─ INSERT node, edge, symbol, file, source_location, occurrence
    └─ node_extension (unsolved 메타)
    ↓
out.srctrldb (SQLite 파일)

[GUI 실행] srm-gui
    ↓
[Week 5 구현] DatabaseReader.load(out.srctrldb)
    ↓
[Week 5-6 구현] GraphScene.load_symbol(symbol_id, depth)
    ├─ DB에서 depth 반경 내 node/edge 조회
    ├─ NodeRenderer — 타입별 색상, unsolved 해치
    ├─ EdgeRenderer — 실선/점선, bundling
    └─ Layout engine — Sugiyama 배치
    ↓
GraphView 렌더링
```

---

## 주요 클래스 계약

```python
# Week 3
class IndexerService:
    def __init__(self, project_root: Path, mode: Literal['shallow', 'deep']): ...
    def index(self, writer: DatabaseWriter, progress_cb: Callable[[int, int], None]) -> IndexResult: ...

class DatabaseWriter:
    def __init__(self, db_path: Path): ...
    def initialize_schema(self) -> None: ...
    def record_symbol(self, name: str, node_type: NodeType, file: FileId, location: SourceLocation) -> NodeId: ...
    def record_edge(self, source: NodeId, target: NodeId, edge_type: EdgeType) -> EdgeId: ...
    def record_unsolved(self, context_node: NodeId, name: str) -> NodeId: ...
    def commit(self) -> None: ...

# Week 5
class GraphScene(QGraphicsScene):
    def load_symbol(self, symbol_id: NodeId, depth: int) -> None: ...
    def on_node_clicked(self, node_id: NodeId) -> None: ...

class NodeRenderer:
    @staticmethod
    def create_class_container(name: str, member_count: int) -> QGraphicsItem: ...
    @staticmethod
    def create_member(name: str, node_type: NodeType) -> QGraphicsItem: ...
    @staticmethod
    def create_unsolved() -> QGraphicsItem: ...  # 회색 해치 패턴
```

---

## 성능 목표 (Phase 1)

| 항목 | 목표 |
|------|------|
| 1만 LoC 인덱싱 (Shallow) | < 1분 |
| 1만 LoC 인덱싱 (Deep) | < 3분 |
| 그래프 첫 표시 | < 500ms |
| 노드 선택 반응 | < 100ms |
| 줌/팬 프레임률 | 60fps (1,000 노드 기준) |

---

## Phase 1 DoD

- [ ] 중규모 프로젝트(~1만 LoC) Shallow 인덱싱 < 1분
- [ ] **첨부 이미지와 시각적으로 동일한 그래프 뷰 재현**
- [ ] Unsolved symbol이 회색 해치 노드로 명시적 표시
- [ ] 탭/히스토리/검색/줌/심도/북마크 모두 작동
- [ ] **생성한 DB를 원본 Sourcetrail GUI에서 열람 가능** (호환성 검증)
- [ ] 단위 테스트 커버리지 70% 이상 (Phase 1 기준, 최종 80%는 Phase 2에서)
- [ ] Alpha 릴리스 태그 (GitHub Release, 내부 검증용)
- [ ] **리스크 게이트 G2 통과**: 10만 LoC 그래프 60fps 확인

---

## Phase 1 리스크

| 리스크 | 등급 | 대응 |
|--------|------|------|
| R-01 Jedi 동적 추론 실패 | 🔴 | UnsolvedSymbolTracker가 적극적으로 placeholder 생성 — "정직한 상태" |
| R-04 대형 프로젝트 성능 | 🔴 | 1만 LoC 기준, 10만은 Phase 5 최적화 대상 |
| R-08 레이아웃 품질 | 🟡 | 1차는 Sugiyama 단순 구현, Phase 5에 개선 |
| R-02 SourcetrailDB 호환 실패 | 🔴 | 매주 호환성 회귀 테스트 |

---

## 수락 시나리오 (Phase 1 종료)

**시나리오 1**: Requests 라이브러리 인덱싱
1. `srm-index requests/ --db requests.srctrldb --shallow`
2. 1분 이내 완료
3. `srm-gui requests.srctrldb` 실행
4. 탭에 `requests.api.get` 같은 FQN 입력
5. 그래프에 해당 함수 + 호출 관계 표시
6. 심도 슬라이더 조정하여 깊이 3까지 확장
7. 일부 심볼이 unsolved로 표시됨 (회색 해치)

**시나리오 2**: 호환성 검증
1. 생성된 `requests.srctrldb` 를 원본 Sourcetrail Windows 4.0 에서 열기
2. 에러 없이 로드 성공
3. 노드/엣지 개수가 우리 앱과 동일

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

**성능 벤치마크 (Phase 1 종료 시)**:
- 1만 LoC Shallow 인덱싱: ?초
- 그래프 첫 표시: ?ms
- 1000 노드 줌/팬: ?fps

**Alpha 피드백 (내부 테스트)**:
-
