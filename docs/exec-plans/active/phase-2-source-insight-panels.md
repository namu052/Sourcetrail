---
title: Phase 2 Source Insight Panels
status: Active
last_updated: 2026-04-25
---

# Phase 2 — Source Insight 핵심 패널 (MVP 종료점)

| 메타 | 값 |
|------|-----|
| 기간 | 8주 (Week 9-16) |
| 누적 | **16주 (MVP 완성)** |
| 상태 | 📋 계획됨 |
| 마일스톤 | **M2 — MVP (Alpha → Beta)** |
| 선행 조건 | Phase 1 완료, 그래프 뷰 동작 |

## 목표

Source Insight의 정체성(DNA)인 4개 핵심 패널을 구현하여 MVP를 완성한다.

**Source Insight의 본질은 단일 기능이 아니라, Context/Symbol/Relation 패널이 에디터와 함께 항상 켜져 있고 자동 동기화되는 통합 UX다.** 이 철학을 PyQt6 기반으로 재현.

## 다루는 기능

- **F1 — Context Window**: 라이브 정의 프리뷰
- **F2 — Symbol Window**: 현재 파일 심볼 아웃라인
- **F3 — Relation Window (Tree/Outline 모드)**: Contains/Calls/References 3축
- **F4 — Syntax Formatting / Semantic Decoration**: 스코프 인식 색상

## 산출물 (Deliverables)

| # | 산출물 | 위치 |
|---|--------|------|
| D2.1 | `ContextWindow` 도킹 패널 | `src/sourcetrail_remake/ui/panels/context.py` |
| D2.2 | 그래프 노드 호버 프리뷰 팝업 | `src/sourcetrail_remake/ui/graph/hover_preview.py` |
| D2.3 | `SymbolWindow` 도킹 패널 | `src/sourcetrail_remake/ui/panels/symbol.py` |
| D2.4 | `RelationWindow` (Tree 모드) | `src/sourcetrail_remake/ui/panels/relation.py` |
| D2.5 | 다중 Relation Window + Lock 기능 | `src/sourcetrail_remake/ui/panels/relation_manager.py` |
| D2.6 | `CodeEditor` (QScintilla 통합) | `src/sourcetrail_remake/ui/editor/code_editor.py` |
| D2.7 | `SemanticHighlighter` | `src/sourcetrail_remake/ui/editor/semantic.py` |
| D2.8 | Syntax Decoration 엔진 | `src/sourcetrail_remake/ui/editor/decoration.py` |
| D2.9 | Panel ↔ Panel 동기화 이벤트 버스 | `src/sourcetrail_remake/core/event_bus.py` |

## 주간 작업 계획

### Week 9-10: Context Window (F1)

**Week 9**
- D41: `ContextWindow` 도킹 패널 (QDockWidget + 읽기 전용 QsciScintilla)
- D42: 심볼 선택 이벤트 구독 → `JediResolver.goto_definition()`
- D43: 정의 영역 추출 (함수/클래스 본문까지 포함)
- D44: 프리뷰 내에서 현재 심볼 라인 하이라이트
- D45: 자동 추적 on/off 토글 + Lock 버튼

**Week 10**
- D46: **그래프 노드 호버 툴팁 프리뷰** (Source Insight 특유의 UX)
- D47: 타입 선언 재귀 디코딩 (`self.session: Session` → `Session` 클래스 내부)
- D48: 변수 선택 시 타입 체인 추적 (포인터/참조 연쇄)
- D49: 여러 정의 후보 처리 (오버로드, 여러 파일의 동명 심볼)
- D50: Week 9-10 통합 테스트

### Week 11: Symbol Window (F2)

- D51: `SymbolWindow` 도킹 패널 (QTreeView + QStandardItemModel)
- D52: 현재 활성 에디터 파일의 심볼 추출 (Parso AST)
- D53: 정렬 옵션 구현 (이름순 / 라인순 / 타입순)
- D54: 심볼 타입별 아이콘 (class/func/method/field/property)
- D55: 더블클릭 → 에디터 해당 라인으로 점프, 스코프 들여쓰기 표시

### Week 12: Relation Window Tree Mode (F3)

- D56: `RelationWindow` 도킹 패널 (QTreeWidget 기반 Outline)
- D57: 관계 축 필터: Contains / Calls / Called By / References / Inherits / Overrides
- D58: 트리 노드 확장 시 lazy-load (1 레벨씩)
- D59: **Graph / Tree 토글 버튼** (같은 데이터의 두 뷰)
- D60: **다중 Relation Window 동시 오픈** + 개별 Lock

### Week 13-16: Editor + Syntax Formatting (F4)

**Week 13 — Editor 기반**
- D61: `CodeEditor` (QsciScintilla 상속) 기본 통합
- D62: Python 렉서 + 탭/인덴트 설정
- D63: 파일 열기/저장, Undo/Redo, 검색/바꾸기 기본
- D64: 멀티 버퍼 탭 (QTabWidget central widget)
- D65: 마진 (줄 번호, 폴딩, 북마크, 리비전)

**Week 14 — Semantic Highlighter**
- D66: `SemanticHighlighter` — Jedi `get_names()` 결과를 QsciStyle로 매핑
- D67: **스코프 기반 색상 차등**:
  - 로컬 변수 / 함수 파라미터 / 모듈 전역 / 클래스 멤버 / 인스턴스 속성
- D68: 외부 패키지 심볼은 흐린 색상 (프로젝트 vs external 구분)
- D69: 현재 커서 아래 심볼의 모든 참조를 라이브 하이라이트 (scope-aware)
- D70: Week 14 회귀 테스트

