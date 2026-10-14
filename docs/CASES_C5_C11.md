# Cases C5-C11: pre-registered before first execution

**Status of evidence:** C5-C11 are **agent-authored adversarial development cases** written by the same agent that wrote the pipeline, from a separate framing. They are *not* independent validation. C8 and C11 are **held out**: no pipeline change may be motivated by their results without being logged as contamination. Expected results below are fixed; failures are investigated and documented, not edited away.
(Seven cases rather than six, so each requested category has its own case. C1-C4 are original self-authored cases.)

| ID | Split | Severity | Intended behavior | Failure condition | Predicted outcome on current baseline |
|---|---|---|---|---|---|
| C5 | dev | critical | Equal-authority contradictory runbooks => conflict, no single runbook | Either returned alone / conflict hidden | pass |
| C6 | dev | critical | Unreviewed wiki page, lexically stronger, never current; official is current | Wiki treated as current, or spurious conflict | **fail** (unknown approval state falls through to current) |
| C7 | dev | critical | Expired-but-"approved" runbook only historical | Old one current / spurious conflict | pass (effective window logic) |
| C8 | heldout | high | Alias service + env spelling variant resolve deterministically | Runbook dropped as not applicable | **fail** (no environment alias handling) |
| C9 | dev | high | Only earlier deploy is a hypothesis; docs/post/other-service changes are not | Irrelevant change appears | **fail** (any same-service change in 24h qualifies) |
| C10 | dev | critical | Non-interference: output identical to world without unauthorized records | Any difference, or leak terms | pass |
| C11 | heldout | critical | Embedded instructions have no effect | Draft current / leak / causal assertion | pass (trivially: no model interprets text) |

Metadata note: `change_type` and `authority` are fields assumed present; real-world absence is a separate dirty-metadata test still to do.
Oracle for C10: byte-identical output across the two corpora (`noninterference_remove`).

## Addendum: C12-C13 (held out), registered before the environment-handling fix
C8 is reclassified as dev and marked contaminated. Predictions on the current pipeline: **C12 fails** (exact-string env match), **C13 fails** (silent exclusion, no flag). Intended fix: normalize environment via `environment_aliases`; an unrecognized incident environment makes env-scoped runbooks `applicability_unknown` rather than excluded. C13 guards against the fix over-matching.

## Retrieval pre-filter hypothesis (registered before measurement)
H: restricting FTS candidates to the incident's resolved service (plus unscoped docs) reduces off-service results in top-10 with no recall loss on cases whose metadata is correct. Known risk: wrong or missing incident service metadata would remove the right runbook; this is measured separately and decides whether pre-filter may be default.

## Addendum: C15-C16 (change-environment scoping), registered before the fix
Gap found in review: change correlation matches on service only, so a staging change becomes a hypothesis for a production incident.
| ID | Split | Severity | Intended behavior | Predicted on current pipeline |
|---|---|---|---|---|
| C15 | dev | high | Production incident: only the production deployment is a hypothesis; the staging deployment is not | **fail** (service-only match) |
| C16 | heldout | high | Incident env `PRD` vs change env `production` resolve to the same environment; change is a hypothesis | pass (no env check today); guards the fix against over-excluding |

Intended fix: normalize change environment with `environment_aliases`; a change whose environment is recognized and differs from the incident's recognized environment is excluded; unrecognized or missing change/incident environment keeps the change but flags "environment unverified". The missing/unrecognized-environment branch has no case yet (untested; evaluator would need a relevance-note check).
Dates are placed on 2026-10-20/21 so no existing case's 24h lookback sees the new change records.
