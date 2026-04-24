# References — Architecture Rules

**Sourcetrail_Remake (Python)**의 강제 가능한 구조 규칙. 위반은 `scripts/structure-check.sh`가 PR을 깨야 한다.

> C++ legacy(`src/lib*/`, `src/app/`, `src/indexer/`, `src/external/`, `src/test/`)는 본 룰에서 **제외**된다 — 무수정 reference. 별도 §7에서 처리.

## 1. 레이어 / 의존 방향

```
Presentation (UI)            ──▶ Application
Application                  ──▶ Domain
Domain                       ──▶ (없음 — pure model)
Infrastructure               ──▶ Domain (인터페이스 의존만)
                                  Infrastructure는 Application/UI를 모름
```

매핑:

| 레이어 | 디렉터리 | 책임 |
|---|---|---|
| **Presentation (UI)** | `src/sourcetrail_remake/ui/` | QWidget, QGraphicsView, 다이얼로그, 패널, EventBus 구독 |
| **Application** | `src/sourcetrail_remake/{indexer,refactor,search}/service.py` 등 + `core/event_bus.py` | 백그라운드 태스크 (QThread), 도메인 오케스트레이션 |
| **Domain** | `src/sourcetrail_remake/core/{project,types}.py` + 향후 도메인 모델 | 순수 dataclass / Protocol — 외부 의존 0 |
| **Infrastructure** | `src/sourcetrail_remake/db/`, `indexer/{jedi_resolver,parso_walker,...}.py`, `refactor/rename.py`, `search/fuzzy.py` 외부 라이브러리 wrapper | SQLite, Jedi, Parso, Rope, rapidfuzz, watchdog 직접 사용 |

화살표는 **허용** 방향. 반대는 모두 **금지**.

## 2. 금지 의존성 (구체)

| 금지 | 이유 |
|---|---|
| `core/{project,types}.py`(Domain) → 그 외 모든 모듈 | Domain은 의존 0. 순환 위험 차단. |
| `core/{project,types}.py` → `PyQt6.*` / `jedi` / `parso` / `rope` / `sqlite3` | Domain은 프레임워크 무지. |
| `db/`, `indexer/`, `refactor/`, `search/`(Infrastructure) → `ui/` | 인프라가 UI를 모른다. |
| `db/`, `indexer/`, `refactor/`, `search/` → `cli/` | 동일. |
| `ui/` → `jedi` / `parso` / `rope` / `sqlite3` 직접 import | UI는 Application/Infrastructure를 통해서만. |
| `ui/<X>/` → `ui/<Y>/` 직접 (Y가 sibling 패널) | 패널 간 직접 통신 금지. `core/event_bus.py`만 경유. |
| `cli/` → `ui/` | CLI는 GUI 의존 금지. `srm-index`는 헤드리스. |
| 모든 모듈 → `print(...)` | 표준 출력 직접 사용 금지. `core.logging` (또는 stdlib `logging`) 사용. |
| 모든 모듈에서 `pip install` / `subprocess.run(["pip", ...])` | 의존성 설치는 `uv` 책임. 코드에서 패키지 설치 금지. |
| `indexer/frameworks/` 외에서 Django/Flask/FastAPI/SQLAlchemy import | 프레임워크 인지는 플러그인 경계로 격리 (`02-architecture.md` §8). |

## 3. 도메인 / 모듈 단위 분리

`src/sourcetrail_remake/`는 의도된 최상위 모듈만:

```
sourcetrail_remake/
├── __init__.py
├── __main__.py
├── cli/         (Application 레벨, 헤드리스 진입)
├── core/        (Domain + 공통: event_bus, types, config, project, environment)
├── db/          (Infrastructure: SourcetrailDB schema/writer/reader/extension/compat)
├── indexer/     (Application + Infrastructure: service + jedi/parso/type_hints/duck/...)
├── refactor/    (Application + Infrastructure: rename via rope)
├── search/      (Application + Infrastructure: service + fuzzy + references)
└── ui/          (Presentation: main_window, graph/, panels/, editor/, dialogs/, ...)
```

**새 최상위 모듈 추가 금지** (예: `src/sourcetrail_remake/utils/` 같은 dump 폴더). 책임이 뚜렷하지 않으면 기존 모듈에 들어가야 한다.

## 4. Cross-cutting concerns의 공식 유입 경로

| 관심사 | 공식 경로 |
|---|---|
| 로깅 | stdlib `logging` + `core.logging` 설정 (Phase 0에서 결정) |
| 이벤트 (패널 간 동기화) | `core/event_bus.py` (`pyqtSignal` only) |
| 설정 / 사용자 데이터 | `core/config.py` (→ `%APPDATA%/Sourcetrail_Remake/`) |
| 환경 감지 (venv/poetry/conda) | `core/environment.py` |
| DB 접근 | `db/reader.py` (UI 측) / `db/writer.py` (인덱서 측) — 다른 곳에서 `sqlite3` 직접 사용 금지 |
| Jedi 호출 | `indexer/jedi_resolver.py`만 |
| Rope 호출 | `refactor/rename.py`만 |

