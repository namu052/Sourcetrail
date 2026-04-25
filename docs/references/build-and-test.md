# References — Build & Test (단일 진실 원천)

이 문서는 **Sourcetrail_Remake (Python)** 의 빌드·테스트 SoT다.
`AGENTS.md` / `CLAUDE.md` / `docs/sop/*` / 검증 스크립트는 모두 이 파일을 가리킨다. 중복 금지, 변경은 여기서만.

> **C++ legacy 자산** (`src/lib*/`, `CMakeLists.txt`, `script/`, `.travis.yml`, `appveyor.yml`)은 **읽기 전용 reference**로 보존된다. 빌드 대상이 아니다. 마지막 §6에 별도 정리.

## 1. 환경 요구

| 항목 | 버전 / 비고 |
|---|---|
| OS | Windows 10 (1809+) / Windows 11, x64 |
| Python | **3.12** 고정 (`pyproject.toml` `requires-python = ">=3.12,<3.13"`) |
| 의존성 매니저 | **uv** (https://docs.astral.sh/uv/) |
| UI | PyQt6 ≥ 6.7, PyQt6-QScintilla ≥ 2.14 |
| 분석 | jedi ≥ 0.19.1 (<0.20), parso ≥ 0.8.4, rope ≥ 1.13 |
| 확장 파서 | tree-sitter ≥ 0.23, tree-sitter-python ≥ 0.23 |
| 유틸 | rapidfuzz ≥ 3.9, PyYAML ≥ 6, nbformat ≥ 5.10, watchdog ≥ 4 |
| 린터/포매터 | ruff ≥ 0.6 |
| 타입 체커 | mypy ≥ 1.11 (strict 모드) |
| 테스트 | pytest ≥ 8, pytest-qt ≥ 4.4, pytest-cov ≥ 5 |
| 패키징 | PyInstaller, Inno Setup |
| 문서 | Sphinx ≥ 7 |

## 2. 설치 / 부트스트랩

```bash
# 1. uv 설치 (한 번만)
pip install uv
# 또는: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. 가상환경 + 의존성 동기화
uv sync --all-extras

# 3. 진입점 확인
uv run python -m sourcetrail_remake          # GUI
uv run srm-index <project-path>              # 인덱싱 CLI
uv run srm-gui                               # GUI CLI
```

> 지금은 `pyproject.toml`이 아직 없다 — Phase 0 D1에 생성. 그 전엔 `uv sync`가 실패할 수 있음. 본 문서는 Phase 0 종료 시점의 상태를 가정.

## 3. 테스트

### 3.1 진입

모든 테스트는 `tests/` 아래. 작업 디렉터리는 **리포 루트** (Catch2처럼 별도 디렉터리 강제 없음).

```bash
bash scripts/run-tests.sh                     # 전체
bash scripts/run-tests.sh -m unit             # unit 마커만
bash scripts/run-tests.sh -m integration
bash scripts/run-tests.sh -m ui               # pytest-qt
bash scripts/run-tests.sh -m compatibility    # SourcetrailDB 호환
bash scripts/run-tests.sh -m performance      # 벤치
bash scripts/run-tests.sh -k test_indexer     # 이름 prefix
bash scripts/run-tests.sh tests/unit/test_db.py::test_writer_smoke   # 단일 함수
```

내부적으로는 `uv run pytest`. 마커는 `pyproject.toml`의 `[tool.pytest.ini_options]`에 등록.

### 3.2 디렉터리 규약

```
tests/
├── unit/           # 단일 클래스/함수 (mock OK)
├── integration/    # DB writer↔reader, indexer 파이프라인
├── ui/             # pytest-qt, qtbot 사용
├── compatibility/  # SourcetrailDB 원본 GUI 호환 검증 (.srctrldb 생성/로드)
├── performance/    # pytest-benchmark
└── fixtures/       # 샘플 .py / .ipynb / 미니 Django 프로젝트
```

### 3.3 커버리지

`pyproject.toml`의 `[tool.pytest.ini_options]`:

```toml
addopts = "--strict-markers --cov=sourcetrail_remake --cov-report=term-missing"
```

게이트 (Phase 1+):

| 영역 | 임계 |
|---|---|
| 전체 라인 | 80% |
| 변경 라인 | 80% (PR diff 기준) |
| `sourcetrail_remake.db` | 90% (호환성 핵심) |
| `sourcetrail_remake.indexer` | 85% |

CI에서 `pytest --cov-fail-under=80` 강제.

### 3.4 새 테스트 추가

- 위치: 가까운 `tests/<area>/test_<name>.py` (snake_case).
- 마커 필수: 적어도 하나 — `unit` / `integration` / `ui` / `compatibility` / `performance`.
- pytest-qt: GUI 테스트는 `qtbot` fixture 사용, `qWait` 대신 `waitUntil`.

## 4. 린트 / 타입 체크

```bash
bash scripts/lint.sh         # ruff check + ruff format --check (변경 파일 한정)
bash scripts/type-check.sh   # mypy strict (전체 src/, --strict)
```

직접 호출:

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/
```

`pyproject.toml`:

```toml
[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
# select / ignore는 Phase 0에서 결정. 시작은 default + E/F/I/B/UP.

[tool.mypy]
python_version = "3.12"
strict = true
```

## 5. 공용 검증 진입점

```bash
bash scripts/verify-all.sh
# 순차: lint → type-check → structure-check → docs-freshness → check-adapter-sync
# (compat-check, bench는 별도 호출)
```

빌드/테스트는 환경 의존성이 크지 않지만 `uv sync` 선행 필요. 게이트 자체는 환경 무관 검사로 한정.

## 6. CI

| 시스템 | 책임 | 트리거 |
|---|---|---|
| `.github/workflows/harness-gate.yml` | lint / type / structure / docs / adapter-sync | PR |
| `.github/workflows/ci.yml` | uv sync + pytest (Phase 0 D2에 생성) | push, PR |
| (legacy) `.travis.yml`, `appveyor.yml` | C++ Sourcetrail 빌드 | tag (legacy) |

신규 워크플로는 Windows runner (`runs-on: windows-latest`)로 통일. Linux/macOS는 타겟 아님 (Windows 전용 결정).

## 7. (Legacy) C++ Sourcetrail

기존 C++ Sourcetrail은 **읽기 전용 reference**로 유지. 본 프로젝트는 빌드/테스트하지 않는다.

| 항목 | 위치 | 비고 |
|---|---|---|
| 빌드 시스템 | `CMakeLists.txt`, `cmake/`, `script/` | 무수정 |
| 소스 | `src/lib*/`, `src/app/`, `src/indexer/`, `src/external/`, `src/test/` | 무수정 |
| CI | `.travis.yml`, `appveyor.yml` | 무수정 |
| 문서 | `README.md`, `DOCUMENTATION.md`, `CHANGELOG.md` | 무수정 |
| 스타일 | `.clang-format` | C++ legacy 한정 |

수정이 필요한 경우: `docs/sop/human-approval.md` 절차에 따라 maintainer 승인. 기본은 "왜 legacy를 건드는가"를 plan에 명시해야 한다.

## 8. 자주 빠지는 함정

- `pip install`로 의존성 추가 → 락파일 깨짐. 항상 `uv add <pkg>` 사용.
- `uv.lock` 미커밋 → CI 재현 불가. 수정 시 항상 같이 커밋.
- pytest를 직접 호출 (`pytest` 단독) → 가상환경 밖. 항상 `uv run pytest` 또는 `bash scripts/run-tests.sh`.
- `mypy --strict`를 선택적으로 끔 → Golden Rule G1 위반.
- C++ legacy 영역에 Python 룰 적용해서 false positive로 PR 차단 → `structure-check.sh`가 legacy를 제외해야 정상.
