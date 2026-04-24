# Repository Guidelines

## Harness Entry (Codex CLI 어댑터)

이 파일은 **공용 하네스의 Codex 진입 허브**다. 본 리포에서 작업 대상은 **Sourcetrail_Remake (Python 데스크톱 앱, PyQt6+QScintilla, Windows 전용, 31주)**. 기존 C++ Sourcetrail은 **읽기 전용 reference**. 정책·절차 본문은 `docs/`에 있고 여기엔 짧은 진입만.

### 먼저 읽을 순서 (우선순위)

1. [`docs/README.md`](docs/README.md) — 트리 인덱스 + 우선순위.
2. [`docs/plan/00-overview.md`](docs/plan/00-overview.md) — 31주 대관 계획 + 8개 확정 사항 + 마일스톤 M0–M5.
3. [`docs/plan/01-requirements.md`](docs/plan/01-requirements.md) — 27개 기능(F1–F27) 명세, P0–P5.
4. [`docs/plan/02-architecture.md`](docs/plan/02-architecture.md) — 모듈 구조 + SourcetrailDB 100% 호환 전략 (extension table).
5. [`docs/plan/03-risks.md`](docs/plan/03-risks.md) — R-01–R-19 + 리스크 게이트 G1–G6.
6. [`docs/sop/codex.md`](docs/sop/codex.md) — Codex 표준 절차 (Python 도구 기준).
7. [`docs/references/build-and-test.md`](docs/references/build-and-test.md) — uv/pytest/ruff/mypy 단일 진실 원천.
8. [`docs/references/architecture-rules.md`](docs/references/architecture-rules.md) — UI→App→Domain→Infrastructure + C++ legacy 영역 격리.
9. [`docs/golden-rules.md`](docs/golden-rules.md) — 절대 위반 금지 (특히 G7 = C++ legacy 보호, G13 = uv only, G14 = SourcetrailDB 호환).

### Phase 작업 시 추가 진입 문서

| 현재 Phase | 문서 | 기간 | 마일스톤 |
|----|------|------|----------|
| Phase 0 | [`docs/plan/phase-0-setup.md`](docs/plan/phase-0-setup.md) | 2주 (W1–2) | M0 Foundation / 게이트 G1 |
| Phase 1 | [`docs/plan/phase-1-mvp-indexer-graph.md`](docs/plan/phase-1-mvp-indexer-graph.md) | 6주 (W3–8) | M1 Image Parity / Alpha / G2 |
| Phase 2 | [`docs/plan/phase-2-context-panels.md`](docs/plan/phase-2-context-panels.md) | 8주 (W9–16) | M2 MVP / Beta / G3 |
| Phase 3 | [`docs/plan/phase-3-editor-features.md`](docs/plan/phase-3-editor-features.md) | 6주 (W17–22) | M3 Productivity / RC1 / G4 |
| Phase 4 | [`docs/plan/phase-4-python-specific.md`](docs/plan/phase-4-python-specific.md) | 6주 (W23–28) | M4 Differentiation / RC2 / G5 |
| Phase 5 | [`docs/plan/phase-5-packaging.md`](docs/plan/phase-5-packaging.md) | 3주 (W29–31) | M5 v1.0.0 / G6 |
| 횡단 | [`docs/plan/phase-6-testing-docs.md`](docs/plan/phase-6-testing-docs.md) | 지속 | 커버리지 80%+ |

**작업 규칙**:
- 각 Phase 문서의 "산출물(Deliverables)" 표에 명시된 경로 그대로 파일 생성.
- "주요 클래스 계약" 섹션의 시그니처 준수.
- Day(D번호) 단위로 커밋. 커밋 메시지: `<module>: <title>` (예: `indexer: add JediResolver skeleton (D13)`).
- Phase 종료 시 해당 문서의 DoD 체크리스트 + 회고 섹션 채움.
- Phase 완료 후 반드시 리스크 게이트(G1–G6) 검증 후 다음 Phase 진입.

### 확정 사항 요약 (변경 금지)

