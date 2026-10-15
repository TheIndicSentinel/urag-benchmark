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

## Supplementary: seed-level spread of the title-style G2 (not a gate; Amendment 12 reading)
Script `src/urag/public_g2_spread.py`, output `results/public_G2_dev_spread.json`. For each (mode, level, governance arm, filter) and each seed, the gap = filter matched-coverage risk minus governance matched-coverage risk (positive = governance lower). Uses its own seeded random draws (20261020), so values differ slightly from the gate script's means. Descriptive only: no interval, no test, and no change to the registered strict-inequality verdict.
- **70 of 72** seed-level gaps are positive across 24 (mode, level, arm pair) cells x 3 seeds; **1 is negative** (`drop/10`, A vs `N1P-open`, seed 13: -0.001) and **1 is exactly zero** (`drop/50`, A2 vs `N1P-closed`, seed 12).
- Typical gaps are +0.02 to +0.16. They are largest under `corrupt/10` (A2: +0.13 to +0.16) and smallest under `drop/50` for A2 (as low as 0.00).
- Reading: consistent direction, small size, and not uniformly strict at seed level. This supports "modestly lower risk at matched coverage", not a robust margin.
- The lead-style spread (gate-relevant) will be produced by the same script only after all 36 lead-style tasks exist; the script refuses earlier.

## Registration order for the lead-style G2 (evidence as of 2026-10-15 18:12 IST)
- Amendment 12 commit `b631207`: author date 2026-10-15T17:15:07+05:30 (local clock). Runner change commit `2adea98`: 17:15:22.
- Earliest lead-style checkpoint file modification time (name and mtime only; contents unread): 2026-10-15T17:16:47.
- Both are on the **local clock**. An external timestamp can only bound the amendment's existence from above; it cannot prove it preceded the first lead output. What does hold regardless: the amendment text states the rule before any lead-style output was read, and the commit chain hashes make later edits detectable. The push is intended to anchor the amendment text externally before the lead run is read.

---
# G2 degradation sweep: lead-style queries (GATE-RELEVANT, Amendment 12)
Same procedure, arms, seeds and reading rule as the title-style sweep; 36/36 tasks validated before reading (digests in `results/public_G2_dev_summary_lead.json`); dev split only; n=275 cases pooled over S1+S2; means over 3 seeds.
**Order evidence:** Amendment 12 committed 2026-10-15T17:15:07+05:30 (local); first lead-style checkpoint 17:16:47 (local); the amendments were pushed to the public repo with GitHub push time **2026-10-15T12:58:12Z (18:28 IST)**, and the lead-style result was read only after that push.

## Registered verdict (mechanical): `favours_governance = FALSE` for A and for A2
Wins by (mode: level 10/25/50): both arms `drop: true, true, FALSE`; `corrupt: true, true, true`. The failing cell is **drop / level 50**:

| Cell | Arm | matched-coverage risk | N1P (open) | N1P-closed |
|---|---|---|---|---|
| drop/50 | A | **0.748** | 0.733 | 0.792 |
| drop/50 | A2 | **0.744** | 0.736 | 0.793 |

At the heaviest degradation, A and A2 are 0.015 and 0.008 *worse* than the open filter at matched coverage and better than the closed filter. Under the registered rule a single failing cell makes the mode, and so the verdict, false (Amendment 9.2: mixed counts as false).

## Both verdicts
| Query style | Role | A | A2 |
|---|---|---|---|
| title | secondary (ran by mistake as the primary; Amendment 12) | TRUE | TRUE |
| **lead** | **gate-relevant** | **FALSE** | **FALSE** |

## Supplementary seed-level spread (lead-style; descriptive, not a gate)
- 67 of 72 seed-level gaps are positive (title-style: 70 of 72). **Four cells have at least one negative seed**: `drop/10 A|N1P` (-0.001), `drop/50 A|N1P` (-0.057), `drop/50 A|N1P-closed` (-0.007), `drop/50 A2|N1P` (-0.045 and -0.022; only 1 of 3 seeds positive).
- Under `corrupt`, gaps are large and consistent (A: +0.08 to +0.19; A2: +0.11 to +0.25). Under `drop`, gaps are small and unstable, and they turn negative at the heaviest level.

## Reading
1. **The rule fired as pre-registered.** The result is not "governance fails everywhere": A is lower-risk than both filters in 5 of 6 mode/level cells (11 of 12 pairwise comparisons; the same for A2), and the one failing cell is a narrow margin at the most severe `drop` level. But the rule was fixed in advance with no tolerance, and it is applied as written. The outcome does not depend on how favourable the other cells are.
2. **What survives:** (a) lower critical-failure rates than a plain top-ranked retriever (N1) in every cell; (b) low *silent*-error rates under `drop` (A: 0.007-0.045 versus 0.51-0.80 for the filters), i.e. missing metadata is flagged, at a coverage cost (A answers 30-44%); (c) the lineage/lifecycle rule, whose effect is policy-defined.
3. **What does not survive:** a claim that the governance rules answer *more correctly than a metadata filter* under heavy metadata loss. At matched coverage under `drop/50` they do not.
4. **Not evidence for or against commercial value.** Dev split, synthetic degradation of fields the rules use, two sources, title/lead queries derived from gold pages.

---
# Plain-language statement of the G2 outcome (supersedes any looser wording above)
- **Under `corrupt` metadata, governance clearly helps:** at matched coverage the risk is lower than both filters at every level (A vs the open filter: 0.404 vs 0.536 at level 10, 0.548 vs 0.704 at level 25, 0.727 vs 0.842 at level 50; i.e. lower by 0.13, 0.16 and 0.12), and all seed-level gaps are positive.
- **Under heavy `drop` (level 50), governance is not reliably different from the open metadata filter:** matched-coverage risk A 0.748 vs 0.733 and A2 0.744 vs 0.736 (differences of +0.015 and +0.008, in the filter's favour); per-seed gaps for A vs the open filter are +0.001, -0.057 and +0.018 (mean -0.013), so even the sign is unstable. Against the closed filter, A and A2 are lower in 2 of 3 and 3 of 3 seeds respectively.
- **The registered rule returns FALSE** because it requires every cell to be strictly lower. This is reported as written, not as "failed" and not as "mostly passed".

# Scope statement: what this benchmark can and cannot say (read first)
- **G1 is not evaluable.** It needs at least 3 sources per failure class on held-out data and at least 20 eligible cases. This benchmark has 2 sources (S1 Kubernetes docs, S2 PostgreSQL docs), and the wrong-version class has only those 2 versioned sources, so it is **inconclusive by construction**. The planned held-out run therefore tests the benchmark's own claims on a separate split; it is **not** a G1 verdict and will not be reported as one.
- All case expectations are scripted from the same version/date metadata that the metadata filter uses, so F1 and F3 cannot separate filtering from governance on clean metadata. F2's gold is policy-defined. Approval state and ACLs are simulated. Queries are derived from gold pages.
- Nothing here is evidence of production readiness, security assurance, compliance, practitioner demand or commercial value. Whether incumbent systems lack these behaviours is untested and needs the Amendment 10 inbound channel.

---
# Held-out run (single run; Amendments 6.4, 7, 11, 11a, 11b)
Run once on pipeline digest `8a12b347d7b8422a…` (published in the hash gist before the run: https://gist.github.com/TheIndicSentinel/f0a0c00f0c1df4e2c4c6a945841887a8), command `python3 -I src/urag/public_eval.py --split heldout --confirm-frozen --query-style lead`, arms A, N1, N0, N1P(open), N1P-closed; claim and log written before evaluation (`results/HELDOUT_RUNS.log`, lock `results/HELDOUT_LOCK_8a12b347d7b8422a`). Output: `results/public_S1-S2_heldout_lead.json`. 423 held-out cases (S1 294, S2 129), clean metadata, `lead` queries, strict taxonomy. Clusters: 66-68 per family (F4: 20).

**Scope first: G1 is not evaluable** (2 sources; wrong-version inconclusive by construction). The numbers below are descriptive results of the benchmark's own held-out split, not a G1 verdict.

## Results (fail rate / critical / abstained / wrong_doc)
| Family (n) | N1 | N1P (= N1P-closed) | A | A - N1 failure, 95% cluster CI |
|---|---|---|---|---|
| F1 wrong-version (135) | .84 / 48 / 0 / 65 | .20 / 0 / 0 / 27 | .81 / 0 / 100 / 10 | -0.022 [-0.119, +0.082] |
| F2 stale / not-yet-effective (134) | .78 / 45 / 0 / 60 | .69 / 24 / 0 / 68 | .87 / 0 / 112 / 5 | +0.090 [-0.007, +0.197] |
| F3 ACL exposure (131) | .80 / 49 / 0 / 56 | .22 / 0 / 0 / 29 | .76 / 0 / 91 / 9 | -0.038 [-0.129, +0.061] |
| F4 constructed abstention (23) | 1.00 / 8 / 0 / 15 | 1.00 / 0 / 0 / 23 | .65 / 0 / 0 / 15 | -0.348 [-0.565, -0.167] |

Overall critical failures over 423 cases: N0 152, N1 150, N1P 24 (all F2), N1P-closed 24, **A 0**.
Supplementary paired contrasts (not registered; same bootstrap): A minus N1P failure rate F1 +0.61 [0.50, 0.75], F2 +0.19 [0.08, 0.30], F3 +0.54 [0.44, 0.66], F4 -0.35 [-0.57, -0.17].

## What the held-out data says (plainly)
1. **Arm A produced zero critical failures in 423 cases**, against 150 for ACL-filtered top-1 retrieval (35% of cases). That safety effect replicates from dev.
2. **A is not more accurate than N1 overall.** On strict failure rate the interval includes zero for F1, F2 and F3; in F2 the point estimate is worse. A's silence is the mechanism: it abstained in 100/135, 112/134 and 91/131 cases, mostly because the frozen `conflict` rule treats several eligible distinct pages as a conflict (recorded as a flaw of arm A).
3. **A plain metadata filter dominates A on clean metadata for wrong-version and ACL cases:** failure 0.20 / 0.22 versus A's 0.81 / 0.76, with 0 critical failures. This is partly by construction (the expectations come from the same fields the filter uses), but it means the governance layer, as built, adds no accuracy over a version/window pre-filter when metadata is clean.
4. **F2 is where a rule matters:** the filter has 24 critical failures (an older supported revision presented as current) and A has none, but A answers in only about 16% of F2 cases.
5. **Per source:** S2 shows A worse than N1 (failure 0.95-0.98 against 0.71-0.83) while still having 0 critical failures versus 56 for N1 across S2 F1-F3.
6. **F4 is the only family where A's failure interval excludes zero** (-0.35), but it is the constructed (synthetic) family and not a working sufficiency check. Of A's 8 correct F4 outcomes, 4 came with a `conflicting_evidence` status (the conflict rule) and 4 with status `ok` and no applicable document. A correct F4 abstention is scored `correct`, which is why the abstained column shows 0 for F4.

## Not claimed
Not G1. Not practitioner demand, production readiness, security assurance, compliance or commercial value. The benchmark compares rule behaviour on public documentation under scripted expectations; it says nothing about whether incumbent products lack these behaviours.


---
# Prevalence caveat and threats to validity (read with every headline number)

## Prevalence: what the 0.78-0.84 means and does not mean
The N1 failure rates (about 0.78-0.84 on held-out) are for a **version-blind BM25 retriever over an index that holds every release of each page** (5-7 versions), asked a title- or lead-sentence-derived query. They also count any outcome other than the gold document, including plain retrieval misses (gold is in the top 10 about 82% of the time). A deployment that indexes one version, or filters by version and date, would see far lower rates of the wrong-version and stale classes: the N1P control (a plain metadata filter) shows 0.20-0.22 on the wrong-version and ACL families. Treat the headline as **the cost of not filtering on metadata**, not as a typical production rate. This benchmark does not measure how often real systems do not filter.

## Threats to validity
1. **Scripted expectations share the filter's fields.** Gold is derived from the same version and date metadata that the metadata filter uses, so wrong-version (F1) and ACL (F3) cannot separate filtering from governance on clean metadata. F2's gold is policy-defined ("latest revision effective at T").
2. **Simulated state.** ACLs are seeded overlays and `approval_state` is `approved` for every document, so the authority check is never exercised by public data (corrupting `approval_state` is a no-op in G2).
3. **Queries are derived from the gold page** (title or first sentences), which favours retrieval of the gold page.
4. **Document-level granularity.** No chunking or passage evidence; "relied upon" means "the document was named".
5. **Two sources, both unusually clean.** Both are version-controlled documentation with explicit release structure. The wrong-version class has only these two sources; the registered minimum is three.
6. **Held-out is not independent of dev.** It comes from the same generator and sources, split by path cluster rather than by source (Amendment 1.2). Style of source is shared across splits.
7. **Single retriever and k.** BM25 with an OR query, k=10. No dense, hybrid or reranking arm was run; absolute failure rates are driven by this retriever.
8. **Design decided partly after seeing results.** Disclosed: N1P and A2 were added after seeing dev results; arms A2/AP/A2P/A-S were selected after the first dev run; G2 first ran with the wrong query style (Amendment 12); the F1 generator was redesigned after the first dev run (Amendment 5).
9. **Small effective sample.** 66-68 clusters per family on held-out (20 for the constructed family), 3 seeds for G2, and the matched-coverage rule has no registered interval.
10. **Not tested against incumbents.** Whether existing products already filter by version, date or access is unknown here and needs practitioner input.

---
# S4 (Django docs) confirmatory test: expectations written BEFORE any held-out output exists
Written 2026-10-15 after `949eadf` was public and before the held-out run. **These expectations were written after the S4 dev sanity output had been seen (it is public in `949eadf`); they are not blind to dev.** They are blind to held-out: no held-out output of any arm exists. Registered in Amendments 13, 13a, 13b, 13c. Pipeline digest to be used: `f071b9247239874ac10582f5eafafc23337c3549988f26f855f795eab84f54ec`.

**Label:** confirmatory test of post-hoc arms on a single source. Not G1. Not a platform decision. Not an IT-operations corpus. It cannot change the project's direction (the platform thesis was dropped by Amendment 9.2 / D26).

## What this test can and cannot show
1. **F1 and F3 cannot show a critical-failure reduction.** The metadata filter (N1P) already has zero critical failures there by construction, because expectations are scripted from the same version and window fields the filter uses. In F1 and F3 the test can only show **no harm** (non-inferiority) or **harm** (Amendment 13b.2 allows 'Falsified' there when the interval lower bound is above 0).
2. **F2 is the only family that can show a benefit,** and its gold is policy-defined ("latest revision effective at T"). A "Supported" verdict means "the lineage policy removes the critical failures the filter has, without hurting overall"; it does not mean users want that policy.
3. **F4 is inconclusive by registration:** 13 held-out cases and 13 clusters, below the floor of 20 and 15. It is reported but not used.
4. **The dev sanity run is not evidence** and is not quoted as such. It only confirms the pipeline runs on the new source. No rule, arm or threshold was changed after seeing it.
5. **One source, 50-51 cases and 38 clusters per family:** intervals will be wide; "Not supported" from imprecision is a likely and acceptable outcome.

## Pre-stated expectations (so they cannot be adjusted afterwards)
- I expect A2P and N1P to have similar failure rates in F1 and F3, and A2P to have fewer critical failures than N1P in F2, because the lineage rule is the only difference that matters. Whether the intervals are narrow enough to call that "Supported" is open.
- I expect A (frozen, with the conflict rule) to abstain in most cases and to look worse than N1P on failure rate, as in S1 and S2. That is context, not the test.
- A result of "Not supported" or "Inconclusive" will be reported with the same prominence as "Supported".

## What would change nothing
Whatever the outcome, no arm, rule, threshold or sample will be altered and re-run on S4 held-out. Any further use of S4 held-out is exploratory under a new digest and amendment (D31).

---
# S4 (Django docs) confirmatory test: held-out result (single run, digest f071b924…54ec)
Run once, claimed before evaluation (`results/HELDOUT_RUNS.log`, lock `results/HELDOUT_LOCK_f071b9247239874a`), exact command `python3 -I src/urag/public_eval.py --split heldout --confirm-frozen --query-style lead --sources S4`. Output: `results/public_S4_heldout_lead.json`. 165 held-out cases, `lead` queries, clean metadata, strict taxonomy, arms N0, N1, N1P(open), N1P-closed, A, AP, A2P. Decision rule: Amendments 13 and 13b (13b governs over the Amendment 13 "Falsified" bullet).

## Registered limits, restated next to the result
1. **Label:** confirmatory test of post-hoc arms on **a single source**. Not G1. Not a platform decision. Not an IT-operations corpus.
2. **F1 and F3 cannot show a critical-failure reduction** (the metadata filter has none there by construction). They can only show no harm, or harm.
3. **F2's gold is policy-defined** ("latest revision effective at T"). The arm that implements that policy is rewarded by the definition of the gold.
4. **F4 is below the registered floor** (13 cases, 13 clusters; floor 20 and 15) and is **inconclusive** by registration.
5. Expectations were written after the S4 dev sanity output had been seen (not blind to dev); they were blind to held-out.

## Results (fail rate / critical / unanswered / wrong_doc)
| Family (n, clusters) | N1 | N1P (open = closed) | A | AP | A2P |
|---|---|---|---|---|---|
| F1 wrong-version (51, 38) | .73 / 18 / 0 / 19 | .10 / 0 / 0 / 5 | .96 / 0 / 49 / 0 | 1.00 / 0 / 51 / 0 | .10 / 0 / 0 / 5 |
| F2 stale / not-yet-effective (51, 38) | .78 / 21 / 0 / 19 | .59 / 10 / 0 / 20 | 1.00 / 0 / 51 / 0 | 1.00 / 0 / 51 / 0 | .10 / 0 / 0 / 5 |
| F3 ACL exposure (50, 38) | .78 / 15 / 0 / 24 | .10 / 0 / 0 / 5 | .98 / 0 / 49 / 0 | 1.00 / 0 / 50 / 0 | .10 / 0 / 0 / 5 |
| F4 constructed (13, 13), inconclusive | 1.00 / 6 / 0 / 7 | 1.00 / 0 / 0 / 13 | .69 / 0 / 0 / 9 | .00 / 0 / 0 / 0 | 1.00 / 0 / 0 / 13 |

## Registered primary contrast, A2P minus N1P (paired, two-sided 95% cluster bootstrap, 2000 resamples, seed 20261018)
| Family | failure-rate difference | CI | critical-indicator difference | CI |
|---|---|---|---|---|
| F1 | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] |
| **F2** | **-0.490** | **[-0.614, -0.352]** | **-0.196** | **[-0.298, -0.089]** |
| F3 | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] |
| F4 (not used) | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] |

