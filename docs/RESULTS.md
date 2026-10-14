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
