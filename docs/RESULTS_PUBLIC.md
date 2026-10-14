# Public-source results (S1 Kubernetes docs, dev split only)

**Status:** dev split, one source, 191 cases. **G1 is not evaluable** (needs >=3 sources and held-out). Held-out has not been run. Not evidence of commercial value, production readiness, or effect on real teams. Raw: `results/public_S1_dev_ablate.json`. Pipeline hash `bd263bd5` + Amendment 4 runner.

## Headline numbers (dev; strict registered taxonomy unless stated)
| Family | n / clusters | A failure | N1 failure | N1 failure, equiv. sensitivity | A critical | N1 critical | A-N1 (95% CI, cluster bootstrap) |
|---|---|---|---|---|---|---|---|
| F1 wrong-version | 56 / 19 | 0.750 | 0.964 | 0.750 | 0 | 13 | -0.214 [-0.312, -0.125] |
| F2 stale / not-yet-effective | 57 / 19 | 0.754 | 0.965 | 0.737 | 0 | 13 | -0.211 [-0.304, -0.121] |
| F3 ACL exposure (ACL arm) | 56 / 19 | 0.732 | 0.946 | 0.732 | 0 | 14 | -0.214 [-0.296, -0.146] |
| F4 constructed abstention | 22 / 11 | 0.682 | 1.000 | 1.000 | 0 | 6 | -0.318 [-0.533, -0.150] |

N0 (no ACL) F3: 39 critical of 56. Gold document in top-10: 59-64% for F1-F3 (0% by construction in F4).

## What the numbers do and do not say
1. **Arm A had 0 critical failures; N1 had 13-14 per family (23-25% of cases).** That is the substantive effect: silent wrong-version / not-yet-effective answers become abstentions or conflict flags. Prevalence of N1 critical failure on this corpus: ~23-25% at k=10.
2. **A is not more *correct* than N1 once near-identical versions are treated as equivalent** (equiv. sensitivity: 0.750 vs 0.750 in F1; 0.754 vs 0.737 in F2). The strict advantage in failure rate is largely N1 returning a harmless equivalent revision that the registered taxonomy scores as a failure. The value claim must be stated as **safety (critical errors -> flags)**, not accuracy.
3. **A's own failure rate is ~75%.** Causes, from the diagnostics: gold not retrieved in top-10 (~40%), plus conflict-flag abstentions (~48%), plus wrong-page answers (~27%). Governance cannot recover evidence the retriever did not surface.
4. **Retrieval is the bottleneck.** ~7 near-identical versions per path crowd the 10 slots. This is the strongest candidate for a pre-registered Phase 5 variant (version/window pre-filter on both A and a matching N1 control).
5. **Sufficiency is effectively untested.** In F4 (gold removed) A still answered with a different page in 68% of cases (15/22 wrong_doc): it has no way to tell that a topically different, in-window, right-version page does not answer the query. Governance as built decides *eligibility*, not *relevance sufficiency*.
6. **Ablation:** disabling `conflict` cuts A's failure to 0.49-0.50 but converts abstentions into wrong_doc answers (28) with no critical failures; the check trades coverage for safety. Disabling `lifecycle` in F2 yields 100% abstention (all in-window candidates collide). In F4, disabling `lifecycle` *improves* the failure rate to 0.18 through collisions that force abstention, an artifact, not a real gain.

## Validity problems found in my own design (not yet fixed)
- **F1 and F2 are not separable.** The ticket time T was sampled inside the gold version's own window, so "version known" and "latest version at T" coincide. Disabling `applicability` changes nothing in F1 and disabling `lifecycle` changes nothing there either: the two checks are redundant on this data. A real wrong-version case needs T *after* the gold version's window, with the older version still supported. This must be fixed by amendment and regeneration (held-out was generated with the same flaw; it has not been run).
- **Strict `wrong_doc` conflates "different page" with "equivalent revision".** Both reported (Amendment 4); the strict figure overstates N1.
- **"Approved" and ACL groups are simulated;** F2's gold is policy-defined (Amendment 3).
- **Single source, single query style** (title-only), single k. Title queries favour finding the page itself.

## Not yet done
S2/S3 ingestion; wrong-version redesign (F1'); held-out run; G2 degradation sweep; retrieval pre-filter experiment; sufficiency test beyond constructed removal.