## Applying the rule exactly as registered
- **Floor (13b.1):** F1, F2, F3 meet it; F4 is below it (inconclusive).
- **Falsified (13b.2)** requires a CI *lower* bound above 0 for the failure rate (F1-F3) or the F2 critical indicator: F1 lower bound 0.000, F2 -0.614 and -0.298, F3 0.000. **Not falsified.**
- **Supported (13)** requires the F2 critical-indicator CI upper bound below 0 (**-0.089, met**) and failure-rate CI upper bound below +0.05 in F1, F2, F3 (**0.000, -0.352, 0.000, met**).
- **Per-family conditions of the hypothesis are all met.**
- **Overall verdict (13b.4): Supported on F1-F3 (per-family reading); Inconclusive under a literal 13b.4 reading.** Both labels stand with equal prominence, and the reading difference is as follows: 13b.4 also says "Inconclusive if any family is below the floor and none is falsified". Read literally with F4 counted as "any family", the overall label would be Inconclusive. The hypothesis and the decision rule concern F1-F3 (Amendment 13 items 3-4), and the pre-run note (item 3) fixed before the run that F4 is "reported but not used"; this reading is the one applied here. The wording of 13b.4 is ambiguous on this point and is recorded as such; a literal-reading label of **Inconclusive** is the alternative and is stated here so it is not silently dropped.

