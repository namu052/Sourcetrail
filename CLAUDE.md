# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Harness Entry (Claude Code 어댑터)

이 파일은 **공용 하네스의 Claude 진입 허브**다. 본 리포에서 작업 대상은 **Sourcetrail_Remake (Python 데스크톱 앱, PyQt6+QScintilla, Windows 전용, 31주)**. 기존 C++ Sourcetrail은 **읽기 전용 reference**. 정책·절차 본문은 `docs/`에 있고 여기엔 짧은 진입만.

먼저 읽을 순서:
1. [`docs/README.md`](docs/README.md) — 트리 인덱스 + 우선순위.
2. [`docs/plan/00-overview.md`](docs/plan/00-overview.md) — 31주 대관 계획 + 8개 확정 사항.
3. [`docs/sop/claude.md`](docs/sop/claude.md) — Claude 표준 절차 (Python 도구 기준).
4. [`docs/references/build-and-test.md`](docs/references/build-and-test.md) — uv/pytest/ruff/mypy **단일 진실 원천**. 아래 §Build/§Tests는 C++ legacy 빠른 참조이며, **Python 작업은 본 링크 우선**.
5. [`docs/references/architecture-rules.md`](docs/references/architecture-rules.md) — UI→App→Domain→Infrastructure + C++ legacy 격리.
6. [`docs/golden-rules.md`](docs/golden-rules.md) — 절대 위반 금지 (G7 C++ legacy 보호, G13 uv only, G14 SourcetrailDB 호환).

스킬: [`.claude/skills/explore-codebase`](.claude/skills/explore-codebase/SKILL.md), [`create-exec-plan`](.claude/skills/create-exec-plan/SKILL.md), [`run-verification`](.claude/skills/run-verification/SKILL.md), [`prepare-pr`](.claude/skills/prepare-pr/SKILL.md).
검증: `bash scripts/verify-all.sh`. PR 전: [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md).
훅 초안: [`.claude/hooks/README.md`](.claude/hooks/README.md) — 적용은 사용자 승인 후.

---

## Project

Sourcetrail is an archived (2021) cross-platform C++/Qt source explorer that indexes C, C++, Java, and Python codebases into a SQLite database and renders an interactive code map. The desktop app drives one or more out-of-process indexer executables that share work via interprocess message queues; the GUI then queries the persisted graph through a `StorageAccess` facade.

## Build

Out-of-source builds only — the top-level `CMakeLists.txt` aborts an in-source configure. Language packages are **off by default**; opt in per language at configure time.

Repo wrappers (Bash, work on Windows via Git Bash):
- `bash script/build.sh release` — configure (first run), build, then launch `Sourcetrail`.
- `bash script/build.sh release test` — build and run the Catch2 test binary.
- `bash script/build.sh debug [test]` — same against the Debug build.
- `bash script/buildonly.sh <release|debug> [test]` — build without launching.
- `bash script/clean.sh` — wipe `build/`.

The wrappers configure both `build/Debug` and `build/Release` with `-G Ninja` and **all three language packages enabled** (`BUILD_CXX_LANGUAGE_PACKAGE`, `BUILD_JAVA_LANGUAGE_PACKAGE`, `BUILD_PYTHON_LANGUAGE_PACKAGE`) plus `DOCKER_BUILD=ON`. For a leaner local build, configure manually:

```
cmake -S . -B build/Release -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DBOOST_ROOT=<path> -DQt5_DIR=<path>/lib/cmake/Qt5 \
  [-DClang_DIR=<llvm_build>/lib/cmake/clang -DBUILD_CXX_LANGUAGE_PACKAGE=ON] \
  [-DBUILD_JAVA_LANGUAGE_PACKAGE=ON] [-DBUILD_PYTHON_LANGUAGE_PACKAGE=ON]
cmake --build build/Release --target Sourcetrail        # app
cmake --build build/Release --target Sourcetrail_test   # tests
```

Hard dependency floors: CMake 3.12+, Boost 1.67 (`filesystem program_options system date_time`), Qt 5.12.3, C++17. C/C++ indexing also needs LLVM/Clang **11.0.0 exactly** built with `-DLLVM_ENABLE_RTTI=ON`. Java indexing needs JDK 1.8 with `JAVA_HOME` set, plus Maven (`M2_HOME`/`MAVEN_HOME`) for the Java tests. `TREAT_WARNINGS_AS_ERRORS=ON` is the default — broken builds may just be a new warning.

## Tests

- Framework: [Catch2](https://github.com/catchorg/Catch2). Sources live in `src/test/*TestSuite.cpp` and are registered in `src/test/CMakeLists.txt`.
- The test binary **must** be run from `bin/test/` (it resolves fixtures with relative paths):
  ```
  cd bin/test && ../../build/Release/test/Sourcetrail_test
  ```
- Run a single suite/test with Catch2 selectors:
  ```
  ../../build/Release/test/Sourcetrail_test "[ConfigManager]"
  ../../build/Release/test/Sourcetrail_test "ConfigManagerTestSuite: ..."
  ```
- Some suites (`JavaIndexSampleProjectsTestSuite`, `JavaParserTestSuite`, `UtilityMavenTestSuite`, `PythonIndexerTestSuite`, `CxxParserTestSuite`) only run when the matching language package is enabled at configure time.
- For UI/project-setup regressions, reuse fixtures under `testing/` rather than building new ones; for everything else, extend the nearest existing suite before adding a new file.

## Architecture

The app is split into independently linkable static libraries that fan out from a small `app/` shell. Cross-module shortcuts (e.g. GUI reaching into `lib_cxx`) are intentionally avoided — extend the right module instead.

### Process layout
- `src/app/` (`Sourcetrail`) — Qt entry point that owns the UI and orchestrates indexing.
- `src/indexer/` (`Sourcetrail_indexer`) — headless worker spawned per indexing job. The app and indexer talk over Boost.Interprocess shared-memory message queues (`src/lib/utility/interprocess/`, `src/lib/utility/messaging/`). Indexers stream `IntermediateStorage` chunks back; the app merges them into the SQLite `PersistentStorage`.

### Library layering (`src/lib*/CMakeLists.txt`)
- `lib_utility/` — leaf-level helpers (logging, file paths, strings, math). No deps on other Sourcetrail libs.
- `lib/` — the engine. Sub-areas:
  - `data/` — domain model and persistence: `graph/` (Node/Edge/Token), `parser/` (`ParserClient` interface implemented by language packages), `storage/` (`Storage` → `PersistentStorage` → `sqlite/` via the migration chain in `storage/migration/`), `search/`, `name/`, `location/`, `bookmark/`, `indexer/` (`IndexerCommand` queue), `tooltip/`.
  - `project/` — `Project`, `SourceGroup`, `RefreshInfoGenerator` decide *what* to (re)index.
  - `component/` — MVC triplets per UI feature: `controller/` (e.g. `GraphController`, `CodeController`, `ActivationController`) drive `view/` interfaces. The Qt implementations of those views live in `lib_gui/qt/view/`.
  - `app/` — `Application`/`AppPath` glue between project, components, and storage.
  - `settings/`, `utility/` — config + cross-cutting helpers (`ConfigManager`, message queue, commandline parsing, migration utilities).
- `lib_gui/` — Qt 5 frontend. `qt/window/` for top-level windows, `qt/view/` for view implementations, `qt/graphics/` for the custom code-map rendering, `qt/network/` for IDE-plugin sockets, `qt/element/` and `qt/project_wizard/` for widgets.
- `lib_cxx/` — C/C++ language package: `LanguagePackageCxx` registers a libclang-backed `Parser`/`SourceGroup` set under `data/` and `project/`.
- `lib_java/` — Java language package: C++ side wraps the Maven-built indexer in `java_indexer/` via JNI; `data/` and `project/` mirror the C++ shape.
- `lib_python/` — thin wrapper around the prebuilt `SourcetrailPythonIndexer` downloaded by `script/download_python_indexer.sh` during configure.

### Data flow when indexing
1. The user picks a project; `Project` + `SourceGroupFactory` build `SourceGroup`s per enabled language.
2. `RefreshInfoGenerator` diffs file modification state against `PersistentStorage` to decide which files to (re)index.
3. `IndexerCommand`s land on the shared message queue; `Sourcetrail_indexer` processes pull them, run the language `Parser`, and emit `IntermediateStorage`.
4. `TaskMergeStorages` / `TaskInjectStorage` / `TaskFinishParsing` (in `src/lib/data/`) merge results into the SQLite DB through `PersistentStorage`.
5. UI `*Controller`s read through `StorageAccess`/`StorageAccessProxy` to render the graph and code views.

### External code & vendoring
`src/external/` holds vendored third-party sources that are compiled in-tree (Catch2, tinyxml, etc.). Update them via the existing CMake glue rather than installing system copies.

### IDE plugins
`ide_plugins/` ships the Sourcetrail-side integrations (VS, Eclipse, IntelliJ, Sublime, Atom, vim, emacs). They communicate with the running app through `lib_gui/qt/network/` over the protocol in `lib/utility/NetworkProtocolHelper`.

## Coding style

`.clang-format` is the source of truth and applies to all C++:
- C++17, **tabs (width 4)**, Allman braces, 100-column limit, `SortIncludes: true`, `PointerAlignment: Left`, `IncludeBlocks: Preserve`.
- File/class naming is PascalCase (`ConfigManager.cpp`, `QtMainWindow.cpp`); test files end in `*TestSuite.cpp`.
- New code belongs in the module that owns the responsibility — don't reach across `lib`/`lib_gui`/`lib_cxx` boundaries to take a shortcut.

## Git

- Run `bash script/setup_git_hooks.sh` once per clone to install the commit-message template and pre-commit hooks.
- Commit subject format follows the existing log: `<scope>: <title>` with short scopes like `src:`, `ui:`, `docs:`, `res:`, `test:` (e.g. `ui: fix tab focus restore`).
- Don't commit directly to `master`; PRs should describe the problem, link the issue, list manual validation, attach screenshots for UI changes, and add the contributor to `AUTHORS.txt`.
