---
title: Phase 3 Editor Productivity
status: Active
last_updated: 2026-04-25
---

# Phase 3 — 에디터 기능 강화

| 메타 | 값 |
|------|-----|
| 기간 | 6주 (Week 17-22) |
| 누적 | 22주 |
| 상태 | 📋 계획됨 |
| 마일스톤 | M3 — Productivity |
| 선행 조건 | Phase 2 MVP 완성, 자가 호스팅 가능 |

## 목표

MVP에 생산성 기능을 추가하여 **일상적으로 사용 가능한 실전 도구** 수준으로 끌어올린다.

## 다루는 기능

- **F5 — Smart Rename** (Rope 기반 스코프 인식 리네이밍)
- **F6 — Fuzzy Lookup** (Ctrl+P 스타일 글로벌 심볼 팔레트)
- **F7 — Lookup References** (DB 기반 정확한 역참조 리스트)
- **F8 — Layouts A/B/C/D** (4개 레이아웃 프리셋)
- **F9 — Bookmarks+** (메모/태그/세트)
- **F10 — Clip Window** (다중 클립보드)
- **F11 — Search Project** (멀티파일 고급 검색)

## 산출물 (Deliverables)

| # | 산출물 | 위치 |
|---|--------|------|
| D3.1 | `RenameService` (Rope 래퍼) | `src/sourcetrail_remake/refactor/rename.py` |
| D3.2 | `RenameDialog` (미리보기) | `src/sourcetrail_remake/ui/dialogs/rename.py` |
| D3.3 | 글로벌 Lookup 팔레트 | `src/sourcetrail_remake/ui/palette/` |
| D3.4 | `SearchService` (멀티파일 검색 엔진) | `src/sourcetrail_remake/search/service.py` |
| D3.5 | `SearchResultsPanel` | `src/sourcetrail_remake/ui/panels/search_results.py` |
| D3.6 | `ReferencesPanel` | `src/sourcetrail_remake/ui/panels/references.py` |
| D3.7 | Layout manager (A/B/C/D) | `src/sourcetrail_remake/ui/layouts/manager.py` |
| D3.8 | `BookmarkWindow` + 저장/로드 | `src/sourcetrail_remake/ui/panels/bookmark.py` |
| D3.9 | `ClipWindow` + 스니펫 관리 | `src/sourcetrail_remake/ui/panels/clip.py` |

## 주간 작업 계획

### Week 17-18: Smart Rename (F5)

**Week 17**
- D81: Rope `Project` 세션 통합, 프로젝트 루트 인식
- D82: 커서 위치 → Rope `Name` 해석
- D83: `RenameService.preview()` — 변경 예정 파일/라인 수집
- D84: 충돌 감지 (동일 스코프 내 이름 중복)
- D85: 주석/docstring 포함 여부 옵션

**Week 18**
- D86: `RenameDialog` — 미리보기 트리뷰 (파일별 그룹, before/after diff)
- D87: 선택적 적용 (특정 occurrence 제외 가능)
- D88: Undo 지원 (Rope changelist → QUndoStack)
- D89: 실패 시 롤백 + 에러 메시지
- D90: 대규모 프로젝트(~5만 LoC) 리네임 테스트

### Week 19-20: Fuzzy Lookup + Search (F6 + F7 + F11)

**Week 19 — Fuzzy Lookup (F6)**
- D91: Ctrl+P 글로벌 팔레트 오버레이 (`QDialog` frameless)
- D92: rapidfuzz 기반 심볼 매칭 — CamelCase/snake_case 자동 경계 인식
- D93: 최근 선택 히스토리 가중치 (MRU)
- D94: 심볼 타입 필터 (`@` 함수, `#` 클래스, `$` 파일)
- D95: 키보드 네비게이션 + Enter로 심볼 열기

**Week 20 — Search Project (F11) + Lookup References (F7)**
- D96: `SearchService` — 멀티파일 검색 엔진
- D97: Regex / keyword expression (암묵적 AND) / Boolean / proximity
- D98: `SearchResultsPanel` — 파일별 그룹화, 소스 링크 활성화
- D99: `ReferencesPanel` — DB 기반 정확한 역참조 + 2-3줄 컨텍스트
- D100: 주석/비활성 코드 제외 옵션, 결과 내 추가 검색

### Week 21: Bookmarks+ & Clip Window (F9 + F10)

- D101: `BookmarkWindow` 도킹 패널
- D102: 북마크에 커스텀 이름/메모/태그 (Ctrl+F2 스타일)
- D103: 북마크 세트 저장/로드 (JSON, 프로젝트별)
- D104: Overview Scroller 연동 준비 (Phase 5와 연결)
- D105: `ClipWindow` — 복사 히스토리 자동 누적(20개) + 수동 고정 스니펫
- D106: Placeholder 치환 (`$date$`, `$filename$`, `$author$`)
- D107: 드래그 앤 드롭으로 에디터에 삽입

### Week 22: Layouts A/B/C/D (F8)

- D108: `LayoutManager` — `QMainWindow.saveState/restoreState` 활용
- D109: 4개 프리셋 슬롯 (기본명: Explore / Edit / Analyze / Custom)
- D110: 단축키 `Ctrl+Alt+1/2/3/4` 전환
- D111: 레이아웃 전환 애니메이션 (부드러운 fade)
- D112: 현재 레이아웃 저장 버튼 (툴바)
- D113: 레이아웃 설정 JSON export/import
- D114: 프리셋 편집 다이얼로그 (이름 변경, 리셋)
- D115: **Phase 3 통합 테스트** — 모든 단축키 충돌 검사, 생산성 시나리오 end-to-end

## 키보드 단축키 체계 (Phase 3 기준)

| 단축키 | 기능 |
|--------|------|
| `Ctrl+P` | Fuzzy Lookup 팔레트 |
| `Ctrl+Shift+F` | Search Project |
| `Ctrl+Shift+R` | Smart Rename |
| `Shift+F12` | Lookup References |
| `F12` | Go to Definition |
| `Alt+←` / `Alt+→` | 히스토리 뒤로/앞으로 |
| `Ctrl+F2` | 북마크 추가 (메모 포함) |
| `Ctrl+Alt+1..4` | Layout A/B/C/D |
| `Ctrl+Shift+V` | Clip Window 팝업 |

> 모든 단축키는 Phase 5에서 사용자 커스터마이징 가능해질 예정.

## 성능 목표 (Phase 3)

| 항목 | 목표 |
|------|------|
| Fuzzy Lookup 첫 글자 입력 → 결과 표시 | < 50ms (10만 심볼 기준) |
| Search Project (Regex) | < 2초 (10만 LoC 기준) |
| Lookup References | < 200ms (DB 쿼리) |
| Layout 전환 | < 100ms |
| Rename 미리보기 생성 | < 3초 (중규모 프로젝트) |

## Phase 3 DoD

- [ ] Django 샘플 프로젝트에서 Smart Rename 안전하게 작동, 회귀율 < 1%
- [ ] Fuzzy Lookup이 10만 심볼에서 < 50ms 응답
- [ ] Search Results의 소스 링크 클릭 시 에디터 정확 점프
- [ ] 4개 레이아웃 프리셋 즉시 전환
- [ ] 북마크 세트 저장/로드 + 다른 머신에서 복원 확인
- [ ] Clip Window에서 드래그로 스니펫 삽입
- [ ] 테스트 커버리지 80% 유지

## 위험 & 완화

| 위험 | 대응 |
|------|------|
| Rope 기반 Rename 실패/불안정 | 실패 시 LibCST 기반 재작성 (리스크 게이트 Week 22) |
| 대형 프로젝트 검색 메모리 사용 | 스트리밍 결과 + 결과 상한 (기본 10,000) |
| Fuzzy Lookup 인덱스 크기 | LRU 캐시 + 디스크 직렬화 |
| Layout JSON 스키마 변경 | 버전 필드 추가, 마이그레이션 함수 |
| 단축키 충돌 | Phase 3 마지막 날 충돌 검사 스크립트 |

## 회고 (Phase 종료 후 작성)

- 잘 된 점:
- 어려웠던 점:
- 다음 Phase로 이월된 항목:
- 타임라인 대비 실적:
