# 01 · 요구사항 명세 — 27개 기능 + 우선순위

> 첨부 이미지의 필수 요소(P0) + Source Insight DNA(P1) + 생산성(P2-P3) + 옵션(P4) + Python 차별화(P5).

---

## 요약 테이블

| 우선순위 | 기능 수 | Phase | 근거 |
|---------|---------|-------|------|
| **P0** (필수, 이미지) | 이미지의 모든 요소 | Phase 1 | 사용자 첨부 이미지 명시 |
| **P1** (SI DNA) | F1-F4 (4개) | Phase 2 | Source Insight의 정체성 |
| **P2** (생산성) | F5-F10 (6개) | Phase 3 | 일상 사용성 |
| **P3** (완성도) | F11-F15 (5개) | Phase 3/5 | 사용자 요청 빈도 |
| **P4** (옵션) | F16-F18 (3개) | Phase 5 | 확장성/내보내기 |
| **P5** (Python 특화) | F19-F27 (9개) | Phase 4 | 경쟁 도구 대비 차별화 |
| **합계** | **27개** | — | — |

---

## P0 · 필수 기능 (첨부 이미지 기반) — Phase 1

### P0.1 네비게이션 바
- **탭 바**: 심볼별 멀티 탭. 예: `app.models.session···ession.is_expired`. 원형 아이콘으로 타입 표시.
- **뒤로/앞으로/홈 버튼**: 히스토리 네비게이션. 가운데 아이콘 클릭 시 드롭다운.
- **새로고침**: 인덱스 재파싱.
- **검색바**: Fully Qualified Name 표시 + 라이브 자동완성.
- **북마크 ★**: 추가/제거/목록.
- **메뉴 버튼**: 설정/도구.

### P0.2 그래프 뷰 시각화
- **클래스 컨테이너 노드**: 둥근 사각형, `▶` 토글(접기/펼치기), 우측 카운트 배지.
- **멤버 노드**: 컨테이너 내부 중첩.
- **타입별 색상**:
  - 🟠 오렌지 = 함수/메서드
  - 🔵 블루 = 필드/속성
  - 🔳 회색 해치 = **unsolved symbol** ← 핵심
- **현재 선택 심볼 강조**: 진한 배경 + 굵은 테두리.
- **엣지 타입**:
  - 실선 오렌지 = **호출(Call)**
  - 점선 블루 = **멤버 접근(Member Access)**
- **엣지 bundling**: 동일 목적지 다중 엣지 묶기.

### P0.3 그래프 제어
- **좌측 세로 슬라이더**: **심도(Depth)** 제어 — BFS 확장 반경.
- **좌하단 `+/-`**: 줌 인/아웃.
- **좌측 아이콘 바**: 레이아웃 토글(수평/수직), 관계 방향 전환 등.
- **우하단 `?`**: 도움말.

### P0.4 "Unsolved Symbol" 명시적 처리
- Python 파서가 해결 못 한 참조를 **감추지 않고** 노드로 표시.
- 회색 해치 패턴 + "unsolved symbol" 라벨.
- 이 철학은 Phase 4의 Type Hint/Duck Typing과 연결됨.

---

## P1 · Source Insight DNA (최우선) — Phase 2

### F1 · Context Window (라이브 정의 프리뷰)
- 선택된 심볼의 정의를 **자동 추적**하여 독립 패널에 실시간 표시.
- 그래프 노드 호버 시 팝업 프리뷰.
- 타입 선언 재귀 디코딩 (`self.session: Session` → `Session` 클래스 내부까지).
- Lock 버튼으로 추적 고정.

### F2 · Symbol Window (현재 파일 아웃라인)
- 현재 열린 파일의 모든 심볼을 **트리 형태**로 표시.
- 정렬: 이름순 / 라인번호순 / 타입순.
- 타입별 아이콘 (class/func/method/field/property).
- 더블클릭 → 에디터 점프.

### F3 · Relation Window (Tree/Outline 모드)
- 그래프 데이터를 **트리 형태로도** 렌더링 (Source Insight 스타일).
- 관계 축 필터: **Contains / Calls / Called By / References / Inherits / Overrides**.
- Graph ↔ Tree 토글.
- **다중 창 동시 오픈** + 개별 Lock.

### F4 · Syntax Formatting / Semantic Decoration
- 단순 하이라이팅이 아닌 **스코프 기반** 색상:
  - 로컬 / 파라미터 / 모듈 전역 / 클래스 멤버 / 인스턴스 속성.