## Which criterion was met in each family (explicit)
| Family | Floor | Critical-failure reduction vs the filter | Non-inferiority (failure-rate CI upper bound < +0.05) | What this means |
|---|---|---|---|---|
| F1 wrong-version | met | **Not applicable and not claimed**: N1P has 0 critical failures, A2P has 0 | met (0.000) | outcomes identical on every case; no harm, no benefit possible by construction |
| F2 stale / not-yet-effective | met | **Met**: CI upper bound -0.089 (10 of 51 for N1P, 0 for A2P) | met (-0.352) | the only family with a benefit, and its gold is defined by the policy A2P implements |
| F3 ACL exposure | met | **Not applicable and not claimed**: both 0 | met (0.000) | identical outcomes; no harm, no benefit possible |
| F4 constructed | **below** (13 cases / 13 clusters) | not assessed | not assessed | inconclusive by registration |

## What this does and does not mean
1. **The entire effect is F2, and it is the policy.** In F1 and F3 A2P and N1P have identical outcomes on every case (interval [0, 0]): no harm, and no benefit possible by construction. In F2 the filter presents a listed older or newer revision as the answer in 10 of 51 cases (critical) and answers a document that is neither the gold nor a listed distractor in 20 more (`wrong_doc`; not classified further), while A2P, which implements the "latest effective revision" lineage rule, does not. Because F2's gold is *defined* by that rule, this shows the rule behaves as specified, not that it is what users want.
2. **A and AP are not competitive here:** they leave 96-100% of F1-F3 cases unanswered because the frozen conflict rule treats several eligible distinct pages as a conflict. This replicates S1 and S2. They have no critical failures, but they answer almost nothing.
3. **Plain top-1 retrieval (N1) again has a high critical-failure share** (15-21 of ~50 per family: 30-41%), the cost of not filtering on version and date in an index holding five releases.
4. **A2P still fails about 10% of F1-F3 cases** (5 of 51, 5 of 51 and 5 of 50), all `wrong_doc`: retrieval misses rather than governance decisions.
5. **No change to the project's direction.** This is a single-source confirmatory test; it neither makes G1 evaluable nor revives the platform thesis, and it is not evidence of demand, production readiness, security or commercial value.


