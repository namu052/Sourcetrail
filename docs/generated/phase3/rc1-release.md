---
status: Generated
owner: codex
last_updated: 2026-04-26
---

# Phase 3 RC1 Release Evidence

## Release

- Tag: `v0.1.0-rc1`
- Milestone: M3 Productivity / RC1
- Scope: Week 22 D106-D110 only

## Week 22 Evidence

| Day | Evidence |
|---|---|
| D106 | Rename regression coverage added for Django, Requests, and Flask fixtures. |
| D107 | Shortcut inventory detects duplicate `QKeySequence` bindings; main window shortcuts have no conflicts. |
| D108 | Fuzzy lookup exact match over 100,000 symbols is gated at `< 50ms`. |
| D109 | Full suite passed with `109 passed`; total coverage `90.04%`, above the 78% gate. |
| D110 | RC1 release tag and G4 gate evidence recorded. |

## Verification

```text
uv run pytest -q --cov-fail-under=78
109 passed, 8 warnings
Required test coverage of 78% reached. Total coverage: 90.04%
```

Targeted Week 22 verification:

```text
uv run pytest tests/integration/test_week22_rename_regression.py tests/ui/test_shortcuts.py tests/performance/test_fuzzy_lookup_performance.py -q
6 passed
```
