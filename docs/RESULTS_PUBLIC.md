# Public-source results (S1 Kubernetes docs, dev split only)

> **v1 section below is superseded by v2 (config v2, Amendment 5).** v1 retained for the record because it exposed the F1/F2 redundancy.

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


---
# v2 results (config v2, Amendment 5), dev only, S1 only
Raw: `results/public_S1_dev_ablate.json`, pipeline hash `4f7a3a21`. 192 dev cases. **G1 not evaluable** (1 source, no held-out). Strict registered taxonomy; sensitivity in brackets.

| Family | n / clusters | A fail [equiv] | N1 fail [equiv] | A crit | N1 crit | A-N1, 95% cluster-bootstrap CI |
|---|---|---|---|---|---|---|
| F1 wrong-version | 56 / 19 | 0.625 [0.625] | 0.911 [0.768] | 0 | 16 (29%) | -0.286 [-0.446, -0.135] |
| F2 stale / not-yet-effective | 57 / 19 | 0.842 [0.842] | 0.982 [0.877] | 0 | 21 (37%) | -0.140 [-0.200, -0.075] |
| F3 ACL exposure | 56 / 19 | 0.679 [0.679] | 0.964 [0.893] | 0 | 20 (36%) | -0.286 [-0.423, -0.171] |
| F4 constructed abstention | 23 / 12 | 0.522 | 1.000 | 0 | 6 | -0.478 [-0.667, -0.300] |

N0 (no ACL) F3 critical: 47/56.

## Reading
1. **The redundancy is fixed.** Ablation now attributes effect: F1 needs `applicability` (A-applicability: 1.00 failure, all abstained); F2 needs `lifecycle` (1.00). Other checks are inert where they should be.
2. **Safety effect is large on this corpus:** A had 0 critical failures; N1's top-1 was a critical error in 29-37% of cases (prevalence at k=10, title queries, 7 versions/path). Under the equivalence sensitivity A still beats N1 in F1 (0.625 vs 0.768) but only marginally in F2 (0.842 vs 0.877).
3. **A is wrong or silent in 52-84% of cases**, mostly because the gold page is absent from the top-10 (gold@10 = 0.51-0.61) and because conflicts are flagged (abstained 25-36 of 56).
4. **`conflict` is a safety/coverage trade:** disabling it cuts failure to 0.45-0.55 by answering with a top-ranked candidate, and introduces 1 critical failure in F2 and F4 each. Disabling `lifecycle` or `applicability` in F4 lowers failure only by forcing collisions that cause abstention, an artifact, not a gain.
5. **Sufficiency gap persists:** F4 A answered with a different page in 52% (12/23). Still no relevance-sufficiency check.

## Still true
Single source, simulated approval/ACL, title-only queries, k=10, gold-derived queries favour retrieval of the gold path. Not G1. Held-out never run.

---
# v3: S1+S2 dev, variants and metadata-filter control (Amendment 6)
Raw: `results/public_S1-S2_dev_variants.json` (289 dev cases; 47/47/45/24 clusters per family). **G1 not evaluable** (2 sources; dev). Strict taxonomy; `crit` = critical failures.

| Family (n) | N1 fail/crit | N1P fail/crit | A fail/crit | A2 fail/crit | A2P fail/crit | A2P-N1P (95% CI) |
|---|---|---|---|---|---|---|
| F1 wrong-version (85) | 0.906 / 25 | 0.424 / 0 | 0.729 / 0 | 0.424 / 0 | 0.424 / 0 | 0.000 [0.000, 0.000] |
| F2 stale/not-yet-effective (86) | 0.895 / 27 | 0.826 / 10 | 0.895 / 0 | 0.477 / 1 | 0.477 / 0 | -0.349 [-0.447, -0.250] |
| F3 ACL exposure (83) | 0.904 / 25 | 0.518 / 0 | 0.771 / 0 | 0.506 / 0 | 0.518 / 0 | 0.000 [0.000, 0.000] |
| F4 constructed abstention (35) | 1.000 / 11 | 1.000 / 2 | 0.457 / 0 | 0.971 / 2 | 1.000 / 2 | 0.000 [0.000, 0.000] |

