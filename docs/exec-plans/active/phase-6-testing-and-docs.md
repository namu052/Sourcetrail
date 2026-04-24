# Phase 6 — 테스트 & 문서 (전 기간 지속)

| 메타 | 값 |
|------|-----|
| 기간 | **전체 31주 (Phase 0 ~ Phase 5와 병행)** |
| 누적 | 지속적 |
| 상태 | 📋 계획됨 (매 Phase와 함께 진행) |
| 마일스톤 | 매 Phase DoD의 품질 게이트 역할 |

## 목표

각 Phase가 완료될 때 **품질 게이트**를 통과하도록 테스트·문서·성능 벤치마크를 **전 기간 병행**하여 관리한다.

**원칙**:
- 테스트는 기능 구현과 동시에 작성 (TDD 권장)
- 문서는 코드보다 뒤처지지 않게
- 성능 벤치마크는 매 Phase 종료 시 실행

## 전 기간 지속 작업

### 1. 테스트

#### 단위 테스트 (pytest)
- **커버리지 목표**: **80% 이상** 유지
- **실행**: `pytest --cov=sourcetrail_remake --cov-report=html`
- **CI 게이트**: 80% 미만이면 PR 블록
- **대상**: 순수 로직 (indexer, db, search, refactor, core)

#### UI 테스트 (pytest-qt)
- **대상**: 패널별 상호작용, 이벤트 버스, 키보드 단축키
- **스냅샷 테스트**: 그래프 렌더링 결과 PNG diff (tolerance 허용)
- **실행**: `pytest tests/ui/`

#### 통합 테스트 (End-to-end)
- **샘플 프로젝트 5종**:
  1. `requests` — 순수 Python 라이브러리 (중소 규모)
  2. `flask` — 마이크로 프레임워크
  3. `django` — 대규모 프레임워크 (ORM 테스트)
  4. `fastapi` — 모던 async 프레임워크
  5. 자기 자신 (`sourcetrail_remake`) — dogfooding
- **시나리오**: 인덱싱 → 심볼 점프 → Rename → Search → 호환성 확인

#### 회귀 테스트 — **SourcetrailDB 호환성**
- 매 릴리스 전 필수
- 샘플 프로젝트 인덱싱 → 원본 Sourcetrail Windows GUI로 열람
- 깨지거나 에러 나면 릴리스 차단

#### 성능 벤치마크
- **매 Phase 종료 시 실행**: `scripts/bench.py`
- 기록된 지표:
  - 1만 / 10만 LoC 인덱싱 시간 (Shallow / Deep)
  - 그래프 첫 표시 시간
  - Fuzzy Lookup 응답 시간
  - 메모리 사용량 (RSS peak)

### 2. 문서

#### Phase별 설계 문서

| Phase | 생성될 문서 |
|-------|------------|
| 0 | `DEVELOPMENT.md`, `ARCHITECTURE.md`, `db-schema.md` |
| 1 | `indexer-design.md`, `graph-renderer.md`, `phase-1-wbs.md` |
| 2 | `panels.md`, `editor-integration.md`, `event-bus.md` |
| 3 | `refactoring.md`, `search-engine.md`, `keyboard-shortcuts.md` |
| 4 | `python-specific.md`, `framework-plugins.md`, `compatibility-strategy.md` |
| 5 | `user-manual/` (최종), `release-notes-v1.0.md`, `packaging.md` |
| 전 기간 | `CONTRIBUTING.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md` |

#### API 레퍼런스
- **도구**: Sphinx + sphinx-rtd-theme
- **생성**: `scripts/build_docs.ps1`
- **대상**: public API (CLI, 플러그인 인터페이스, SourcetrailDB writer)
- **호스팅**: GitHub Pages (v1.0.0 이후)

#### 사용자 매뉴얼 (최종본 — Phase 5에 완성)
```
docs/user-manual/
├── 01-getting-started.md
├── 02-project-setup.md
├── 03-graph-view.md
├── 04-panels/
│   ├── context-window.md
│   ├── symbol-window.md
│   ├── relation-window.md
│   └── search-results.md
├── 05-editor.md
├── 06-refactoring.md
├── 07-keyboard-shortcuts.md
├── 08-customization.md
├── 09-troubleshooting.md
└── 10-faq.md
```

### 3. 릴리스 전략

| 릴리스 | 시점 | 대상 | 비고 |
|--------|------|------|------|
| **Alpha** | Week 8 종료 (Phase 1 완료) | 내부 | 이미지 재현 확인용 |
| **Beta** | Week 16 종료 (Phase 2 MVP 완료) | 공개 (GitHub Release) | 얼리어답터 피드백 |
| **RC 1** | Week 24 종료 (Phase 4 중간) | 공개 | Django/Jupyter 테스트 |
| **RC 2** | Week 28 종료 (Phase 4 완료) | 공개 | 기능 동결 |
| **v1.0.0** | Week 31 종료 (Phase 5 완료) | 공개 정식 | 인스톨러 배포 |

