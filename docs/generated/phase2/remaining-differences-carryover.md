# Phase 2 Remaining Differences and Carry-Over

Generated: 2026-04-26

This ledger records the differences between the Phase 2 closeout target and the evidence currently
available at the end of Phase 2. It is the authoritative carry-over list for final G3/Beta signoff.

Related records:
- [`closeout-evidence.md`](closeout-evidence.md)
- [`g3-risk-gate.md`](g3-risk-gate.md)
- [`beta-release-draft.md`](beta-release-draft.md)

## Summary

Phase 2 implementation evidence is sufficient for a conditional closeout, but not for a clean
release-scale G3 pass. The main difference is that automated validation uses the small
`tests/fixtures/sample-django` fixture as the MVP proxy, while the Phase 2 plan calls for
dogfooding on an approximately 50k LoC Django project and a complete 15-scenario pass record.

## Plan vs Current Evidence

| Target | Current evidence | Gap | Disposition |
|---|---|---|---|
| Django project target of approximately 50k LoC | `tests/fixtures/sample-django` through `tests/integration/test_phase2_mvp_django_flow.py` | Scale and realism are not equivalent to a real 50k LoC Django codebase | Carry over or formally waive for Beta |
| 15 MVP scenarios all passed | Automated tests cover the core workflow groups, but no scenario-by-scenario manual pass sheet exists | Scenario-level evidence is incomplete | Carry over |
| Clean G3 pass | `docs/generated/phase2/g3-risk-gate.md` records Conditional Pass | Release-scale evidence remains pending | Conditional pass only |
| Beta GitHub Release and public tag | `docs/generated/phase2/beta-release-draft.md` prepared; proposed tag is `v0.2.0-beta.1` | Tag and GitHub Release were not created | Maintainer-controlled follow-up |
| Cursor movement updates Context/Symbol/Relation within 150ms | Debounced editor cursor events and Context refresh are tested | No single end-to-end timing assertion for all three panels | Carry over |
| Original Sourcetrail GUI can open generated DB | Schema compatibility tests exist | No manual original-GUI open/read evidence in this closeout ledger | Carry over if required for Beta |
| Exec-plan-only graph hover preview | Context and graph selection behavior have tests | Hover-preview evidence is not present | Carry over |
| Exec-plan-only Relation Graph/Tree toggle and multi-window lock | Relation tree tabs, lazy loading, depth, selection, and recursive markers are tested | Graph/Tree toggle and multiple locked Relation windows are not evidenced | Carry over |
| Exec-plan-only closing-block annotation | Syntax and semantic decoration tests exist | Closing-block annotation is not evidenced | Carry over |
| Exact `self`/`cls` scope styling | Semantic analyzer and decorator tests exist | Exact visual distinction for `self`/`cls` is not evidenced | Carry over |

## Carry-Over Items

| ID | Item | Required follow-up | Suggested destination |
|---|---|---|---|
| P2-CO-01 | 50k LoC Django dogfooding | Run against a real or representative 50k LoC Django project, record timing and scenario results, or record a maintainer waiver | Phase 3 entry gate or Beta final signoff |
| P2-CO-02 | 15-scenario MVP pass sheet | Add a scenario-by-scenario pass/fail sheet with evidence links | Phase 3 entry gate or Beta final signoff |
| P2-CO-03 | Beta tag and GitHub Release | Create `v0.2.0-beta.1` and publish/reconcile the release notes after maintainer approval | Release process |
| P2-CO-04 | Original Sourcetrail GUI DB-open evidence | Manually open a generated DB in original Sourcetrail and record result, screenshot, or waiver | Compatibility/Beta final signoff |
| P2-CO-05 | 3-panel cursor timing assertion | Add an end-to-end UI timing test or manual timing note proving Context/Symbol/Relation refresh behavior | Phase 3 regression suite |
| P2-CO-06 | Graph hover preview | Implement or explicitly descope the hover-preview behavior from the active exec-plan wording | Phase 3 backlog triage |
| P2-CO-07 | Relation Graph/Tree toggle and multi-window lock | Add implementation/tests or formally defer to a later Relation Window enhancement | Phase 3 backlog triage |
| P2-CO-08 | Closing-block annotation | Implement/test inline or margin annotation for closing blocks, or defer with rationale | Phase 3 editor backlog |
| P2-CO-09 | Exact `self`/`cls` styling | Add visual style assertions or document the accepted fallback styling | Phase 3 editor backlog |

## Closeout Rule

Do not mark Phase 2 as a clean full release pass until either:
- all carry-over items required for Beta are completed and evidenced, or
- the maintainer explicitly accepts the remaining items as Phase 3 carry-over.

Until then, Phase 2 status remains: **Completed with Conditional G3 Pass**.