## Findings
1. **On clean metadata, a metadata filter matches governance on F1 and F3.** `N1P` (ACL + version/window filter before ranking, top-ranked output, no governance decisions) has 0 critical failures and exactly the same per-case outcomes as `A2P` (paired difference 0, CI [0, 0]). Amendment 6.3's falsification reading is therefore **not triggered** for these families, and cannot be until metadata is degraded (G2): **on this data F1 and F3 cannot distinguish the governance layer from a metadata filter: the outcomes are identical by construction (expectations are scripted from the same fields the filter uses), so the [0, 0] interval describes the construction, not the world. This is not a falsification of the thesis; it is the absence of a test.**
2. **Governance adds measurable value only where policy has to be applied:** F2 (version unspecified). The lineage rule removes N1P's 10 critical failures (older supported revision presented as current) and lowers failure from 0.826 to 0.477. Caveat: F2's gold is policy-defined (Amendment 3.2), so this shows the rule implements the stated policy, not that users want it.
3. **Tautology warning (important).** Expected behaviour is scripted from the same version/window metadata the filter uses, so `N1P` succeeds largely by construction. These families cannot separate filtering from governance on clean metadata; the registered G2 degradation sweep (missing/corrupt metadata) is where silent filtering and flagged abstention should differ. No conclusion about real metadata quality is supported yet.
4. **`conflict` as built is a coverage killer in document corpora** (A: abstained 52-65 of 85-86 in F1/F2) and the A2 variant restores coverage but **loses abstention under missing evidence**: in F4 A2/A2P/N1P answer in 97-100% (A: 46%). The old conflict rule was acting as an accidental sufficiency proxy. No variant has a real sufficiency check.
5. **`AP` abstains on everything** (F1-F3 failure 1.00, F4 0.00): the degenerate always-abstain profile; reported to keep coverage-vs-risk honest.
6. **Variant selection (Amendment 6.4):** by the registered rule (0 critical, then lowest failure) the carried variant is **A itself**; A2P is a better coverage profile but has 2 critical failures in synthetic F4 and is **exploratory only**, not selected.

## Labelling corrections (after review)
- `N1P`, `AP`, `A2`, `A2P` are **post-hoc** variants/controls: defined after seeing dev results for N1 and A (Amendment 6 was written before their code, but in response to those results). `N1P` is still the right comparison; it is not a pre-planned control.
- **Finding about the frozen arm A:** the `conflict` check treats *multiple eligible documents* as *contradiction*. Distinct pages of the same service and version are not contradictory. In legacy runbook cases the proxy ("two approved runbooks for the same service and environment") is defensible; in document corpora it over-abstains (S2: A fails more than N1). This is a scoping flaw in the frozen rule, recorded here as a result, not tuned away. A2 is a variant, not a fix of arm A.
- **F4 twins derived from F2 are mis-specified:** removing the latest revision leaves an older revision of the same page that is a legitimate answer under the lineage rule. Corrected by Amendment 8 (twins from F1 only).

## Per-source note
S1: A 0.62/0.84/0.68 (F1-F3) vs N1 0.91/0.98/0.96. S2: A 0.93/1.00/0.96 vs N1 0.90/0.72/0.78: **A is worse than N1 on S2 failure rate** (conflict abstention) while having 0 critical failures vs N1's 20 critical across S2 F1-F3.

## What this changes
- Value claim narrows to: *eligibility governance converts silent critical errors into flags/abstentions*, and a **simple metadata prefilter delivers most of that on clean metadata.** The distinct contribution is lineage/lifecycle policy and behaviour under degraded metadata, both still to be shown.
- Not yet run: S3, held-out, G2 sweep.

---
# v4: corrected F4, sufficiency (A-S), closed filter, query styles. Dev, S1+S2, 275 cases (F4 twins now F1-only: n=21)
Raw: `results/public_S1-S2_dev_variants.json` (title queries), `..._variants_lead.json` (lead queries, Amendment 8.2). **Not G1 evidence** (2 sources, dev). fail/crit(ical)/abstained/wrong_doc per family.

