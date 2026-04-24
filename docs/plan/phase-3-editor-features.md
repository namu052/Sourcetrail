# Phase 3 · 에디터 생산성 기능 (P2)

| 메타 | 값 |
|------|-----|
| 기간 | **6주 (Week 17-22)** |
| 누적 | 22주 |
| 마일스톤 | **M3 — Productivity** (RC1 릴리스) |
| 선행 조건 | Phase 2 MVP/Beta 완료, G3 통과 |

---

## 목표

Source Insight의 진짜 경쟁력인 **대규모 코드베이스에서의 생산성 도구**들을 구현한다.
"읽기"에서 "쓰기/리팩토링"으로 영역 확장.

---

## 다루는 기능 (P2)

### F5 — Smart Rename (지능형 이름 변경)
- 심볼 단위 리네임 (변수, 함수, 클래스, 모듈)
- 스코프 인식 (같은 이름의 다른 스코프 변수 보호)
- Preview → Apply 플로우 (QDialog)
- Rope 라이브러리 기반
- Undo 지원 (변경 전 스냅샷)

### F6 — Fuzzy Symbol Lookup (Ctrl+P 퀵 오픈)
- 프로젝트 전체 심볼을 퍼지 검색
- rapidfuzz 기반 (Levenshtein distance)
- `Ctrl+P` 단축키 (Source Insight 호환)
- 실시간 필터 (< 50ms per keystroke)
- 최근 선택 히스토리 상단 고정

### F7 — Lookup References (즉시 참조 찾기)
- 현재 심볼의 모든 참조를 한 번에 표시
- Relation Window의 "Referenced by"와 동일한 데이터, 다른 UX
- 결과 리스트 + 미니 프리뷰
- `Shift+F12` 단축키
- 파일별 그룹핑

### F8 — Layouts A/B/C/D (작업 흐름별 레이아웃)
- A: Reading (에디터 큰 중앙, 사이드 패널 작게)
- B: Graph-centric (그래프 뷰 중앙)
- C: Refactor (에디터 2 개 분할)
- D: Custom (사용자 저장)
- `Ctrl+Alt+1~4` 로 빠른 전환

### F9 — Bookmarks+ (고급 북마크)
- 파일:라인 북마크 (Phase 1의 심볼 북마크와 별도)
- 태그 지정 (`TODO`, `REVIEW`, 사용자 정의)
- 북마크 패널 (필터/정렬/이동)
- 프로젝트당 북마크 DB 저장

### F10 — Clip Window (클립 스크래치)
- 코드 조각 임시 저장
- 드래그&드롭 에디터 → 클립, 클립 → 에디터
- 제목 + 태그 + 메모
- 프로젝트별 클립 저장 (`.srm-clips`)

---

## 산출물 (Deliverables)

| # | 산출물 | 위치 |
|---|--------|------|
| D3.1 | `RopeRenameService` | `src/sourcetrail_remake/refactor/rename.py` |
| D3.2 | `RenameDialog` (preview + apply) | `src/sourcetrail_remake/ui/dialogs/rename.py` |
| D3.3 | `SymbolFuzzyIndex` | `src/sourcetrail_remake/search/fuzzy.py` |
| D3.4 | `QuickOpenDialog` | `src/sourcetrail_remake/ui/dialogs/quick_open.py` |
| D3.5 | `ReferencesDialog` | `src/sourcetrail_remake/ui/dialogs/references.py` |
| D3.6 | `LayoutManager` 확장 (A/B/C/D) | `src/sourcetrail_remake/ui/layout_manager.py` |
| D3.7 | `BookmarkStore` (파일:라인 기반) | `src/sourcetrail_remake/core/bookmarks.py` |
| D3.8 | `BookmarkPanel` | `src/sourcetrail_remake/ui/panels/bookmarks.py` |
| D3.9 | `ClipStore` | `src/sourcetrail_remake/core/clips.py` |
| D3.10 | `ClipWindow` | `src/sourcetrail_remake/ui/panels/clip_window.py` |
| D3.11 | Undo 스냅샷 시스템 | `src/sourcetrail_remake/refactor/undo.py` |

---

## 주간 작업 계획

### Week 17-18: Smart Rename (가장 어려운 기능)

**Week 17**
- D81: Rope 라이브러리 통합 (`rope.base.project.Project`)
- D82: `RopeRenameService.preview(node_id, new_name)` — 영향받는 파일 수집
- D83: 스코프 충돌 감지 (같은 이름 다른 스코프 경고)
- D84: `RenameDialog` UI (변경 전/후 파일별 diff 표시)
- D85: Apply → 파일 시스템 쓰기 + 인덱스 갱신

**Week 18**
- D86: Undo 스냅샷 (변경 전 파일 백업, `.srm-undo/` 숨김 디렉터리)
- D87: 실패 시 롤백 (원자적 처리 — 하나라도 실패하면 전체 되돌림)
- D88: 리네임 후 자동 재인덱싱 (백그라운드 QThread)
- D89: 테스트 케이스 — 변수/함수/클래스/모듈 각각
- D90: Edge case — 오버라이드 메서드 리네임 (전 서브클래스 추적)

### Week 19: Fuzzy Lookup & References

- D91: `SymbolFuzzyIndex` — 인덱싱 시점에 `(fqn, name, node_id)` 플랫 리스트 구축
- D92: rapidfuzz `process.extract()` 활용, 가중치 (exact > prefix > fuzzy)
- D93: `QuickOpenDialog` — `QLineEdit` + `QListView` (50ms 디바운스)
- D94: 최근 선택 히스토리 상단 고정 (`QSettings` 저장)
- D95: `ReferencesDialog` — Shift+F12, 결과 그룹핑 + 미니 프리뷰

### Week 20: Layouts A/B/C/D