---
# Supplementary (2026-10-16): equivalence sensitivity and gold-in-top-10, held-out, all arms
Computed from the existing held-out result files (no new run). Strict = any page other than the gold counts as a failure; equiv. = Amendment 4 sensitivity (same path, other version, change below the significance threshold counts as correct; not applied to constructed abstention). Gold in top-10 is for the unfiltered retriever shared by N1 and A (not recorded for the pre-filtered arms).

| Set / family (n, clusters) | N1 strict → equiv. | N1P strict → equiv. | A strict → equiv. | A2P strict → equiv. | Gold in top-10 |
|---|---|---|---|---|---|
| S1+S2 wrong-version (135, 68) | .84 → .57 | .20 → .20 | .81 → .81 | – | .82 |
| S1+S2 stale (134, 68) | .78 → .56 | .69 → .38 | .87 → .87 | – | .82 |
| S1+S2 ACL (131, 66) | .80 → .60 | .22 → .22 | .76 → .76 | – | .81 |
| S1+S2 constructed (23, 20; floor met) | 1.00 → 1.00 | 1.00 → 1.00 | .65 → .65 | – | 0 (gold removed) |
| S4 wrong-version (51, 38) | .72 → .45 | .10 → .10 | .96 → .96 | .10 → .10 | .96 |
| S4 stale (51, 38) | .78 → .51 | .59 → .29 | 1.00 → 1.00 | .10 → .10 | .96 |
| S4 ACL (50, 38) | .78 → .40 | .10 → .10 | .98 → .98 | .10 → .10 | .96 |
| S4 constructed (13, 13; **below floor**) | 1.00 → 1.00 | 1.00 → 1.00 | .69 → .69 | 1.00 → 1.00 | 0 (gold removed) |

Reading: critical-failure counts and the critical-indicator contrasts are unchanged by the sensitivity (a critical failure requires a significant-difference distractor). The failure-rate gaps in the stale/version-unspecified family **do** move, because the filter's strict failure rate contains near-identical versions: on S4 the A2P minus N1P failure difference becomes about -0.20 (N1P .588 to .294 against A2P .098), and on S1+S2 the A minus N1P gap becomes about +0.49 (strict +0.19). No registered verdict depends on the sensitivity: the S4 criteria are critical reduction and non-inferiority, both unchanged.

## Additional threats (added 2026-10-16)
11. **Short and untitled pages stay in the index.** 22.9% of Kubernetes files normalise to under 30 words and 9.1% have no title (extraction ledger in `SOURCES.md`); they cannot be gold but compete in retrieval. Left in deliberately: removing them would change the digest and the splits are spent.
12. **Dev and held-out are split by path cluster within each source**, not by source (Amendment 1.2); this is not source-level independence.
