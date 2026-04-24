# Phase 6 · 테스팅 & 문서화 (지속, 전 Phase 병행)

| 메타 | 값 |
|------|-----|
| 기간 | **지속 (Week 1-31 전체)** |
| 성격 | **횡단 Phase** — 다른 Phase 와 병행 |
| 목표 커버리지 | **80% 이상 (라인/브랜치/함수)** |
| 산출물 | 테스트 스위트, 문서 사이트, CI 파이프라인 |

---

## 목표

품질과 지속 가능성을 담보하는 **두 개의 기둥**:

1. **자동화된 테스트 스위트** — 단위/통합/E2E, 커버리지 80%+
2. **공개 문서 사이트** — 사용자 가이드, 개발자 가이드, API 레퍼런스

---

## 다루는 범위

### T1 — 단위 테스트 (pytest)
- 모든 public 함수/클래스 단위 테스트
- 목표: 라인/브랜치/함수 80%+

### T2 — 통합 테스트 (pytest + Qt)
- 컴포넌트 간 상호작용 (indexer → DB → UI)
- pytest-qt 로 위젯 테스트
- DB 호환성 회귀 (원본 Sourcetrail 열람 검증)

### T3 — E2E 테스트 (pytest-qt + subprocess)
- CLI 인덱싱 → GUI 실행 → 사용자 액션 시뮬레이션
- 주요 시나리오 (Phase DoD 기반)

### T4 — 성능 테스트 (pytest-benchmark)
- 인덱싱 속도
- 그래프 렌더링 fps
- Fuzzy lookup latency

### T5 — 스냅샷/회귀 테스트
- 그래프 렌더링 결과 PNG 비교
- DB 스키마 해시 검증 (호환성 유지)

### D1 — 사용자 문서 (MkDocs Material)
- 설치 가이드
- 빠른 시작 튜토리얼
- 기능별 가이드 (P0-P5)
- FAQ / 트러블슈팅

### D2 — 개발자 문서
- 아키텍처 개요 (docs/plan/02-architecture.md 링크)
- 기여 가이드 (`CONTRIBUTING.md`)
- 플러그인 개발 가이드 (F21 프레임워크 플러그인)
- 코드 스타일 (ruff, mypy 설정)

### D3 — API 레퍼런스
- `mkdocstrings` 자동 생성
- 주요 public API (IndexerService, DatabaseReader, EventBus)

### D4 — 릴리스 노트 / CHANGELOG
- Keep a Changelog 포맷
- 각 Phase 종료 시 업데이트

### C1 — CI/CD 파이프라인
- GitHub Actions: lint / test / coverage / build (매 PR)
- Nightly 벤치마크 (main 브랜치)
- Release workflow (Phase 5에서 구축)

---

## 산출물 (Deliverables)

| # | 산출물 | 위치 |
|---|--------|------|
| D6.1 | `tests/` 디렉터리 구조 | `tests/unit/`, `tests/integration/`, `tests/e2e/`, `tests/benchmark/` |
| D6.2 | pytest 설정 | `pyproject.toml` (tool.pytest.ini_options) |
| D6.3 | Coverage 설정 | `pyproject.toml` (tool.coverage) |
| D6.4 | Fixture (샘플 프로젝트) | `tests/fixtures/` (Django mini, Flask mini, Jupyter mini) |
| D6.5 | CI workflow | `.github/workflows/ci.yml` |
| D6.6 | Nightly benchmark workflow | `.github/workflows/nightly.yml` |
| D6.7 | MkDocs 사이트 | `docs/` (MkDocs Material) |
| D6.8 | `CONTRIBUTING.md` | 루트 |
| D6.9 | `CODE_OF_CONDUCT.md` | 루트 |
| D6.10 | `CHANGELOG.md` | 루트 |
| D6.11 | Issue/PR 템플릿 | `.github/ISSUE_TEMPLATE/`, `.github/pull_request_template.md` |
| D6.12 | 기여자 빌드 가이드 | `docs/dev/build.md` |

---

## Phase 병행 작업 계획

### Phase 0 (Week 1-2) 병행
- pytest 구조 세팅 (`tests/unit`, `tests/integration`)
- CI 워크플로우 (lint + test) 작동
- Coverage 리포트 업로드 (Codecov 또는 GitHub Artifact)
- MkDocs 골격 (홈, 설치 페이지만)

### Phase 1 (Week 3-8) 병행
- 인덱서 단위 테스트 (ParsoWalker, JediResolver, UnsolvedTracker)
- DB 호환성 회귀 테스트 (원본 Sourcetrail 샘플 DB와 비교)
- 그래프 렌더링 스냅샷 테스트 (결정적 레이아웃)
- 사용자 문서: 빠른 시작 튜토리얼 초안 (Alpha 단계)

