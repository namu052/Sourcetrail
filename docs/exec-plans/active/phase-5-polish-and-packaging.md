---
title: Phase 5 Polish and Packaging
status: Active
last_updated: 2026-04-25
---

# Phase 5 — 완성도 & 패키징

| 메타 | 값 |
|------|-----|
| 기간 | 3주 (Week 29-31) |
| 누적 | **31주 (v1.0.0 릴리스)** |
| 상태 | 📋 계획됨 |
| 마일스톤 | **M5 — v1.0.0 Release** |
| 선행 조건 | Phase 4 완료, RC 릴리스 피드백 수렴 |

## 목표

잔여 기능(F12-F18) 구현 + 배포 가능한 완성품으로 다듬기. 일반 사용자가 설치 후 바로 쓸 수 있는 수준의 **v1.0.0 정식 릴리스**.

## 다루는 기능

- **F12 — Overview Scroller** (minimap with semantic marks)
- **F13 — Code Folding** (중첩 블록 접기)
- **F14 — Line Revision Marks** (편집 추적)
- **F15 — Master File List** (팀 공유 프로젝트 설정)
- **F16 — Custom Language Parser 확장성**
- **F17 — Graph Export** (PNG/SVG/DOT)
- **F18 — Directory Compare** (최소 구현)
- **Visual Theme 시스템** (라이트/다크/커스텀)
- **패키징** (PyInstaller + Inno Setup)

## 산출물 (Deliverables)

| # | 산출물 | 위치 |
|---|--------|------|
| D5.1 | `OverviewScroller` 위젯 | `src/sourcetrail_remake/ui/editor/overview.py` |
| D5.2 | Code Folding 엔진 | `src/sourcetrail_remake/ui/editor/folding.py` |
| D5.3 | Line Revision 트래커 | `src/sourcetrail_remake/ui/editor/revision.py` |
| D5.4 | `MasterFileList` 포맷 (YAML) | `src/sourcetrail_remake/core/mfl.py` |
| D5.5 | Tree-sitter 기반 Custom Language 플러그인 API | `src/sourcetrail_remake/indexer/custom_language/` |
| D5.6 | Graph Export (PNG/SVG/DOT) | `src/sourcetrail_remake/ui/graph/export.py` |
| D5.7 | Directory Compare 다이얼로그 | `src/sourcetrail_remake/ui/dialogs/dir_compare.py` |
| D5.8 | Visual Theme 시스템 | `src/sourcetrail_remake/ui/themes/` |
| D5.9 | PyInstaller 빌드 스크립트 | `scripts/build_installer.ps1` |
| D5.10 | Inno Setup 인스톨러 스크립트 | `installer/setup.iss` |
| D5.11 | 사용자 매뉴얼 (최종) | `docs/user-manual/` |
| D5.12 | 릴리스 노트 | `CHANGELOG.md`, `docs/release-notes-v1.0.md` |

## 주간 작업 계획

### Week 29: 에디터 부가 기능

**Overview Scroller (F12)**
- D151: 스크롤바 옆 미니맵 위젯 (축소된 QsciScintilla 또는 커스텀 QPainter)
- D152: 함수/클래스 경계 표시 (색 블록)
- D153: 북마크 위치 표시
- D154: 검색 매치/리네임 대상 라인 표시
- D155: 변경된 라인 (Revision) 표시
- D156: 미니맵 클릭 → 해당 위치로 점프

**Code Folding (F13)**
- D157: QScintilla 기본 folding 활성화
- D158: 함수/클래스/if/for/while 블록 folding 지원
- D159: Fold-all / Unfold-all 명령
- D160: 세션 종료 시 fold 상태 저장 → 재개 시 복원
- D161: 지역 주석 블록 `# region` / `# endregion` 지원

**Line Revision Marks (F14)**
- D162: 편집 이벤트 훅 → 수정/추가/삭제 라인 추적
- D163: 마진에 색상 표시 (수정=노랑, 추가=초록, 삭제=빨강)
- D164: Git 연동 없이 세션 로컬 추적 (저장 시 리셋 옵션)

### Week 30: 확장성 & 외부 연동

**Visual Theme 시스템**
- D165: 테마 JSON 스키마 정의 (색상/폰트/아이콘 세트)
- D166: **Light / Dark** 기본 테마 2종
- D167: 테마 전환 다이얼로그 (실시간 미리보기)
- D168: 사용자 커스텀 테마 저장/불러오기
- D169: 그래프/에디터/패널 모두 테마 반영

**Custom Language Parser (F16)**
- D170: Tree-sitter 기반 플러그인 인터페이스
- D171: 최소 예제 플러그인 (Cython `.pyx` 또는 Python 스텁 `.pyi`)
- D172: Plugin discovery (`entry_points`) 또는 `plugins/` 폴더 스캔
- D173: 플러그인 개발자 문서

