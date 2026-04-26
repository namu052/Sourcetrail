# Phase 2 · Context & Symbol 패널 (P1 기능 - MVP 완성)

| 메타 | 값 |
|------|-----|
| 기간 | **8주 (Week 9-16)** |
| 누적 | 16주 |
| 마일스톤 | **M2 — MVP Complete** (Beta 릴리스) |
| 선행 조건 | Phase 1 Alpha 릴리스 완료, G2 통과 |

---

## 목표

Source Insight의 핵심 정체성인 **4개 사이드 패널**(Context / Symbol / Relation / Syntax Formatting)을 PyQt6 도킹 시스템 위에 구현하여 **MVP 완성**.

> "코드를 읽는 행위 자체가 즐거워지는 상태" = Phase 2 종료.

---

## 다루는 기능 (P1)

### F1 — Context Window (컨텍스트 윈도우)
- 현재 커서 위치 심볼의 선언부 자동 표시
- 커서 이동 시 실시간 업데이트 (QTimer 디바운스)
- 미니 QScintilla 임베드 (읽기 전용, 구문 하이라이트)
- "원본으로 이동" 버튼
- 중첩 호출 스택 표시 (최근 5개 심볼)

### F2 — Symbol Window (심볼 윈도우)
- 현재 파일의 모든 심볼을 트리로 표시
- 클래스 → 메서드/필드 계층 구조
- 아이콘 (class/function/variable/property)
- 접근 수준 표시 (public/protected/private — `_` prefix 기반)
- 필터 입력창 (실시간 필터)
- 정렬 모드 (알파벳 / 선언 순서)
- 더블클릭 → 에디터 해당 위치로 이동

### F3 — Relation Window (관계 윈도우 — Tree 모드)
- 현재 심볼의 관계를 트리로 표시
  - Called by (누가 이 함수를 호출하는가)
  - Calls (이 함수가 호출하는 것)
  - Referenced by (참조하는 곳)
  - Overrides / Overridden by (메서드 오버라이드 관계)
- 확장 시 하위 관계 재귀적 조회
- 더블클릭 → 해당 심볼로 이동
- 깊이 제한 (기본 3단계)

### F4 — Syntax Formatting / Semantic Decoration
- 구문 하이라이트 (QScintilla 기본)
- **의미 기반 추가 데코레이션**:
  - 사용되지 않는 변수 (회색 + 취소선)
  - 미정의 참조 (빨간 물결)
  - deprecated 호출 (노란 배경)
  - type hint 누락 (연한 노란 밑줄, 옵션)
- 설정 창에서 각 항목 on/off

---

## 산출물 (Deliverables)

| # | 산출물 | 위치 |
|---|--------|------|
| D2.1 | `ContextWindow` 위젯 | `src/sourcetrail_remake/ui/panels/context_window.py` |
| D2.2 | `SymbolWindow` 위젯 | `src/sourcetrail_remake/ui/panels/symbol_window.py` |
| D2.3 | `RelationWindow` 위젯 | `src/sourcetrail_remake/ui/panels/relation_window.py` |
| D2.4 | `SyntaxDecorator` | `src/sourcetrail_remake/ui/editor/decorator.py` |
| D2.5 | `QScintillaEditor` 래퍼 | `src/sourcetrail_remake/ui/editor/editor.py` |
| D2.6 | `EventBus` (Qt Signal 기반) | `src/sourcetrail_remake/core/event_bus.py` |
| D2.7 | `SymbolIndex` (빠른 심볼 조회) | `src/sourcetrail_remake/indexer/symbol_index.py` |
| D2.8 | `RelationQuery` (관계 그래프 순회) | `src/sourcetrail_remake/indexer/relation_query.py` |
| D2.9 | `DeprecationAnalyzer` | `src/sourcetrail_remake/indexer/deprecation.py` |
| D2.10 | `UnusedVariableAnalyzer` | `src/sourcetrail_remake/indexer/unused.py` |
| D2.11 | 도킹 레이아웃 프리셋 저장/복원 | `src/sourcetrail_remake/ui/layout_manager.py` |
| D2.12 | 설정 다이얼로그 (데코레이션 on/off) | `src/sourcetrail_remake/ui/dialogs/preferences.py` |