**우회 신호**: 모듈에서 위 항목을 직접 import하면 위반.

## 5. 위반 사례 5개와 수정

| # | 위반 | 수정 |
|---|---|---|
| 1 | `ui/panels/context.py`에서 `import jedi` | `core/event_bus.py`의 `symbol_selected` 시그널을 구독하고, 정의 조회는 `db/reader.py`의 함수를 호출. Jedi 자체는 `indexer/jedi_resolver.py`만. |
| 2 | `db/writer.py`에서 `from PyQt6.QtCore import QObject` | DB 레이어는 Qt 무지. `Worker`는 `indexer/service.py`(Application)에 두고 그쪽이 `QThread` 상속. |
| 3 | `core/types.py`에서 `from sourcetrail_remake.db.reader import ...` | Domain → Infrastructure 역방향. 타입은 `core`에서 정의하고 Infrastructure가 import. |
| 4 | `ui/panels/symbol.py`에서 `from sourcetrail_remake.ui.panels.context import ContextPanel` 후 `ContextPanel.refresh()` 직접 호출 | EventBus로 `symbol_selected.emit(node_id)`. ContextPanel이 자기 슬롯에서 처리. |
| 5 | `indexer/frameworks/django.py`에서 `from sourcetrail_remake.ui.dialogs.indexing_mode import IndexingMode` | 인덱서가 UI를 import 금지. enum이 필요하면 `core/types.py`로 승격. |

## 6. 자동 검사 (pseudo-code)

`scripts/structure-check.sh`가 강제 (구현은 묶음 3):

```bash
PYROOT="src/sourcetrail_remake"

# Domain 격리
grep -rEn '^(from|import)\s+(PyQt6|jedi|parso|rope|sqlite3)' \
  "$PYROOT/core/" 2>/dev/null \
  && fail "Domain (core/) must not import frameworks"

# Infrastructure → UI 금지
grep -rEn '^(from|import)\s+sourcetrail_remake\.ui' \
  "$PYROOT/db/" "$PYROOT/indexer/" "$PYROOT/refactor/" "$PYROOT/search/" 2>/dev/null \
  && fail "Infrastructure must not depend on UI"

# UI에서 외부 라이브러리 직접 사용 금지
grep -rEn '^(from|import)\s+(jedi|parso|rope|sqlite3)' \
  "$PYROOT/ui/" 2>/dev/null \
  && fail "UI must go through Infrastructure"

# CLI → UI 금지
grep -rEn '^(from|import)\s+sourcetrail_remake\.ui' \
  "$PYROOT/cli/" 2>/dev/null \
  && fail "CLI must not import UI"

# 패널 간 직접 import
grep -rEn '^(from|import)\s+sourcetrail_remake\.ui\.panels' \
  "$PYROOT/ui/panels/" 2>/dev/null \
  | grep -v 'panels/__init__' \
  && fail "panels must communicate via core.event_bus"

# print 직접 사용
grep -rEn '\bprint\(' "$PYROOT/" 2>/dev/null \
  | grep -v '^.*#.*allow-print' \
  && warn "use logging, not print (suppress with # allow-print)"

# pip subprocess
grep -rEn 'subprocess.*pip' "$PYROOT/" 2>/dev/null \
  && fail "do not call pip from code; use uv"

# 외부 프레임워크 import는 frameworks/ 하위만
grep -rEn '^(from|import)\s+(django|flask|fastapi|sqlalchemy)' \
  "$PYROOT/" 2>/dev/null \
  | grep -vE "$PYROOT/indexer/frameworks/" \
  && fail "framework imports allowed only in indexer/frameworks/"
```

## 7. C++ Legacy 영역

다음 경로는 **무수정 reference**. Python 구조 룰 대상 아님. 본 룰의 grep도 이 경로를 제외해야 한다.

```
CMakeLists.txt, cmake/, script/, .clang-format,
.travis.yml, appveyor.yml,
src/lib*/, src/app/, src/indexer/, src/external/, src/test/,
java_indexer/, ide_plugins/, deployment/, setup/, bin/, testing/,
docs/documentation/, docs/readme/,
README.md, DOCUMENTATION.md, CHANGELOG.md, CONTRIBUTING.md,
SPONSORS.md, AUTHORS.txt, LICENSE.txt
```

수정이 필요한 경우 `docs/sop/human-approval.md` 절차로만. 변경 PR은 `legacy-cpp-touch` 라벨 + 사유 기재 필수.

## 8. CI 실패 조건

`.github/workflows/harness-gate.yml`이 §6 위반 시 PR 머지 차단.
긴급 우회는 `docs/sop/human-approval.md`의 `RULE_OVERRIDE` 절차로만.

## 9. 향후 개선

- §6의 grep 기반 검사는 **Phase 1 종료 시** [`import-linter`](https://import-linter.readthedocs.io/) 또는 [`tach`](https://github.com/gauge-sh/tach)로 교체 검토. 이때 본 문서의 룰을 그 도구의 contract 형식으로 옮긴다.
- 새 layer/모듈 추가는 본 문서를 먼저 갱신하고 PR.