| # | 항목 | 값 |
|---|------|-----|
| 1 | 라이선스 | GPL v3 |
| 2 | 에디터 위젯 | QScintilla (PyQt6 바인딩) |
| 3 | MVP 범위 | Phase 0–2 (16주) |
| 4 | 타겟 플랫폼 | Windows 전용 |
| 5 | 개발 체계 | 1인 풀타임 |
| 6 | SourcetrailDB | 100% 호환 (원본 GUI 열람 가능) |
| 7 | 레포명 | `Sourcetrail_Remake` 유지 |
| 8 | 기능 범위 | F1–F27 전체 포함, 제외 없음 |

### 검증 & PR

- 환경 무관 게이트: `bash scripts/verify-all.sh` — lint(ruff) + type-check(mypy strict) + structure-check + docs-freshness + check-adapter-sync.
- 테스트: `bash scripts/run-tests.sh -m <unit|integration|ui|compatibility|performance>` (= `uv run pytest`).
- DB/스키마 영향 변경 시: `bash scripts/compat-check.sh tests/fixtures/<sample>/` (G14).
- 성능 회귀 추적: `bash scripts/bench.sh` (Phase 1+).
- PR 전: [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md) 체크리스트.
- 권한/샌드박스/위험 명령: [`.codex/config.toml`](.codex/config.toml) (+ [`.codex/README.md`](.codex/README.md)).

> 이 섹션 아래의 **Repository Guidelines**는 원본 C++ Sourcetrail의 기여자 가이드이며, **C++ legacy reference로만** 보존된다. Python 작업은 위 `docs/` 링크가 우선.

---

## Project Structure & Module Organization
`src/` contains the main CMake targets split by responsibility: `app/` for the desktop entry point, `lib/` and `lib_utility/` for shared logic, `lib_gui/` for Qt UI, `lib_cxx/`, `lib_java/`, and `lib_python/` for language packages, `indexer/` for indexing executables, `external/` for vendored dependencies, and `test/` for Catch2 suites. `java_indexer/` holds the Maven-based Java indexer under `src/main/java/com/sourcetrail`. Use `testing/` for UI/manual regression fixtures, `bin/app/data` for runtime assets, `deployment/` for packaging, and `ide_plugins/` for editor integrations.

## Build, Test, and Development Commands
Use out-of-source builds only; the top-level `CMakeLists.txt` rejects in-source builds.

- `cmake -S . -B build/Release -G Ninja -DCMAKE_BUILD_TYPE=Release ...` configures a release build.
- `cmake --build build/Release --target Sourcetrail` builds the app.
- `cmake --build build/Release --target Sourcetrail_test` builds the automated test binary.
- `cd bin/test && ../../build/Release/test/Sourcetrail_test` runs the Catch2 suite with the expected working directory.
- `bash script/build.sh release` is the repo wrapper to configure, build, and run the app.
- `bash script/build.sh release test` builds and runs tests in one step.

Enable language packages explicitly during configure when needed, for example `-DBUILD_CXX_LANGUAGE_PACKAGE=ON -DBUILD_JAVA_LANGUAGE_PACKAGE=ON -DBUILD_PYTHON_LANGUAGE_PACKAGE=ON`.

## Coding Style & Naming Conventions
Follow `.clang-format`: tabs with width 4, Allman braces, 100-column limit, left-aligned pointers, and C++17. Match existing naming patterns: classes and implementation files use PascalCase such as `ConfigManager.cpp` or `QtMainWindow.cpp`; tests use `*TestSuite.cpp`. Keep new code in the module that matches its responsibility instead of adding cross-module shortcuts.

## Testing Guidelines
Tests live in `src/test` and are registered in `src/test/CMakeLists.txt`. Extend the nearest existing suite before creating a new one. For bug fixes and features, add a regression test and reuse fixtures from `testing/` when the issue is UI- or project-setup-related.

## Commit & Pull Request Guidelines
Use the shipped commit template style: `<module>: <title>`, for example `ui: fix tab focus restore` or `test: add Java parser regression`. History shows short scope prefixes such as `docs:`, `src:`, and `res:`. Run `bash script/setup_git_hooks.sh` once to install the commit template and hooks. For pull requests, describe the problem, summarize the fix, list validation steps, link the related issue, include screenshots for UI changes, add your name to `AUTHORS.txt`, and avoid committing directly to `master`.