---

## 주간 작업 계획

### Week 9-10: Context Window + 에디터 통합

**Week 9**
- D41: `QScintillaEditor` 래퍼 클래스 (Lexer, 폰트, 색상, 기본 단축키)
- D42: Python Lexer 설정 + 커스텀 스타일 (이미지 톤에 맞춤)
- D43: `ContextWindow` 위젯 스켈레톤 (도킹 가능 `QDockWidget`)
- D44: 커서 이동 이벤트 → 심볼 DB 조회 → 선언부 로드
- D45: 미니 QScintilla 임베드 (읽기 전용, 해당 심볼 하이라이트)

**Week 10**
- D46: `EventBus` — `cursor_moved(file, line, col)` 시그널
- D47: QTimer 디바운스 (150ms) 로 빈번한 업데이트 억제
- D48: "원본으로 이동" 버튼 — `file_opened(file, line)` 시그널 발행
- D49: 중첩 스택 (최근 5개 심볼) 상단 breadcrumb 표시
- D50: Context Window 단위 테스트 (Mock DB 기반)

### Week 11-12: Symbol Window + 빠른 조회

**Week 11**
- D51: `SymbolWindow` — `QTreeView` + `QAbstractItemModel` 커스텀
- D52: `SymbolIndex` — 파일별 심볼 캐싱 (메모리, file_opened 시 로드)
- D53: 클래스 → 메서드/필드 트리 구조 생성
- D54: 아이콘 세트 (class, function, variable, property, static) — 16x16 PNG
- D55: 접근 수준 표시 (`_` prefix → protected, `__` → private)

**Week 12**
- D56: 실시간 필터 (`QLineEdit` + `QSortFilterProxyModel`)
- D57: 정렬 모드 토글 (알파벳 ↔ 선언 순서)
- D58: 더블클릭 → `file_opened` 시그널
- D59: 심볼 변경 감지 (파일 저장 시 재인덱싱)
- D60: Symbol Window 단위 테스트

### Week 13-14: Relation Window

**Week 13**
- D61: `RelationWindow` — 탭 4개 (Called by / Calls / Refs / Overrides)
- D62: `RelationQuery` — DB edge 테이블에서 방향별 조회
  - `get_callers(node_id)` → incoming call edges
  - `get_callees(node_id)` → outgoing call edges
  - `get_references(node_id)` → occurrence + usage
- D63: `QTreeView` + lazy loading (확장 시에만 하위 조회)
- D64: 깊이 제한 슬라이더 (1-5, 기본 3)
- D65: 더블클릭 → `symbol_selected(node_id)` 시그널

**Week 14**
- D66: 오버라이드 관계 조회 (MRO 순회)
- D67: 순환 참조 감지 (depth 초과 시 `(recursive)` 표시)
- D68: 결과 없음 상태 UI (`"관계가 없습니다"` 안내)
- D69: Relation Window 단위 테스트
- D70: 3개 패널 + 에디터 + 그래프 뷰 통합 E2E 테스트

### Week 15: Syntax Formatting / Semantic Decoration

- D71: `SyntaxDecorator` — QScintilla `QsciStyle` 기반 의미 스타일 추가
- D72: `UnusedVariableAnalyzer` — Jedi 기반, 스코프 내 참조 0인 변수 탐지
- D73: `DeprecationAnalyzer` — `@deprecated` 데코레이터 / `warnings.warn(DeprecationWarning)` 패턴 매칭
- D74: 미정의 참조 마커 (빨간 물결 — QsciIndicator)
- D75: 설정 다이얼로그 — 각 데코레이션 on/off 체크박스

### Week 16: 통합 & Beta 릴리스

- D76: 도킹 레이아웃 프리셋 저장/복원 (`QSettings`)
- D77: 기본 레이아웃 3종 (Default / Source Insight Style / Wide)
- D78: MVP 통합 회귀 테스트 — 전체 시나리오 통합
- D79: **Phase 2 MVP 통합 테스트** — Django 프로젝트 대상
- D80: 단위 테스트 커버리지 75% 달성
- D80: **Beta 릴리스 태그** — 외부 공개 준비 완료
- D80: **리스크 게이트 G3 통과**: MVP DoD 100% 달성