### Phase 2 (Week 9-16) 병행
- 4개 패널 통합 테스트 (pytest-qt)
- E2E 시나리오 15가지 (MVP DoD)
- 사용자 문서: Context/Symbol/Relation/Syntax 가이드
- CHANGELOG: Alpha / Beta 엔트리

### Phase 3 (Week 17-22) 병행
- Rename 정확도 테스트 (샘플 100건 자동화)
- Fuzzy lookup 성능 벤치마크
- 사용자 문서: Rename / Layouts / Bookmarks / Clips 가이드
- CHANGELOG: RC1

### Phase 4 (Week 23-28) 병행
- Framework plugin 단위 테스트 (Django/Flask/FastAPI/SQLAlchemy)
- Hybrid 인덱싱 회귀 (대규모 프로젝트 샘플)
- 사용자 문서: Python 특화 기능 가이드
- 개발자 문서: 플러그인 작성 가이드
- CHANGELOG: RC2

### Phase 5 (Week 29-31) 병행
- 설치 관리자 E2E (Windows 샌드박스에서 설치/실행/삭제)
- 전체 회귀 스위트 100% pass 확인
- 사용자 문서 최종 정리 (스크린샷 갱신, 오타 수정)
- CHANGELOG: v1.0.0

---

## 테스트 전략 상세

### 단위 테스트 패턴

```python
# tests/unit/indexer/test_unsolved.py
from sourcetrail_remake.indexer.unsolved import UnsolvedSymbolTracker

def test_tracker_registers_empty_inference():
    tracker = UnsolvedSymbolTracker()
    tracker.register("foo.bar", context_file="x.py", line=10)
    assert tracker.count() == 1
    assert tracker.get("foo.bar").is_unsolved
```

### 통합 테스트 (pytest-qt)

```python
# tests/integration/ui/test_context_window.py
def test_context_window_updates_on_cursor_move(qtbot, main_window):
    editor = main_window.editor
    qtbot.mouseClick(editor, Qt.LeftButton)
    editor.setCursorPosition(10, 0)
    qtbot.waitUntil(lambda: main_window.context_window.current_symbol == "expected")
```

### E2E 테스트

```python
# tests/e2e/test_django_scenario.py
def test_django_indexing_and_graph(tmp_path):
    subprocess.run(['srm-index', 'fixtures/django_mini', '--db', tmp_path / 'out.srctrldb'], check=True)
    # GUI 실행은 pytest-qt 로 검증
```

### 성능 벤치마크

```python
# tests/benchmark/test_indexing_speed.py
def test_shallow_indexing_speed(benchmark, django_mini_project):
    benchmark(lambda: indexer.index(django_mini_project, mode='shallow'))
    # 결과를 nightly 리포트에 기록
```

### 스냅샷 테스트

```python
# tests/snapshot/test_graph_rendering.py
def test_session_graph_matches_snapshot(tmp_path):
    # 고정된 시드 + 결정적 레이아웃
    scene = load_session_graph()
    pixmap = scene.render_to_pixmap()
    assert pixmap_equals(pixmap, 'snapshots/session_graph.png', tolerance=0.01)
```

---

## 문서 사이트 구조

```
docs/
├── index.md                    # 홈 — "Python 전용 Sourcetrail + Source Insight"
├── getting-started/
│   ├── installation.md
│   ├── quick-start.md          # 5분 튜토리얼
│   └── first-project.md
├── user-guide/
│   ├── navigation.md           # 탭 / 히스토리 / 검색
│   ├── graph-view.md           # 그래프 뷰
│   ├── panels.md               # 4개 패널
│   ├── rename.md               # Smart Rename
│   ├── fuzzy-lookup.md
│   ├── layouts.md
│   ├── bookmarks.md
│   └── python-features.md      # Type hint, framework plugins, Hybrid
├── dev-guide/
│   ├── architecture.md         # 02-architecture 링크
│   ├── contributing.md
│   ├── build.md                # 소스 빌드
│   ├── plugins.md              # 프레임워크 플러그인 작성
│   └── testing.md
├── api/                        # mkdocstrings 자동 생성
├── faq.md
├── troubleshooting.md
└── changelog.md                # CHANGELOG.md 미러
```

---

## 품질 메트릭 (Phase 6 전체 DoD)