**Master File List (F15)**
- D174: 프로젝트 설정 YAML 포맷 — 상대 경로, 제외 패턴, 인덱싱 모드
- D175: Export: 현재 프로젝트 → `srm-project.yml`
- D176: Import: YAML에서 복원
- D177: Git에 체크인하여 팀원 간 공유

**Graph Export (F17)**
- D178: 현재 그래프 뷰 → PNG (고해상도 옵션)
- D179: 현재 그래프 뷰 → SVG (벡터)
- D180: 전체 그래프 → DOT (Graphviz 호환)

**Directory Compare (F18)**
- D181: 두 디렉터리 트리 비교 다이얼로그
- D182: 파일별 존재/크기/수정일 차이 표시
- D183: 심볼 레벨 diff (선택한 파일 쌍)

### Week 31: 패키징 & v1.0.0 릴리스

**Packaging**
- D184: PyInstaller spec 작성 (`sourcetrail_remake.spec`)
- D185: Windows .exe 빌드 (One-folder 모드)
- D186: Inno Setup 인스톨러 스크립트 — 시작 메뉴 바로가기, 제거 프로그램, 파일 연관(`.srctrldb`)
- D187: 아이콘, 라이선스(GPL v3), 사용 약관 포함
- D188: 코드 서명 (선택 — 인증서 구매 시)

**사용자 매뉴얼**
- D189: Getting Started (프로젝트 생성 → 인덱싱 → 탐색 흐름)
- D190: 패널별 사용법 (Context / Symbol / Relation / Search)
- D191: 키보드 단축키 치트시트
- D192: 자주 묻는 질문 (FAQ)
- D193: 트러블슈팅 가이드

**릴리스**
- D194: CHANGELOG.md 최종본
- D195: GitHub Release 작성 (인스톨러 첨부)
- D196: README.md 완성 (스크린샷, 설치 링크, 사용 예시)
- D197: **v1.0.0 태그 및 릴리스** 🎉
- D198: 릴리스 후 스모크 테스트 (깨끗한 Windows VM에서 설치 → 실행)

## 배포 아티팩트

| 파일 | 설명 | 크기 예상 |
|------|------|----------|
| `Sourcetrail_Remake_Setup_1.0.0.exe` | Inno Setup 인스톨러 | ~150 MB |
| `Sourcetrail_Remake_Portable_1.0.0.zip` | 포터블 버전 (압축) | ~180 MB |
| `sourcetrail_remake-1.0.0-py3-none-win_amd64.whl` | pip 설치용 휠 (선택) | ~5 MB (바이너리 제외) |
| `source-1.0.0.tar.gz` | 소스 배포 (GPL 준수) | ~2 MB |

## 시스템 요구사항 (v1.0.0)

- **OS**: Windows 10 (1809 이상) / Windows 11
- **아키텍처**: x64
- **RAM**: 최소 4GB, 권장 8GB
- **디스크**: 500MB (설치) + 프로젝트당 100MB~1GB (인덱스)
- **기타**: Microsoft Visual C++ Redistributable (인스톨러가 번들)

## Phase 5 DoD

- [ ] Overview Scroller가 함수/북마크/변경 라인 모두 시각화
- [ ] Code Folding 상태가 세션 간 유지
- [ ] Revision Marks가 편집 시 실시간 표시
- [ ] Light/Dark 테마 전환 < 1초
- [ ] Graph Export PNG/SVG/DOT 3종 모두 동작
- [ ] Master File List로 팀원 간 프로젝트 설정 공유 가능
- [ ] **Windows 10 VM에서 더블클릭 설치 → 실행 → 프로젝트 인덱싱** 전 과정 성공
- [ ] GitHub Release 공개
- [ ] 사용자 매뉴얼 모든 챕터 완성
- [ ] F1-F27 전체 기능 체크리스트 통과

## 위험 & 완화

| 위험 | 대응 |
|------|------|
| PyInstaller 바이너리 크기 초과 (>200MB) | UPX 압축, 불필요 모듈 제외 |
| Windows Defender 오탐 | 제외 리스트 제출, 가능하면 코드 서명 |
| Inno Setup 인스톨러 실패 시나리오 | 깨끗한 VM에서 3회 이상 테스트 |
| QScintilla DLL 누락 | `--collect-all=PyQt6.Qsci` 옵션 |
| 테마 전환 시 위젯 깜빡임 | 스타일시트 한 번에 적용, 개별 위젯 스타일링 금지 |
| 매뉴얼 작성 시간 부족 | Week 28 여유 시간부터 병행 작성 |

## 회고 (Phase 종료 후 작성)

- 잘 된 점:
- 어려웠던 점:
- v1.0.0 이후 로드맵으로 이월된 항목 (v1.1에 포함):
- 타임라인 대비 실적:
- 초기 사용자 피드백:
- 프로젝트 전체 회고 (8개월 여정):