---

## 주요 클래스 계약

```python
# Week 9
class QScintillaEditor(QsciScintilla):
    cursor_moved = pyqtSignal(str, int, int)  # file, line, col
    def load_file(self, path: Path) -> None: ...
    def goto_line(self, line: int) -> None: ...

# Week 9
class ContextWindow(QDockWidget):
    def __init__(self, event_bus: EventBus, reader: DatabaseReader): ...
    @pyqtSlot(str, int, int)
    def on_cursor_moved(self, file: str, line: int, col: int) -> None: ...

# Week 11
class SymbolWindow(QDockWidget):
    def __init__(self, event_bus: EventBus, index: SymbolIndex): ...
    @pyqtSlot(str)
    def on_file_opened(self, file: str) -> None: ...

# Week 13
class RelationQuery:
    def get_callers(self, node_id: NodeId, depth: int = 3) -> list[Relation]: ...
    def get_callees(self, node_id: NodeId, depth: int = 3) -> list[Relation]: ...
    def get_references(self, node_id: NodeId) -> list[Occurrence]: ...
    def get_overrides(self, node_id: NodeId) -> list[NodeId]: ...

# Week 10
class EventBus(QObject):
    symbol_selected = pyqtSignal(int)  # node_id
    file_opened = pyqtSignal(str, int)  # file, line
    cursor_moved = pyqtSignal(str, int, int)  # file, line, col
    layout_changed = pyqtSignal(str)  # layout_name
```

---

## 이벤트 플로우 (Phase 2 통합)

```
[사용자: 에디터에서 커서 이동]
    ↓
QScintillaEditor.cursorPositionChanged 내부 시그널
    ↓ (QTimer 150ms 디바운스)
EventBus.cursor_moved.emit(file, line, col)
    ↓
   ┌─────────────────────────────────────────────────┐
   │                                                 │
   ▼                                                 ▼
ContextWindow.on_cursor_moved          SymbolWindow (현재 심볼 강조만)
    ├─ DB 조회: 해당 위치의 심볼
    ├─ 선언부 로드
    └─ 미니 QScintilla 갱신


[사용자: Symbol Window 더블클릭]
    ↓
EventBus.file_opened.emit(file, line)
    ↓
Editor.load_file() + goto_line()
    ↓
커서 이동 → cursor_moved → ContextWindow / RelationWindow 자동 갱신


[사용자: Relation Window 항목 더블클릭]
    ↓
EventBus.symbol_selected.emit(node_id)
    ↓
   ┌─────────────────────────────────────────────────┐
   ▼                       ▼                         ▼
Editor.goto(...)       GraphScene.load_symbol(id)   ContextWindow 갱신
```

---

## 성능 목표 (Phase 2)

| 항목 | 목표 |
|------|------|
| Context Window 업데이트 | < 100ms (커서 이동 후) |
| Symbol Window 로드 (1000 심볼) | < 200ms |
| Relation Window 1단계 펼침 | < 150ms |
| Syntax decoration 초기 적용 | < 300ms (1,000 줄 파일) |
| 에디터 타이핑 반응 | < 16ms (60fps) |

---

## Phase 2 DoD (MVP DoD)

Evidence ledger: [`docs/generated/phase2/closeout-evidence.md`](../generated/phase2/closeout-evidence.md)

- [x] **4개 Source Insight 패널 모두 작동**: Context / Symbol / Relation / Syntax
  - Evidence: Context/Symbol/Relation UI tests, SyntaxDecorator and semantic decoration tests.
- [ ] 커서 이동 → 3개 패널 동시 업데이트 (150ms 내)
  - Partial evidence: `QScintillaEditor` debounce and Context Window cursor refresh are tested. A single end-to-end timing assertion for all three panels is still missing.
- [x] 3개 레이아웃 프리셋 저장/복원
  - Evidence: `tests/ui/test_layout_manager.py`.
- [x] Unused variable, deprecated call 데코레이션 on/off 가능
  - Evidence: preferences dialog and semantic decoration flow tests.