### 4. CI/CD 파이프라인

```yaml
# .github/workflows/ci.yml (핵심 구조)
on: [push, pull_request]
jobs:
  lint:
    runs-on: windows-latest
    steps:
      - run: uv run ruff check
      - run: uv run ruff format --check
      - run: uv run mypy src/

  test:
    runs-on: windows-latest
    steps:
      - run: uv run pytest --cov --cov-fail-under=80

  compatibility:
    runs-on: windows-latest
    if: github.event_name == 'pull_request'
    steps:
      - run: python scripts/compatibility_check.py

  benchmark:
    runs-on: windows-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - run: python scripts/bench.py --report
      - uses: actions/upload-artifact@v4
```

### 5. 주간/Phase 종료 체크리스트

**매주 금요일**
- [ ] 커버리지 확인
- [ ] 성능 회귀 없는지 스모크 벤치
- [ ] CHANGELOG.md 업데이트
- [ ] 다음 주 TODO 정리

**매 Phase 종료**
- [ ] 모든 DoD 항목 체크
- [ ] 성능 벤치마크 실행 및 기록 (`docs/benchmarks/phase-N.md`)
- [ ] Phase 회고 작성 (계획 문서의 "회고" 섹션)
- [ ] Phase 계획 문서를 `completed/`로 이동
- [ ] 다음 Phase 시작 킥오프 (새 주간 WBS)

### 6. 품질 지표 대시보드

```
┌─────────────────────────────────────────────┐
│ Sourcetrail_Remake — Quality Dashboard      │
├─────────────────────────────────────────────┤
│ Test Coverage:    85%   ✓ (목표 80%)        │
│ MyPy Errors:      0     ✓                   │
│ Ruff Violations:  0     ✓                   │
│ Sourcetrail Compat: ✓ Passing               │
│                                             │
│ Benchmarks (latest):                        │
│   10K LoC index (Shallow): 35s  ✓          │
│   10K LoC index (Deep):    2m10s ✓         │
│   Graph first paint:       420ms ✓         │
│   Fuzzy lookup:            38ms  ✓         │
│                                             │
│ Open Issues:      12                        │
│ Open PRs:         2                         │
└─────────────────────────────────────────────┘
```

## Phase 6 DoD (전 기간 유지)

- [ ] 모든 Phase 종료 시 커버리지 80% 이상
- [ ] CI가 항상 green
- [ ] 설계 문서가 구현과 동기화됨 (매 Phase 종료 시 업데이트)
- [ ] SourcetrailDB 호환성 회귀 테스트 전 릴리스 통과
- [ ] 사용자 매뉴얼 Phase 5 종료 시 완성
- [ ] API 레퍼런스 v1.0.0 태그 시 자동 생성되어 호스팅됨
- [ ] Alpha / Beta / RC / v1.0.0 모두 예정 주차에 릴리스됨

## 위험 & 완화

| 위험 | 대응 |
|------|------|
| 기능 개발에 치여 테스트 작성 미루기 | CI 게이트가 80% 미만 시 PR 블록 (강제) |
| 문서가 구현과 괴리 | 매 Phase 종료 체크리스트에 문서 업데이트 포함 |
| 성능 회귀 감지 늦음 | 매주 금요일 스모크 벤치 자동화 |
| Sourcetrail GUI 버전 차이로 호환성 테스트 흔들림 | 특정 버전 (4.0.x) 고정, CI runner에 설치 |
| 매뉴얼 작성 번아웃 | Phase 4 Week 28부터 병행 시작, Phase 5에 마감 |
| 혼자 리뷰 — 사각지대 가능 | 주간 셀프 리뷰 체크리스트, 자동화 최대한 |

## 참고 — 테스트 디렉터리 구조

```
tests/
├── unit/
│   ├── indexer/
│   ├── db/
│   ├── search/
│   ├── refactor/
│   └── core/
├── integration/
│   ├── test_requests_project.py
│   ├── test_flask_project.py
│   ├── test_django_project.py
│   ├── test_fastapi_project.py
│   └── test_self_hosting.py
├── ui/
│   ├── test_graph_view.py
│   ├── test_context_window.py
│   ├── test_symbol_window.py
│   └── test_editor.py
├── compatibility/
│   └── test_sourcetraildb_compat.py
├── performance/
│   └── bench_suite.py
└── fixtures/
    ├── sample_projects/
    └── golden_outputs/
```