| 항목 | 목표 | Phase 종료 시점 |
|------|------|----------------|
| 테스트 커버리지 (라인) | ≥ 80% | Phase 5 종료 |
| 테스트 커버리지 (브랜치) | ≥ 75% | Phase 5 종료 |
| 테스트 커버리지 (함수) | ≥ 85% | Phase 5 종료 |
| CI 통과율 (main) | 100% | 지속 |
| 문서 페이지 | ≥ 40개 | Phase 5 종료 |
| API 레퍼런스 커버리지 | 100% (public API) | Phase 5 종료 |
| Nightly 벤치마크 회귀 | 0 | 지속 |
| Linter 경고 | 0 | 지속 |
| mypy strict 통과 | 100% | Phase 5 종료 |

---

## 테스트 Fixture 프로젝트

| Fixture | 크기 | 용도 |
|---------|------|------|
| `django_mini` | ~500 LoC | Django URL/View 통합 |
| `flask_mini` | ~300 LoC | Flask Blueprint |
| `fastapi_mini` | ~300 LoC | FastAPI Dependency |
| `sqlalchemy_mini` | ~200 LoC | SQLAlchemy Model |
| `jupyter_mini` | 3 notebooks | Jupyter 파싱 |
| `typed_mini` | ~500 LoC | 완전 타입 힌트 |
| `untyped_mini` | ~500 LoC | 힌트 없음, unsolved 많음 |
| `dynamic_mini` | ~200 LoC | 동적 import, getattr |

각 fixture 에 `expected_symbols.json` + `expected_edges.json` 동봉 → 회귀 스위트에서 비교.

---

## CI/CD 파이프라인

### PR 검증 (`.github/workflows/ci.yml`)

```yaml
name: CI
on: [pull_request, push]
jobs:
  test:
    runs-on: windows-latest  # Windows only
    steps:
      - checkout
      - setup uv
      - uv sync
      - ruff check
      - mypy src
      - pytest --cov --cov-report=xml
      - upload coverage to Codecov
  docs:
    runs-on: ubuntu-latest
    steps:
      - mkdocs build --strict
```

### Nightly (`.github/workflows/nightly.yml`)

```yaml
name: Nightly Benchmark
on:
  schedule: [cron: '0 18 * * *']  # 매일 03:00 KST
jobs:
  benchmark:
    runs-on: windows-latest
    steps:
      - pytest tests/benchmark --benchmark-json=out.json
      - compare with previous & report regressions
```

### Release (`.github/workflows/release.yml` — Phase 5에서 구축)

```yaml
name: Release
on:
  push:
    tags: ['v*']
jobs:
  build:
    runs-on: windows-latest
    steps:
      - pyinstaller srm.spec
      - innosetup compile installer.iss
      - gh release create --generate-notes --attach srm-*.exe
```

---

## Phase 6 리스크

| 리스크 | 등급 | 대응 |
|--------|------|------|
| pytest-qt GUI 테스트 플레이키 | 🟡 | 고정 프레임 폴링, `qtbot.waitUntil` 타임아웃 관대 |
| 커버리지 80% 미달 | 🟡 | 주간 체크, 60% → 70% → 80% 단계 목표 |
| 문서 분량 과다 | 🟢 | 최소 필수 40 페이지만 Phase 5에 완결 |
| 벤치마크 환경 변동 | 🟡 | 동일 러너 사용, 결과를 비율로 비교 |
| mypy strict 충돌 | 🟡 | 타입 stub 보완, Phase 1-4 끝마다 점검 |

---

## v1.0.0 문서 DoD

- [ ] 빠른 시작 튜토리얼 (5분)
- [ ] 27개 기능 모두 1개 이상의 문서 페이지
- [ ] API 레퍼런스 (mkdocstrings 자동 생성 + 수기 설명 50개)
- [ ] FAQ 최소 20개
- [ ] 트러블슈팅 가이드 (설치/실행/인덱싱 실패 사례)
- [ ] 스크린샷/GIF 최소 15개
- [ ] 기여 가이드 (빌드/테스트/PR 흐름)
- [ ] 플러그인 작성 가이드 (F21 기반)
- [ ] CHANGELOG 완성
- [ ] 라이선스 (GPL v3) + 크레딧 페이지

---

## 회고 (v1.0.0 출시 후)

**테스트 현황**:
- 라인 커버리지: ?%
- 브랜치 커버리지: ?%
- 총 테스트 수: ?개
- 플레이키 테스트 수: ?개

**문서 현황**:
- 총 페이지 수: ?개
- 누적 PV (GitHub Pages): ?
- 외부 기여 문서 PR: ?건

**CI/CD 현황**:
- 평균 CI 실행 시간: ?분
- Nightly 회귀 감지 횟수: ?회
- 릴리스 자동화 실패 횟수: ?회

**개선 제안 (v1.1)**:
-
