# Phase 2 G3 Risk Gate

Generated: 2026-04-26

Gate: G3  
Week: 16  
Question: Can Sourcetrail_Remake dogfood itself and satisfy the MVP closeout bar?

## Disposition

**G3 conditionally passes for implementation readiness.**

The implementation and automated verification are sufficient to proceed with Phase 2 closeout work,
but G3 is not a clean release pass yet. The remaining release-scale evidence must either be completed
before tagging Beta or explicitly accepted as Phase 3 carry-over by the maintainer.

## Evidence Accepted

| Evidence | Result |
|---|---:|
| `bash scripts/verify-all.sh` | PASS |
| `bash scripts/run-tests.sh` | PASS, 77 tests |
| Total line coverage | 90% |
| D41-D80 day commits | Present |
| Context / Symbol / Relation / Syntax automated coverage | Present |
| Sample Django MVP integration | Present via `tests/fixtures/sample-django` |

Primary evidence ledger: [`closeout-evidence.md`](closeout-evidence.md)

## Explicit Scope Difference

The Phase 2 plan says:

- Django project target: approximately 50k LoC.
- MVP scenario target: 15 scenarios against that project.

Current automated evidence uses:

- `tests/fixtures/sample-django`
- A small fixture project, not a 50k LoC Django codebase.
- `tests/integration/test_phase2_mvp_django_flow.py` as the MVP proxy.

This means the Django requirement is **partially verified**, not fully satisfied. The sample fixture
is accepted only as an MVP proxy for implementation readiness.

## Carry-Over Items

These items remain outside the conditional G3 pass:

| Item | Status | Required follow-up |
|---|---|---|
| 50k LoC Django dogfooding | Carry-over | Run and record full-scale dogfooding, or formally waive for Beta |
| 15-scenario manual MVP pass sheet | Carry-over | Add scenario-by-scenario pass evidence |
| Beta tag / GitHub Release | Blocking release task | Create beta release draft and tag, e.g. `v0.2.0-beta.1` |
| Original Sourcetrail GUI manual DB-open evidence | Carry-over | Add manual compatibility evidence if required for Beta |
| 3-panel cursor update timing assertion | Carry-over | Add an end-to-end timing test or manual timing note |

## Gate Decision

G3 status: **Conditional Pass**

Allowed next step:
- Continue Phase 2 closeout documentation and Beta release preparation.

Not allowed from this record alone:
- Claim a full Phase 2/Beta release pass.
- Mark the 50k LoC Django requirement complete.
- Mark GitHub Beta release complete.

Final G3 pass requires either:

1. Beta release evidence plus full-scale dogfooding evidence, or
2. Maintainer-approved carry-over of the missing release-scale evidence into Phase 3.