**Week 15 — Syntax Decoration**
- D71: `self` / `cls` 특별 스타일 (이탤릭)
- D72: 데코레이터 특별 스타일 (`@property`, `@classmethod` 등)
- D73: 중첩 괄호 크기 차등 (Painter 오버라이드)
- D74: 연산자 시각 치환 옵션 (`->` → `→`, `**` → 상첨자) — 기본 off
- D75: 괄호 자동 매칭 하이라이트

**Week 16 — 닫는 블록 & MVP QA**
- D76: 닫는 블록 auto-annotation (`# end if cond`, `# end def foo`) — 렌더링만, 텍스트 수정 아님
- D77: **Panel ↔ Panel 동기화** 최종 정비:
  - 에디터 커서 이동 → Symbol Window 선택 업데이트
  - Symbol Window 선택 → 에디터 점프 + Context Window 프리뷰
  - 그래프 노드 선택 → 모든 패널 동기화
- D78: MVP 성능 튜닝
- D79: MVP 최종 QA — 첨부 이미지 재현 검증 + 자가 분석(dogfooding)
- D80: **Beta 릴리스 준비** (GitHub Release 초안)

## Panel 동기화 이벤트 버스

```python
# src/sourcetrail_remake/core/event_bus.py
class EventBus(QObject):
    symbol_selected = pyqtSignal(NodeId)          # 심볼 선택 (그래프/트리/에디터 공통)
    file_opened = pyqtSignal(Path)                # 에디터 파일 열기
    cursor_moved = pyqtSignal(Path, int, int)     # 에디터 커서 이동
    relation_lock_toggled = pyqtSignal(int, bool) # Relation Window ID + lock
    bookmark_added = pyqtSignal(BookmarkData)
```

각 패널은 이벤트 버스를 통해 느슨하게 결합 — Source Insight의 "항상 동기화" 철학을 이벤트 구독 모델로 구현.

## MVP 수락 시나리오 (자가 호스팅 dogfooding)

MVP가 완성되면 **Sourcetrail_Remake 자체의 소스코드를 자신으로 분석**할 수 있어야 한다:

1. 프로젝트 열기 → `src/sourcetrail_remake/` 인덱싱 (< 30초)
2. `IndexerService` 심볼 선택 → Context Window 정의 표시
3. Symbol Window에서 클래스 메서드 확인
4. Relation Window (Calls)로 `IndexerService.index()` 의 호출 체인 추적
5. Editor에서 스코프별 색상으로 `self.project` vs 로컬 `project` 변수 구분 가능
6. 퍼지 검색으로 `Writ` 입력 → `DatabaseWriter` 매칭

## 성능 목표 (Phase 2)

| 항목 | 목표 |
|------|------|
| 심볼 선택 → Context Window 프리뷰 | < 200ms |
| 파일 열기 → Symbol Window 표시 | < 500ms (10만 줄 파일 기준) |
| 에디터 Semantic Highlighting | < 1초 (초기), 증분 < 100ms |
| Relation Window 1 레벨 lazy-load | < 300ms |

## Phase 2 DoD (= MVP 완성 기준)

Evidence ledger: [`docs/generated/phase2/closeout-evidence.md`](../../generated/phase2/closeout-evidence.md)

- [ ] F1 Context Window: 그래프/에디터 모두에서 호버/선택 시 정의 표시
  - Partial evidence: editor cursor and Context Window refresh are tested; graph hover preview evidence is not present.
- [ ] F2 Symbol Window: 3가지 정렬 모드, 더블클릭 점프
  - Partial evidence: current Symbol Window tests cover outline, filter, access, icon, declaration/alphabetical sort, and double-click jump. The "3가지 정렬 모드" wording is not fully evidenced.
- [ ] F3 Relation Window: Tree/Graph 토글, 3축 필터, 다중 창 + Lock
  - Partial evidence: Relation Window tree tabs, lazy loading, depth, empty state, recursive markers, and selection are tested. Graph/Tree toggle and multi-window Lock are not evidenced.
- [ ] F4 Editor: 스코프별 색상, self/cls/데코레이터 스타일, 닫는 블록 annotation
  - Partial evidence: SyntaxDecorator, semantic analyzer aggregation, unused/deprecated/undefined markers, and decoration preferences are tested. Closing-block annotation and the exact self/cls scope styling are not evidenced.
- [ ] **자가 호스팅 dogfooding 시나리오 6종 전부 통과**
  - Partial evidence: sample Django MVP integration passes. Full Sourcetrail_Remake self-analysis dogfooding is not evidenced.
- [ ] Beta 릴리스 (GitHub Release + 내부 공개)
  - Draft prepared: [`docs/generated/phase2/beta-release-draft.md`](../../generated/phase2/beta-release-draft.md). Proposed tag: `v0.2.0-beta.1`. Tag not created.
- [x] 테스트 커버리지 80% 달성
  - Evidence: `bash scripts/run-tests.sh` reports 77 passed and 90% total coverage.

## 위험 & 완화

| 위험 | 대응 |
|------|------|
| QScintilla 커스텀 렌더링 한계 | QsciStyle 최대한 활용 + QPainter 오버라이드로 decoration 구현 |
| 패널 동기화 피드백 루프 | 이벤트 버스에 시그널 소스 태그 + 디바운싱 |
| Jedi 분석 지연으로 UI 버벅임 | 모든 Jedi 호출을 `QThread` + 캐시 레이어 |
| MVP 범위 팽창 | Phase 3 기능 요청은 무조건 이월 (scope creep 방지) |
| 닫는 블록 annotation 오렌더 | QScintilla margin annotation API 우선 시도, 실패 시 inline annotation |

## 회고 (Phase 종료 후 작성)

- 잘 된 점:
- 어려웠던 점:
- 다음 Phase로 이월된 항목:
- 타임라인 대비 실적:
- MVP 배포 후 피드백:
