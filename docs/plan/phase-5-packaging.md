# Phase 5 · 나머지 기능 + 패키징/배포 (P3/P4 + Release)

| 메타 | 값 |
|------|-----|
| 기간 | **3주 (Week 29-31)** |
| 누적 | 31주 |
| 마일스톤 | **M5 — v1.0.0 Release** |
| 선행 조건 | Phase 4 RC2 완료, G5 통과 |

---

## 목표

남은 P3/P4 기능을 마무리하고, **Windows 단일 exe 설치 관리자로 배포**하여 v1.0.0 정식 릴리스.

---

## 다루는 기능 (P3/P4)

### P3 — 기타 생산성

**F11 — Search Project (전체 텍스트 검색)**
- 전체 파일 내용 검색 (ripgrep/grep 스타일)
- 정규식 / 대소문자 / Whole word 옵션
- 결과 그룹 (파일 → 라인)
- `Ctrl+Shift+F`

**F12 — Overview Scroller (미니맵)**
- 에디터 우측 미니맵 (QScintilla 기본 지원 + 커스텀)
- 검색 결과 / 에러 위치 마커

**F13 — Code Folding (접기)**
- 클래스/함수 단위 접기
- `Ctrl+Shift+[` / `Ctrl+Shift+]`

**F14 — Line Revision Marks (변경 마커)**
- Git diff 기반 (unstaged/staged/committed)
- 에디터 좌측 거터에 색상 바

**F15 — Master File List (MFL)**
- 프로젝트의 모든 파일 트리 뷰
- 필터 + 정렬 + 즐겨찾기

### P4 — 확장성

**F16 — Custom Language Parser (Tree-sitter)**
- Python 외 언어를 Tree-sitter 기반 간이 인덱싱
- YAML 설정으로 언어 추가 (`.srm-languages.yml`)

**F17 — Graph Export**
- PNG / SVG / DOT 내보내기
- 현재 뷰포트 또는 전체 그래프

**F18 — Directory Compare**
- 두 프로젝트 구조 비교
- 파일 차이, 심볼 차이

### Release — 패키징 & 배포

- PyInstaller 단일 폴더 번들
- Inno Setup 설치 관리자 (.exe)
- 코드 서명 (선택, 비용 발생 시 건너뜀)
- GitHub Releases 자동 업로드

---

## 산출물 (Deliverables)

| # | 산출물 | 위치 |
|---|--------|------|
| D5.1 | `ProjectSearchService` | `src/sourcetrail_remake/search/text_search.py` |
| D5.2 | `SearchPanel` | `src/sourcetrail_remake/ui/panels/search_panel.py` |
| D5.3 | `OverviewScroller` | `src/sourcetrail_remake/ui/editor/minimap.py` |
| D5.4 | Code Folding 통합 | `src/sourcetrail_remake/ui/editor/folding.py` |
| D5.5 | `GitRevisionProvider` | `src/sourcetrail_remake/core/git.py` |
| D5.6 | `MasterFileList` | `src/sourcetrail_remake/ui/panels/file_list.py` |
| D5.7 | `TreeSitterIndexer` | `src/sourcetrail_remake/indexer/treesitter.py` |
| D5.8 | `GraphExporter` | `src/sourcetrail_remake/ui/graph/export.py` |
| D5.9 | `DirectoryCompare` | `src/sourcetrail_remake/ui/dialogs/compare.py` |
| D5.10 | PyInstaller spec 파일 | `packaging/srm.spec` |
| D5.11 | Inno Setup 스크립트 | `packaging/installer.iss` |
| D5.12 | GitHub Release workflow | `.github/workflows/release.yml` |
| D5.13 | 아이콘 (.ico) + 리소스 | `packaging/resources/` |

---

## 주간 작업 계획

### Week 29: 나머지 기능 (1) — 검색 / 미니맵 / 폴딩

- D141: `ProjectSearchService` — ripgrep subprocess 또는 Python 자체 구현
- D142: `SearchPanel` — 결과 트리 (파일 → 라인), 클릭 시 에디터 이동
- D143: 정규식 / 대소문자 / Whole word 체크박스
- D144: `OverviewScroller` — QScintilla `setMarginType` + 커스텀 페인팅
- D145: Code Folding — QScintilla 기본 (`setFolding(QsciScintilla.BoxedTreeFoldStyle)`)

### Week 30: 나머지 기능 (2) — Git / MFL / Tree-sitter / Export / Compare

- D146: `GitRevisionProvider` — `subprocess.run(['git', 'diff', ...])`
- D147: 에디터 좌측 거터 색상 바 (`QsciMarker`)
- D148: `MasterFileList` — `QFileSystemModel` 확장, 즐겨찾기 기능
- D149: `TreeSitterIndexer` — tree-sitter 바인딩, JavaScript/TypeScript 우선 지원
- D150: YAML 언어 설정 (`.srm-languages.yml`) 파싱
- D151: `GraphExporter` — `QGraphicsScene.render()` → PNG, SVG 직접 생성, DOT 텍스트 출력
- D152: `DirectoryCompare` — 두 프로젝트 DB 비교, diff 트리 뷰

### Week 31: 패키징 & 배포 & v1.0.0

**Day 153-155: PyInstaller 번들**
- D153: PyInstaller spec 파일 작성 — hidden imports (Jedi, PyQt6, QScintilla, tree-sitter)
- D154: 번들 크기 최적화 (`--exclude-module` 으로 불필요한 의존성 제거)
- D155: 번들 실행 smoke test (srm.exe 실행 → GUI 표시 확인)

**Day 156-158: Inno Setup 설치 관리자**
- D156: Inno Setup 스크립트 작성 — 설치 경로, 시작 메뉴, 파일 연결 (.srctrldb)
- D157: 업데이트 로직 (기존 버전 감지 후 덮어쓰기)
- D158: 언인스톨러 동작 확인

**Day 159-161: 릴리스 자동화 & v1.0.0**
- D159: GitHub Actions `.github/workflows/release.yml` — 태그 push → build → installer 생성 → Release 업로드
- D160: 최종 회귀 테스트 — 모든 Phase 시나리오 통합 실행
- D161: **v1.0.0 릴리스 태그 push** + GitHub Release 공개
- D161: **리스크 게이트 G6 통과**: 배포 검증 (크린 머신 설치 성공)

---

## 주요 클래스 계약

```python
# Week 29
class ProjectSearchService:
    def search(self, query: str, regex: bool, case: bool, whole_word: bool) -> Iterator[SearchHit]: ...

@dataclass
class SearchHit:
    file: Path
    line: int
    col: int
    matched: str
    context_before: str
    context_after: str

# Week 30
class GraphExporter:
    def export_png(self, scene: QGraphicsScene, path: Path, dpi: int = 300) -> None: ...
    def export_svg(self, scene: QGraphicsScene, path: Path) -> None: ...
    def export_dot(self, scene: QGraphicsScene, path: Path) -> None: ...
```

---

## 배포 아키텍처

```
pyproject.toml (uv sync)
    ↓
PyInstaller
    ├─ --onedir  (단일 폴더, ~200MB)
    ├─ hidden-imports: jedi, parso, rope, PyQt6, QScintilla, tree-sitter-*
    └─ exclude: matplotlib, numpy (불필요)
    ↓
dist/srm/ (실행 폴더)
    ↓
Inno Setup (packaging/installer.iss)
    ├─ 설치 경로: C:\Program Files\Sourcetrail Remake\
    ├─ 시작 메뉴: Sourcetrail Remake
    ├─ 파일 연결: *.srctrldb → srm.exe
    └─ 언인스톨러
    ↓
srm-1.0.0-win-x64.exe (~150MB)
    ↓
GitHub Release (자동 업로드)
```

---

## 성능/품질 목표 (Phase 5)

| 항목 | 목표 |
|------|------|
| 설치 관리자 크기 | < 150MB |
| 첫 실행 시간 | < 5초 (exe 클릭 → 메인 윈도우) |
| 설치 시간 | < 30초 |
| Defender/Smart Screen 경고 | 없음 (또는 명시적 안내) |
| Tree-sitter 인덱싱 (TS 프로젝트) | < 5분 (10만 LoC) |
| 전체 텍스트 검색 (1만 파일) | < 2초 |

---

## Phase 5 DoD

- [ ] F11-F15 (P3) 모두 동작
- [ ] F16-F18 (P4) 모두 동작
- [ ] Windows 10/11 클린 머신에서 설치 관리자 실행 성공
- [ ] 시작 메뉴 바로 가기 정상 동작
- [ ] 파일 연결 (`.srctrldb` 더블클릭 → srm.exe 실행) 동작
- [ ] 언인스톨러가 완전히 제거
- [ ] Defender/Smart Screen 경고 없음 (또는 문서화된 우회 절차 제공)
- [ ] GitHub Release v1.0.0 공개 + 설치 관리자 첨부
- [ ] 단위 테스트 커버리지 80% 이상
- [ ] **리스크 게이트 G6 통과**: Release 검증

---

## Phase 5 리스크

| 리스크 | 등급 | 대응 |
|--------|------|------|
| R-12 PyInstaller 크기 폭발 | 🟡 | `--exclude-module` 로 불필요 의존성 제거, UPX 압축 |
| R-13 Defender 오탐 | 🟡 | 서명 없으면 SmartScreen 경고 → README 에 해결 절차 안내 |
| Inno Setup 설치 경로 권한 문제 | 🟡 | Program Files 대신 LocalAppData 옵션 제공 |
| Tree-sitter 바인딩 빌드 실패 | 🟢 | Phase 5 시작 전 격리 테스트 |
| 최종 회귀 테스트 누락 | 🔴 | 체크리스트 기반 매뉴얼 회귀 (80 시나리오) |

---

## 수락 시나리오 (Phase 5 종료 = v1.0.0)

**시나리오 1**: 신규 사용자 첫 설치
1. GitHub Release 에서 `srm-1.0.0-win-x64.exe` 다운로드
2. 더블클릭 → Inno Setup 설치 마법사
3. 다음 → 다음 → 설치 완료 (30초)
4. 시작 메뉴에서 "Sourcetrail Remake" 실행
5. 환영 화면 → 샘플 프로젝트 로드 → 그래프 표시 (5초 이내)

**시나리오 2**: 전체 기능 회귀
- 80개 시나리오 체크리스트 (Phase 0-5 DoD 기반)
- 모든 시나리오 통과 시 v1.0.0 태그

**시나리오 3**: Graph Export
1. Django `urls.py` 그래프 뷰 열기
2. 파일 → 내보내기 → PNG
3. 300 DPI로 저장, 블로그에 그림 삽입 가능 품질
4. SVG 로도 내보내기 → Inkscape 에서 열기 성공

---

## v1.0.0 릴리스 체크리스트

- [ ] 모든 Phase DoD 통과
- [ ] 테스트 커버리지 ≥ 80%
- [ ] README 완성 (설치 / 빠른 시작 / 스크린샷)
- [ ] CHANGELOG 작성
- [ ] LICENSE 파일 (GPL v3)
- [ ] 크레딧 페이지 (Sourcetrail / Source Insight 영감, Jedi/QScintilla 등)
- [ ] GitHub Release 공개 + 설치 관리자 첨부
- [ ] 홍보 포스트 (선택) — Reddit r/Python, Hacker News

---

## 회고 (Phase 종료 후 작성)

**잘 된 점**:
-

**어려웠던 점**:
-

**타임라인 대비 실적**:
- 계획: 3주 / 실제: ?주
- 전체 31주 / 실제: ?주

**v1.0.0 출시 직후 피드백 (첫 1주)**:
- GitHub Stars:
- Issues:
- 주요 피드백:

**다음 버전 (v1.1) 로 이월된 항목**:
-
