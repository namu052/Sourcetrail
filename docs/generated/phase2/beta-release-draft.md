# Sourcetrail_Remake v0.2.0-beta.1 Release Draft

Generated: 2026-04-26

Release type: Beta  
Proposed tag: `v0.2.0-beta.1`  
Target branch: current Phase 2 closeout branch  
Tag status: **not created**  
GitHub Release status: **draft prepared in this document**

## Release Summary

`v0.2.0-beta.1` is the proposed Phase 2 MVP Beta checkpoint for the Python
Sourcetrail_Remake application. It adds the Source Insight-style core panel workflow:
Context, Symbol, Relation, and semantic editor decoration, backed by PyQt6/QScintilla
and SourcetrailDB-compatible index data.

This draft is prepared under the G3 conditional-pass record:
[`g3-risk-gate.md`](g3-risk-gate.md).

## Release Highlights

- Context Window for cursor-driven declaration preview.
- Symbol Window with per-file symbol outline, filtering, sorting, icons, access labels, and jump signals.
- Relation Window with calls, called-by, references, overrides, lazy loading, depth limits, empty states, and recursive markers.
- QScintilla editor wrapper with Python lexer styling and debounced cursor events.
- Semantic decorations for unused variables, undefined references, and deprecated declarations/calls.
- Preferences dialog for semantic decoration toggles.
- QSettings-backed dock layout persistence and three built-in layout presets.
- MVP integration coverage against `tests/fixtures/sample-django`.

## Validation Evidence

| Check | Result |
|---|---:|
| `bash scripts/verify-all.sh` | PASS |
| `bash scripts/run-tests.sh` | PASS, 77 tests |
| Total coverage | 90% |
| Phase 2 day commits | D41-D80 present |
| G3 | Conditional Pass |

Primary evidence:

- [`closeout-evidence.md`](closeout-evidence.md)
- [`g3-risk-gate.md`](g3-risk-gate.md)

## Known Limitations

These are accepted limitations for the Beta draft and must not be represented as complete:

- Full 50k LoC Django dogfooding has not been evidenced.
- Current Django verification uses `tests/fixtures/sample-django` as a small MVP proxy.
- The 15-item MVP manual scenario pass sheet is not yet recorded.
- GitHub Release publication has not happened.
- The beta tag has not been created.
- Original Sourcetrail Windows GUI manual-open evidence for the Phase 2 generated DB is not recorded here.
- A single end-to-end timing assertion for simultaneous 3-panel cursor updates is not present.

## Release Blocking Items

Before publishing the GitHub Release or creating the beta tag, one of these decisions is required:

1. Complete and record full-scale Django dogfooding plus remaining release-scale evidence, or
2. Maintainer accepts the missing release-scale evidence as Phase 3 carry-over.

Also required:

- Confirm the tag target commit after all closeout docs are committed.
- Confirm whether `pyproject.toml` should remain `0.1.0` for this Beta checkpoint or be updated in a separate versioning commit.
- Create the GitHub Release from this draft.

## Proposed Git Tag

Recommended tag:

```bash
git tag -a v0.2.0-beta.1 -m "Sourcetrail_Remake v0.2.0-beta.1"
```

Push command, maintainer-only:

```bash
git push origin v0.2.0-beta.1
```

Policy note:

- `docs/reliability.md` says release tags are maintainer-only.
- `docs/sop/human-approval.md` lists release tags / `git push --tags` as human-approval work.
- Therefore this task prepares the release draft but does not create or push the tag.

## Draft GitHub Release Body

### Sourcetrail_Remake v0.2.0-beta.1

This Beta checkpoint introduces the Phase 2 Source Insight-style MVP panel workflow.

#### Added

- Context Window with declaration preview and cursor-driven refresh.
- Symbol Window with outline tree, filtering, sorting, icons, access labels, and jump events.
- Relation Window with relation tabs, lazy tree expansion, depth control, recursive markers, and empty states.
- QScintilla editor wrapper and Python lexer styling.
- Semantic decoration pipeline for unused variables, deprecated patterns, and undefined references.
- Decoration preferences dialog.
- Dock layout save/restore and Default / Source Insight / Wide presets.

#### Validation

- `bash scripts/verify-all.sh`: PASS
- `bash scripts/run-tests.sh`: 77 passed
- Coverage: 90%
- G3: Conditional Pass

#### Known Limitations

- Full-scale 50k LoC Django dogfooding is pending or must be accepted as Phase 3 carry-over.
- GitHub Release assets/installers are not part of this Beta checkpoint.
- Original Sourcetrail GUI manual-open evidence is not included in this draft.

#### Upgrade / Install Notes

This is a source-level Beta checkpoint. Packaging and installer work remains in later phases.