| Style | Family | N1 | N1P(-closed identical, clean data) | A | A-S | A2 | A2-S |
|---|---|---|---|---|---|---|---|
| title | F1 | .91/25/0/52 | .42/0/0/36 | .73/0/52/10 | .62/0/38/15 | .42/0/2/34 | .42/0/5/31 |
| title | F2 | .90/27/0/50 | .83/10/0/61 | .90/0/65/12 | .80/0/51/18 | .48/1/0/40 | .47/1/1/38 |
| title | F3 | .90/25/0/50 | .52/0/0/43 | .77/0/53/11 | .69/0/42/15 | .51/0/2/40 | .49/0/4/37 |
| title | F4 | 1.00/5/0/16 | 1.00/0/0/21 | .57/0/0/12 | .48/0/0/10 | .81/0/0/17 | .67/0/0/14 |
| lead | F1 | .78/26/0/40 | .22/0/0/19 | .72/0/51/10 | .58/0/40/9 | .22/0/0/19 | .21/0/2/16 |
| lead | F2 | .85/32/0/41 | .76/18/0/47 | .84/0/67/5 | .66/0/53/4 | .19/0/0/16 | .17/0/1/14 |
| lead | F3 | .75/23/0/39 | .18/0/0/15 | .69/0/53/4 | .54/0/41/4 | .18/0/0/15 | .17/0/1/13 |
| lead | F4 | 1.00/8/0/13 | 1.00/0/0/21 | .62/0/0/13 | .52/0/0/11 | .76/0/0/16 | .67/0/0/14 |

## Findings
1. **F1/F3 are non-informative by construction** (A2 and N1P identical per case; CI [0,0]). Not a falsification of the thesis; the absence of a test (see label corrections above).
2. **F2 is the only family where a governance rule changes outcomes on clean metadata**: lead queries, N1P 0.76 / 18 critical vs A2 0.19 / 0 critical; title queries 0.83 / 10 vs 0.48 / 1. Policy-defined gold (Amendment 3.2); the one remaining A2 critical failure in F2 is unexamined.
3. **Retrieval quality is the dominant factor**: gold@10 is 0.57-0.64 with title queries and 0.82-0.90 with lead queries; every arm's failure rate falls sharply with the better query. Absolute failure rates should not be read as product accuracy.
4. **Sufficiency (A-S, threshold 0.70, fixed a priori) mostly acts by resolving conflicts, not by abstaining on irrelevant evidence.** A-S vs A: F1 -0.11 / -0.14 (title/lead), F2 -0.09 / -0.17, F3 -0.08 / -0.14, all with CI excluding 0. But on F4, the case it was meant for, it removes only 2 of 13 wrong answers under lead (-0.095, CI [-0.22, 0.0]) and 2 of 12 under title (CI [-0.26, 0.0]): A-S still answers wrongly in 11/21 (lead). Under Amendment 8.3 sufficiency is **not declared dropped** (no coverage loss) but is **not demonstrated**: a lexical coverage floor cannot tell an on-topic near-duplicate page from the answer. A real sufficiency claim needs content-level evidence the benchmark does not provide.
5. **A's abstention in F4 is accidental** (the conflict rule); N1P answers wrongly in 100% of F4 cases with 0 critical failures; A answers wrongly in 57-62%. No arm has a working sufficiency check.
6. `N1P-closed` equals `N1P` on clean data, as expected (no missing fields); the difference appears only in G2.

---
# Determinism check (Amendment 9.5)
Task `S2 / level 25 / corrupt / seed 12`, first 40 dev cases, five arms, run in two separate processes: `PYTHONHASHSEED=1` with index cache size 1, and `PYTHONHASHSEED=777` with cache size 3. SHA-256 prefix of the sorted JSON result: **`2e2eaa30b0620160` in both**. G2 outputs are independent of process, hash seed and cache size; checkpoint resumes and worker count therefore cannot change results (tasks are pure functions of source, level, mode, seed).
Scope of the check: one task, one source. It is a spot check, not a proof.