- D96: 레이아웃 A (Reading) — 에디터 중앙 70%, Context/Symbol 오른쪽
- D97: 레이아웃 B (Graph-centric) — GraphView 중앙, 에디터 하단
- D98: 레이아웃 C (Refactor) — 에디터 2개 수평 분할 (`QSplitter`)
- D99: 레이아웃 D (Custom) — 현재 상태 저장 다이얼로그
- D100: `Ctrl+Alt+1~4` 단축키 + 메뉴 항목

### Week 21: Bookmarks+ & Clip Window

- D101: `BookmarkStore` — SQLite 테이블 (`file`, `line`, `tag`, `note`, `created_at`)
- D102: 에디터 좌측 거터에 북마크 마커 (QScintilla margin)
- D103: `BookmarkPanel` — 테이블 뷰 + 태그 필터
- D104: `ClipStore` + `ClipWindow` — 드래그&드롭 지원 (`QMimeData`)
- D105: 클립 내보내기/가져오기 (JSON)

### Week 22: 통합 테스트 & RC1

- D106: Rename 회귀 테스트 (Django, Requests, Flask)
- D107: 모든 단축키 충돌 검사 (`QKeySequence` 중복 탐지)
- D108: 부하 테스트 — 10만 LoC 프로젝트 Fuzzy Lookup < 50ms 검증
- D109: 단위 테스트 커버리지 78%
- D110: **RC1 릴리스 태그**
- D110: **리스크 게이트 G4 통과**: Rename 정확도 ≥ 95%

---

## 주요 클래스 계약

```python
# Week 17
class RopeRenameService:
    def preview(self, node_id: NodeId, new_name: str) -> RenamePreview:
        """영향받는 파일 + 라인 + 새 내용을 미리 계산"""
        ...
    def apply(self, preview: RenamePreview) -> RenameResult: ...
    def undo(self, result: RenameResult) -> None: ...

class RenamePreview:
    affected_files: list[Path]
    changes: list[FileChange]
    conflicts: list[ScopeConflict]

# Week 19
class SymbolFuzzyIndex:
    def build(self, db: DatabaseReader) -> None: ...
    def search(self, query: str, limit: int = 50) -> list[FuzzyResult]: ...

# Week 21
class BookmarkStore:
    def add(self, file: str, line: int, tag: str, note: str) -> BookmarkId: ...
    def list_by_tag(self, tag: str) -> list[Bookmark]: ...
    def list_by_file(self, file: str) -> list[Bookmark]: ...
    def remove(self, bm_id: BookmarkId) -> None: ...
```

---

## 성능 목표 (Phase 3)

| 항목 | 목표 |
|------|------|
| Fuzzy Lookup (10만 심볼) | < 50ms |
| Rename Preview (100 affected files) | < 2초 |
| Rename Apply (100 files) | < 5초 |
| References (1,000 ref) | < 500ms |
| 레이아웃 전환 | < 200ms |

---

## Phase 3 DoD

- [ ] Smart Rename: Django 프로젝트에서 클래스 리네임 성공, 영향 범위 100% 추적
- [ ] Rename Undo 동작 확인
- [ ] Fuzzy Lookup: 10만 심볼 기준 50ms 이하
- [ ] References: `Shift+F12` 동작, 파일별 그룹핑
- [ ] 4가지 레이아웃 전환 (`Ctrl+Alt+1~4`) 동작
- [ ] Bookmarks+: 태그 기반 필터, 저장 유지
- [ ] Clip Window: 드래그&드롭 동작
- [ ] 단위 테스트 커버리지 78%
- [ ] **RC1 릴리스 태그**
- [ ] **리스크 게이트 G4 통과**: Rename 정확도 ≥ 95% (샘플 100건 수동 검증)

---

## Phase 3 리스크

| 리스크 | 등급 | 대응 |
|--------|------|------|
| R-07 Rope 불안정성 | 🟡 | 사전 격리 테스트, 실패 시 스냅샷 기반 자체 구현 fallback |
| R-01 동적 참조 누락 (Rename) | 🔴 | Preview UI에 "감지 불가능한 참조 경고" 명시 |
| 드래그&드롭 MIME 타입 충돌 | 🟢 | 커스텀 MIME type `application/x-srm-clip` 사용 |
| Undo 스냅샷 디스크 사용 | 🟡 | 30일 보관 후 자동 삭제 |

---

## 수락 시나리오 (Phase 3 종료)

**시나리오 1**: 대규모 리네임
1. Django 프로젝트에서 `HttpResponse` 를 `Http200Response` 로 리네임 시도
2. Preview 창에 영향받는 파일 500개 표시
3. 스코프 충돌 3건 표시 (경고)
4. 사용자가 3건 건너뛰기 선택
5. Apply → 497개 파일 수정, 5초 이내
6. Undo → 모두 복원

**시나리오 2**: Fuzzy Quick Open
1. `Ctrl+P` 누름
2. `"sessm"` 입력
3. `SessionManager`, `session_mgr`, `SessionMaker` 등 퍼지 매칭 결과 표시
4. 첫 키스트로크부터 결과까지 < 50ms

**시나리오 3**: Layout 전환
1. 리딩 모드 (`Ctrl+Alt+1`) → 에디터 크게
2. 리팩토링 (`Ctrl+Alt+3`) → 에디터 2분할, 좌우에 원본/대상 파일
3. Ctrl+Alt+4로 저장된 custom 모드 복귀

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

**성능 벤치마크 (Phase 3 종료 시)**:
- Fuzzy Lookup (10만 심볼): ?ms
- Rename (100 files): ?초

**RC1 피드백**:
-

**Rename 정확도 샘플 100건**:
- 성공: ?건
- 실패: ?건 (원인:)