- [ ] Django (~5만 LoC) 프로젝트에서 MVP 시나리오 15가지 모두 통과
  - Partial evidence: `tests/fixtures/sample-django` MVP integration passes. Full-scale 50k LoC Django dogfooding is not evidenced.
- [x] 단위 테스트 커버리지 75%
  - Evidence: `bash scripts/run-tests.sh` reports 77 passed and 90% total coverage.
- [ ] **Beta 릴리스 태그** (외부 공개, GitHub Release)
  - No beta tag or GitHub Release evidence yet. Existing release tag evidence stops at `v0.1.0-alpha.1`.
- [ ] **리스크 게이트 G3 통과**: MVP 완성
  - Pending G3 disposition after Beta release and the full-scale Django/dogfooding decision.

### MVP 시나리오 (G3 통과 기준)

1. 프로젝트 인덱싱 (Shallow, 1분 이내)
2. 심볼 탭 열기 → 그래프 뷰 표시
3. 심도 슬라이더로 깊이 조정
4. Unsolved 심볼 회색 해치로 표시됨
5. 에디터에서 심볼 클릭 → 3 패널 동시 업데이트
6. Context Window에 선언부 표시
7. Symbol Window에서 필터링
8. Relation Window 확장 → 호출 관계 탐색
9. 더블클릭으로 정의 이동
10. 북마크 추가/제거
11. 히스토리 뒤로/앞으로
12. 검색바로 FQN 검색
13. 퍼지 자동완성 동작
14. 생성한 DB를 원본 Sourcetrail에서 열기 성공
15. 레이아웃 프리셋 저장/복원

---

## Phase 2 리스크

| 리스크 | 등급 | 대응 |
|--------|------|------|
| R-05 QScintilla 커스텀 렌더링 한계 | 🟡 | `QsciIndicator` 기반으로 우선 구현, 복잡한 효과는 Phase 5 |
| R-09 이벤트 루프 과부하 | 🟡 | QTimer 디바운스 150ms, 동시 업데이트 배치 처리 |
| R-11 mypy 통합 느림 | 🟡 | 이 Phase에서는 mypy 배제, Phase 4로 이월 |
| 도킹 레이아웃 깨짐 | 🟡 | `QSettings` 백업 + 복구 로직, 기본값 리셋 버튼 제공 |

---

## 수락 시나리오 (Phase 2 종료)

**시나리오 1**: Django 프로젝트 읽기 체험
1. `srm-index django/ --db django.srctrldb --shallow` (약 2분)
2. `srm-gui django.srctrldb`
3. 탭에 `django.db.models.Model` 입력
4. 그래프 뷰에 Model 클래스 중심 관계 표시
5. 에디터에 `models.py` 자동 열림
6. 커서를 `Model.__init__` 에 두면:
   - Context Window: `__init__` 선언부 표시
   - Symbol Window: `Model` 트리 아래 `__init__` 강조
   - Relation Window (Called by): 이 메서드를 호출하는 서브클래스 목록
7. Relation Window 항목 더블클릭 → 서브클래스 코드로 이동
8. 이동 후 모든 패널 자동 갱신

**시나리오 2**: 의미 기반 데코레이션
1. `django/contrib/auth/views.py` 열기
2. 사용되지 않는 import 문 회색 + 취소선
3. Deprecated `url()` 함수 호출이 노란 배경으로 표시
4. 설정에서 "Unused variable" 체크 해제 → 즉시 표시 사라짐

---

## 회고 (Phase 종료 후 작성)

**잘 된 점**:
-

**어려웠던 점**:
-

**다음 Phase로 이월된 항목**:
-

**타임라인 대비 실적**:
- 계획: 8주 / 실제: ?주

**성능 벤치마크 (Phase 2 종료 시)**:
- Context Window 업데이트: ?ms
- Symbol Window 로드 (1000 심볼): ?ms
- Relation 1단계 펼침: ?ms

**Beta 피드백 (외부)**:
- GitHub Issues 수:
- Discord/Reddit 반응:

**MVP 시나리오 통과율**:
- 15가지 중 ?가지 통과
