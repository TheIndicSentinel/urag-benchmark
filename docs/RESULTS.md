# Results log

All cases are synthetic and agent-authored (C1-C4 by the baseline author, C5-C11 as adversarial development cases). **No result here is independent validation, commercial evidence, or evidence of production readiness.** n=11.

## Run 1: baseline as committed in 0493185 (`results/run1_initial.json`)
8/11 passed. Predictions registered in `CASES_C5_C11.md` before execution matched all 7 new cases.

| Case | Result | Cause (verified) |
|---|---|---|
| C6 low-authority wiki | FAIL, critical | `classify_runbook` only denied `draft/superseded/deprecated`; unknown states such as `unreviewed` fell through to current_guidance (fail-open). Official + wiki then both "current" -> spurious conflict. |
| C8 service alias + env spelling | FAIL, high, held out | Service alias resolved correctly; environment compared by exact string (`Production` vs `prod`), so the runbook was dropped as "not applicable" with no flag. |
| C9 irrelevant nearby change | FAIL, high | Every same-service change within 24h became a hypothesis, including a docs-only change. |

## Run 2: after fixes to C6 and C9 only (`results/run2_after_dev_fixes.json`)
10/11 pass. Fixes: fail-closed approval state (only `approved` is guidance); changes limited to runtime-affecting `change_type`, missing type kept but flagged "relevance unverified".

| Metric | Value |
|---|---|
| Passed | 10 of 11 (dev 9/9, held-out 1/2) |
| Critical failures | 0 (within this small set) |
| Coverage (answered) | 0.73 |
| Risk among answered | 0.0 |
| Correct abstentions | 2 |
| Unnecessary abstentions | 1 (C8) |
| Mean recall@10 | 0.80 |

**C8 deliberately left failing.** The fix (environment alias map, already present in corpus as `environment_aliases`) is obvious, but applying it changes behavior on a held-out case. It will be fixed together with a new, unseen sibling case so the fix can be checked on fresh data; the old C8 will then be reclassified as dev (contaminated).

## Caveats on the numbers
- **Recall@10 for change records is not measured**: changes are located by structured lookup, not FTS (C3 and C9 show 0.0 as an artifact). C10 has no relevant set.
- **C11 is baseline-trivial**: nothing in the deterministic pipeline interprets text, so passing says little. It is meaningful only for the constrained-LLM variant.
- **Retrieval is noisy**: the OR query lets common tokens ("api", "errors") pull unrelated services into top-10 (C3 retrieves notify/auth/search runbooks). It's harmless today because classification filters them, but it will crowd out relevant records as the corpus grows. Metadata pre-filtering is the likely fix and should be measured before adopting.
- `change_type` and `approval_state` are assumed present and correct; missing/wrong values in real systems are untested beyond one case.
- One data point, not a coverage-risk curve; no threshold exists to sweep yet.

## Run 3-5: environment handling, pre-filter, and two latent bugs
Files: `results/run3_*`, `run4_*`, `run5_*`.

**Run 3 (before fix):** C8, C12, C13 fail as pre-registered. 10/13.
**Run 4 (env normalization + unknown-env flagged):** 13/13 default mode. C12 and C13 passed, but they were written by the same agent that knew the fix, so this is weak confirmation. C8 is contaminated and no longer counts as held out.

**Pre-filter hypothesis check (Run 4, prefilter mode): 11/13, two failures, both traced:**
| Failure | Cause | Class |
|---|---|---|
| C5 `insufficient_evidence` instead of `conflicting_evidence` | Final status assignment overwrote the conflict status when no historical/hypothesis items existed. In default mode an off-service incident (`inc-0900`) leaked in as "historical" and masked this. | Real pipeline bug, latent since baseline |
| (same cause) off-service historical incident | Historical incidents were never checked for service applicability | Real applicability bug |
| C10 output differs | Non-interference reference ran without the prefilter mode, so two different modes were compared | Evaluator bug; not a leak |

**Run 5 (all fixes):** 14/14 in both modes. C14 was added post-hoc as a regression case for the history leak (dev, not pre-registered).

| Metric (n=14) | default | prefilter |
|---|---|---|
| Passed | 14 | 14 |
| Critical failures | 0 | 0 |
| Coverage / risk among answered | 0.71 / 0.0 | 0.71 / 0.0 |
| Correct / unnecessary abstentions | 4 / 0 | 4 / 0 |
| Mean off-service docs in top-10 | 6.64 | 0.0 |
| Mean recall@10 | 0.85 | 0.85 |

**Reading it:** pre-filtering removes off-service noise with no recall loss on these cases. Cross-service runbooks would be classified "not applicable" anyway, so the benefit is protecting top-k from crowd-out as the corpus grows, not changing outputs today. Untested: unscoped docs when service is missing in the incident (pre-filter is skipped when the service doesn't resolve), and corpus sizes where crowd-out matters (current corpus has ~30 docs). Not yet made default.

**Lesson:** the noise hid a correctness bug. Running every case in both modes is now part of the unit tests.
