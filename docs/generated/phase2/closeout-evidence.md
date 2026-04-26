# Phase 2 Closeout Evidence

Generated: 2026-04-26

This document records the evidence currently available for the Phase 2 MVP closeout gate.
G3 disposition is recorded separately in [`g3-risk-gate.md`](g3-risk-gate.md).

## Automated Verification

| Gate | Command | Result | Evidence |
|---|---|---:|---|
| Repository gate | `bash scripts/verify-all.sh` | PASS | lint passed, mypy strict passed, structure-check passed with warnings, docs-freshness OK, adapter-sync passed with warnings |
| Full test suite | `bash scripts/run-tests.sh` | PASS | 77 tests passed |
| Coverage | `bash scripts/run-tests.sh` | PASS | total line coverage 90% |

Notes:
- `verify-all.sh` warnings are pre-existing policy/protected-path warnings and adapter sync warnings; the gate returned `ALL GATES PASSED`.
- Full test coverage exceeds the Phase 2 75% target in `docs/plan/phase-2-context-panels.md` and the 80% target in `docs/exec-plans/active/phase-2-source-insight-panels.md`.

## Day Commit Evidence

| Range | Evidence |
|---|---|
| D41-D50 Context Window | `e290bb6b` through `d0aeea9e` |
| D51-D60 Symbol Window | `59ed66ad` through `2ce09482` |
| D61-D70 Relation Window | `fcd79b13` through `7c8d37ea` |
| D71-D80 Syntax/Integration | `f8d0e16c` through `70ab2c3d` |

All planned D41-D80 day commits are present in git history.

## Phase 2 DoD Evidence

| DoD item | Evidence status | Evidence |
|---|---|---|
| 4 Source Insight panels work: Context / Symbol / Relation / Syntax | Verified by automated tests | `tests/ui/test_context_window.py`, `tests/ui/test_symbol_window.py`, `tests/ui/test_relation_window.py`, `tests/unit/test_syntax_decorator.py`, `tests/integration/test_semantic_decoration_flow.py` |
| Cursor movement updates panels within debounce model | Partially verified | `QScintillaEditor` emits debounced `cursor_moved`; Context Window tests cover cursor-driven refresh. A single end-to-end timing assertion for all three panels is not present. |
| 3 layout presets save/restore | Verified by automated tests | `tests/ui/test_layout_manager.py` covers QSettings save/restore and Source Insight preset application. |
| Unused variable and deprecated call decoration on/off | Verified by automated tests | `tests/ui/test_preferences_dialog.py`, `tests/integration/test_semantic_decoration_flow.py`, `tests/unit/test_week15_semantic_coverage.py` |
| Django project MVP scenario | Partially verified | `tests/integration/test_phase2_mvp_django_flow.py` covers `tests/fixtures/sample-django`. This is not a 50k LoC Django project. |
| Unit test coverage target | Verified | `bash scripts/run-tests.sh` reports 90% total coverage. |
| Beta release tag / GitHub Release | Draft prepared, tag not created | `docs/generated/phase2/beta-release-draft.md`; existing tags include `v0.1.0-alpha.1`; no beta tag exists yet. |
| G3 risk gate passed | Conditional pass recorded | `docs/generated/phase2/g3-risk-gate.md`; release-scale evidence remains pending. |

## MVP Scenario Coverage

The planned 15-item MVP scenario from `docs/plan/phase-2-context-panels.md` is covered only partially by automated tests.

| Scenario group | Evidence status | Evidence |
|---|---|---|
| Project indexing and graph display | Verified | Phase 1 and Phase 2 integration tests, including `test_phase1_gui_flow.py` and `test_phase2_mvp_django_flow.py` |
| Graph depth slider / zoom / bookmarks / history / FQN search | Verified | `tests/integration/test_phase1_gui_flow.py`, navigation and control UI tests |
| Context / Symbol / Relation panel behavior | Verified | Dedicated UI tests plus `tests/integration/test_relation_panels_flow.py` |
| Semantic decorations | Verified | Week 15 analyzer and semantic decoration tests |
| Original Sourcetrail DB compatibility | Partially verified | `tests/compatibility/test_schema_tables.py`; no original GUI manual-open evidence in this closeout ledger |
| 50k LoC Django dogfooding | Not evidenced | Current automated coverage uses `tests/fixtures/sample-django` |
| Beta release publication | Draft prepared, tag not created | `docs/generated/phase2/beta-release-draft.md`; no beta tag or published GitHub Release evidence |

## Closeout Assessment

Implementation and automated test evidence are strong enough to support a Phase 2 closeout review:
- D41-D80 commits exist.
- Repository gates pass.
- Full tests pass.
- Coverage target is exceeded.

Phase 2 should not be marked fully complete until the remaining release evidence is added:
- Create the beta release tag / published GitHub Release, or record maintainer acceptance of draft-only Beta preparation.
- Decide whether the 50k LoC Django requirement is mandatory now or explicitly accepted as a Phase 3 carry-over with `sample-django` as the MVP proxy.