- `self`/`cls`/데코레이터 특별 스타일.
- 중첩 괄호 크기 차등.
- 닫는 블록 auto-annotation (`# end if cond`).
- 연산자 시각 치환 옵션 (`->` → `→`).

---

## P2 · 생산성 기능 — Phase 3

### F5 · Smart Rename (스코프 인식 리네이밍)
- Rope 기반, 프로젝트 전역 안전 리네임.
- 미리보기 다이얼로그 (파일별 before/after).
- 주석/docstring 포함 옵션.

### F6 · Fuzzy Lookup (글로벌 심볼 팔레트)
- `Ctrl+P` 스타일 오버레이.
- rapidfuzz 기반 매칭 — CamelCase/snake_case 자동 경계.
- MRU 가중치, 심볼 타입 필터.

### F7 · Lookup References (역참조 리스트)
- DB 기반 정확한 참조 검색.
- 파일별 그룹화 + 2-3줄 컨텍스트 프리뷰.

### F8 · Layouts A/B/C/D
- 4개 레이아웃 프리셋 (Explore / Edit / Analyze / Custom).
- 단축키 `Ctrl+Alt+1..4`.

### F9 · Bookmarks+ (강화)
- 커스텀 이름/메모/태그.
- 북마크 세트 저장/로드 (JSON).

### F10 · Clip Window (다중 클립보드)
- 복사 히스토리 자동 누적(20개) + 고정 스니펫.
- Placeholder (`$date$`, `$filename$`, `$author$`).

---

## P3 · 완성도 기능 — Phase 3/5

### F11 · Search Project (멀티파일 고급 검색) — Phase 3
- Regex / keyword expression / Boolean / proximity.
- Search Results 독립 패널, 소스 링크 활성화.

### F12 · Overview Scroller (minimap) — Phase 5
- 스크롤바 옆 미니맵.
- 함수 경계 / 북마크 / 검색 매치 / 변경 라인 표시.

### F13 · Code Folding — Phase 5
- 함수/클래스/블록 접기.
- 세션 간 fold 상태 유지.

### F14 · Line Revision Marks — Phase 5
- 편집/추가/삭제 라인 마진 색상 표시.
- Git 독립적 세션 로컬 추적.

### F15 · Master File List (팀 공유) — Phase 5
- 프로젝트 설정 YAML export/import.
- Git에 체크인하여 팀원 공유.

---

## P4 · 옵션 기능 — Phase 5

### F16 · Custom Language Parser (확장성)
- Tree-sitter 기반 플러그인 API.
- 사용자가 새 언어 추가 가능.

### F17 · Graph Export
- PNG / SVG / DOT(Graphviz) 내보내기.

### F18 · Directory Compare
- 두 디렉터리 파일/심볼 수준 diff.

---

## P5 · Python 특화 차별화 — Phase 4

### F19 · Type Hint 기반 정밀도 향상
- `typing` 힌트 해석 (PEP 484/526/604).
- mypy/pyright 결과 흡수 옵션.
- **Unsolved → Solved 승격**: 타입 힌트가 있으면 회색 해치 제거.
- 노드에 타입 배지 추가 (`: str`, `: Optional[Session]`).

### F20 · Duck Typing 추정 뷰
- 정적 추론 실패 시 **후보 심볼들**을 opacity 50%로 표시.
- 사용자가 확정 가능한 경우 선택 UI 제공.

### F21 · Django/Flask/FastAPI ORM 관계 인식
- Django: `ForeignKey`, `ManyToManyField`, `OneToOneField`.
- SQLAlchemy: `relationship()`, `Mapped[...]`.
- Flask: `@app.route`, `@blueprint.route`.
- FastAPI: `@app.get/post`, `@router.*`.
- ORM 관계 = **녹색 점선 엣지** (새 타입).

### F22 · 가상환경 / Site-Packages 인식
- venv / poetry / pipenv / conda 자동 감지.
- site-packages 심볼은 별도 그룹, 흐린 색상.
- 필터 토글: "Project only" / "External" / "All".

### F23 · Jupyter Notebook 통합
- `.ipynb` 파싱 (nbformat), 셀 단위 심볼.
- IPython magic 무시.
- `.py` ↔ `.ipynb` 심볼 크로스 참조.

### F24 · Import Graph 뷰
- 모듈 간 import 의존성 전용 그래프.
- 순환 import 탐지 & 경고.
- `__all__` 기반 공개 API 경계 시각화.