---
# G2 degradation sweep: title-style queries (SECONDARY; see Amendment 12)
Procedure per Amendments 7 and 9; 36/36 tasks (S1, S2 x levels 10/25/50 x drop/corrupt x seeds 11/12/13); dev split only; matched-coverage rule applied; per-task digests in `results/public_G2_dev_summary.json`. **Executed with title queries, not the registered primary `lead` style (Amendment 12).**

Means over 3 seeds, pooled over S1+S2 dev cases (n=275). cov = answered; crit/wrong = rate over all cases; silent = wrong or critical with no flag; risk = (critical+wrong)/answered.

| Mode/level | Arm | cov | crit | wrong | silent | risk@ans | matched-coverage risk vs N1P / N1P-closed |
|---|---|---|---|---|---|---|---|
| corrupt/10 | N1P | 1.00 | .050 | .650 | .699 | .699 | |
| | A | .347 | .002 | .200 | .202 | .584 | .584 vs .701 / .698 |
| | A2 | .851 | .011 | .461 | .471 | .554 | .554 vs .699 / .698 |
| corrupt/50 | N1P | 1.00 | .101 | .779 | .880 | .880 | |
| | A | .285 | .023 | .204 | .227 | .795 | .795 vs .881 / .881 |
| | A2 | .584 | .070 | .400 | .470 | .805 | .805 vs .881 / .880 |
| drop/10 | N1P / N1P-closed | 1.00 | .075 / .052 | .602 / .645 | .678 / .697 | .678 / .697 | |
| | A | .451 | .002 | .281 | **.057** | .629 | .629 vs .674 / .697 |
| | A2 | .875 | .015 | .507 | **.099** | .596 | .596 vs .678 / .697 |
| drop/50 | N1P / N1P-closed | 1.00 | .233 / .078 | .612 / .766 | .845 / .844 | .845 / .844 | |
| | A | .303 | .019 | .219 | **.009** | .782 | .782 vs .845 / .841 |
| | A2 | .389 | .039 | .275 | **.009** | .797 | .797 vs .846 / .841 |
(levels 25 behave in between; full table in the summary file.)

## Registered verdict (mechanical)
`favours_governance = TRUE` for A **and** A2: at matched coverage, risk is lower than both `N1P-open` and `N1P-closed` in all 3 levels under both `drop` and `corrupt`.

## Reading (what the rule does not say)
1. **The margins are modest.** Matched-coverage risk improves by about 0.04-0.12 (e.g. 0.584 vs 0.701; 0.782 vs 0.845). The registered rule is a strict inequality on means with no interval; 3 seeds on a 275-case dev set cannot support a stronger claim. No CI was registered for this rule.
2. **Absolute risk is high for every arm** (0.55-0.80 of answered cases are wrong or critical), because title queries retrieve the gold page in only ~0.6 of cases (Section v4).
3. **Where governance clearly differs is flagging.** Under `drop`, A's silent-error rate is 0.9-5.7% against 68-85% for the filters: missing metadata is flagged instead of silently mis-answered. This is the "flagging, not accuracy" reading of Amendment 7.6, and it is the main effect. A pays for it with coverage (0.30-0.45 answered).
4. **Open vs closed filter is a real trade-off,** not a free choice: closed cuts critical failures (0.078 vs 0.233 at drop/50) by dropping candidates, at the cost of more wrong answers (0.766 vs 0.612).
5. **Under `corrupt`, nothing can detect the change;** A's advantage there comes from selective answering (coverage 0.28-0.35), not from detecting corruption.
6. **A2's critical rate rises with degradation** (0.07 at corrupt/50), above A's 0.023; it remains below `N1P-open` and `N1P-closed` at drop/50 but not below the closed filter by much at low levels.
7. **Not G1 evidence.** Dev split only; synthetic metadata degradation of fields the governance rules use by construction.