### F25 · Decorator / Metaclass 추적
- `@property`, `@classmethod`, `@staticmethod` 배지.
- `@dataclass`, `@attrs`, Pydantic `BaseModel` 자동 필드 확장.

### F26 · Dynamic Import 탐지
- `importlib.import_module`, `__import__` 정적 탐지.
- 탐지된 dynamic import = **점선 회색 "dynamic" 엣지**.

### F27 · Shallow / Deep / Hybrid 인덱싱 모드
- **Shallow**: 이름 기반, 빠름, 낮은 정확도.
- **Deep**: Jedi 완전 분석, 느림, 높은 정확도.
- **Hybrid**: 기본 Shallow, 탐색된 서브트리만 Deep 재분석 (on-demand).
- GUI 토글 제공.

---

## 기능 ↔ Phase 매핑 다이어그램

```
Phase 1 │ ████████████████████  P0 전체 (이미지 재현)
Phase 2 │ ████████████████      F1 F2 F3 F4
Phase 3 │ ████████              F5 F6 F7 F8 F9 F10 F11
Phase 4 │ ██████████████████    F19 F20 F21 F22 F23 F24 F25 F26 F27
Phase 5 │ ██████████████        F12 F13 F14 F15 F16 F17 F18 + 패키징
```

---

## 비기능 요구사항

### 성능
| 지표 | 목표 |
|------|------|
| 1만 LoC 인덱싱 (Shallow) | < 1분 |
| 1만 LoC 인덱싱 (Deep) | < 3분 |
| 10만 LoC 인덱싱 (Shallow) | < 5분 |
| 그래프 첫 표시 | < 500ms |
| 심볼 선택 → Context 프리뷰 | < 200ms |
| Fuzzy Lookup 응답 | < 50ms (10만 심볼) |
| Search Project (Regex) | < 2초 (10만 LoC) |
| UI 프레임률 | 60fps (1천 노드 기준) |

### 메모리
- Idle: < 500MB
- 중규모 프로젝트: < 1GB
- 대형 프로젝트 (10만+ LoC): < 2GB

### 호환성
- **SourcetrailDB 100% 호환**: 생성한 DB를 원본 Sourcetrail Windows GUI에서 에러 없이 열람.
- Python 특화 확장 정보는 별도 확장 테이블 사용 (원본 스키마 미훼손).

### 품질
- 테스트 커버리지: **80% 이상**
- CI: Windows runner 상시 green
- 릴리스 전 샘플 프로젝트 5종 smoke test 통과

### 플랫폼
- Windows 10 (1809 이상) / Windows 11
- x64 아키텍처
- Python 3.12

---

## 의도적 제외 (비기능 목록)

**명시적으로 제외하는 항목** (요청 시 v1.1+로 이월 검토):

- macOS / Linux 네이티브 지원
- Language Server Protocol (LSP) 서버 모드
- 통합 디버거 (DAP)
- Git 네이티브 통합 (diff/blame은 외부 도구 사용)
- AI 자동완성 (LLM 연동)
- 웹 UI / SaaS 모드
- 실시간 협업 편집
- 컨테이너/WSL 원격 인덱싱
- Python 외 언어 기본 지원 (F16 Custom Language로 확장 가능)

---

## 요구사항 추적 매트릭스

각 기능의 검증 방법 (Phase별 DoD와 연결):

| 기능 | 수락 시나리오 | Phase |
|------|--------------|-------|
| P0 전체 | 첨부 이미지와 동일한 화면 구현 | 1 |
| F1 | 심볼 선택 0.2초 내 Context 프리뷰 | 2 |
| F2 | 10만 줄 파일 Symbol Window 1초 이내 | 2 |
| F3 | 다중 Relation Window + Lock 동작 | 2 |
| F4 | 스코프별 차등 색상 육안 확인 | 2 |
| F5 | Django 프로젝트 Rename 회귀율 < 1% | 3 |
| F6 | 10만 심볼에서 < 50ms | 3 |
| F7 | DB 쿼리 기반 정확도 100% | 3 |
| F8 | 4개 레이아웃 < 100ms 전환 | 3 |
| F19 | 타입 힌트로 unsolved 50% 감소 | 4 |
| F21 | Django 샘플 ORM 관계 시각화 성공 | 4 |
| F23 | Jupyter 셀 심볼이 그래프에 표시 | 4 |
| 전체 | 원본 Sourcetrail GUI 호환성 테스트 통과 | 지속 |
