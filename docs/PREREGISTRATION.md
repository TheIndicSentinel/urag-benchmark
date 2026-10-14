# Pre-registration v1 (Phase 0)

Registered before any public-data case is generated or any new arm is run. Status: **registered, unamended**. Changes go only in the Amendments section at the bottom, with date and reason; the text above is never edited after registration. Commit date of this file is the registration timestamp.

## 1. Question
Does governance-aware evidence selection (lifecycle, applicability, authority, conflict, sufficiency) reduce relied-upon-evidence failures compared with ACL-filtered retrieval, on publicly sourced corpora with externally defined ground truth?

## 2. Arms (same corpus, queries, retriever, k, scoring code)
| Check | N0 | N1 | A |
|---|---|---|---|
| BM25 retrieval (same index, same k) | yes | yes | yes |
| Authorization filter | no | yes | yes |
| Lifecycle (superseded/draft/effective window) | no | no | yes |
| Applicability (service/version/environment) | no | no | yes |
| Authority / approval state | no | no | yes |
| Conflict detection | no | no | yes |
| Sufficiency / abstention | no | no | yes |
| Output rule | top-ranked doc | top-ranked authorized doc | structured, flagged |

Ablations (A minus one check) are run on the same cases to attribute effect. No arm may see expected outputs. N0 and N1 must be implemented before any public case is generated and are frozen for the held-out run.

## 3. Failure classes and critical failures
Classes: stale-as-current, wrong-version/environment, unauthorized exposure, unresolved-conflict-resolved, causal-overclaim, insufficient-evidence-answered, unnecessary-abstention.
**Critical failures** (never averaged away): unauthorized content in output or citations; superseded/draft/out-of-window item presented as current guidance; wrong-version item presented as applicable when version is known; correlation asserted as cause.

## 4. Case generation and splits
- Expected behavior is scripted from source metadata and committed **before** any arm runs on that case. The implementer does not hand-write expected outputs for public-source cases.
- Splits are by **source first**, then by scenario family. Held-out sources are never used for tuning; looking at held-out results to motivate a change is logged as contamination and the affected cases are reclassified dev.
- Held-out is run once per frozen pipeline version. Any rerun is logged.
- Near-duplicates are detected (shingle similarity, threshold recorded when chosen, before generation). Per-template cap is recorded in the generator config. Effective sample size is reported per family, not raw count.
- The 14 existing hand-authored cases are regression only and are excluded from all gate computations.
- ACLs on public data are simulated with seeded, documented rules. Results cover policy-engine behavior only.

## 5. Gates
Minimum sample per failure class: **>= 20 eligible cases, from >= 3 sources, >= 2 scenario families**. Below this the class result is **inconclusive**, never pass.
- **G1 (value), per class, held-out only:** A's failure rate is lower than N1's and the 95% CI of the paired difference (cluster bootstrap by source) excludes zero, **and** A has zero critical failures on held-out. Any single critical failure in A fails G1 regardless of other results.
- **G2 (robustness):** under random metadata degradation (drop or corrupt k% of fields; k and seed fixed in advance by the generator config), A's additional errors must be flags/abstentions, not silent critical failures. Reported as a coverage-vs-risk curve, and compared at matched coverage.
- **G3 (generality):** a second public corpus runs using only configuration changes; report config lines vs core lines changed. Any core code change means G3 not passed for that corpus.
- **G4 (pull):** >= 3 completed practitioner conversations in 4 weeks, or the stop rule fires (8 invitations, 4 weeks, 0 conversations: change channel or reframe).
Also reported with every G1 result: prevalence (how often N1's top result is actually a failure on real corpora) and the A-N1 difference. A large delta with negligible prevalence is reported as low real-world significance.

## 6. What each outcome means
- G1 pass: governance adds measurable value on tested public corpora. Not evidence of production readiness, of effect in a customer's environment, or of willingness to pay.
- G1 fail or prevalence negligible: thesis weakened; reframe or stop.
- Inconclusive: collect more diverse sources or report as inconclusive; do not lower thresholds after seeing results.

## 7. Amendments
### Amendment 1 (2026-10-14): generator config and clarifications
Registered before any ingestion or generation. Nothing above this section was changed.
1. **Generator config.** `configs/generator.json` v1 fixes seeds, thresholds, families, dedupe, ACL simulation, degradation levels and the expected-inconclusive list.
2. **Split interpretation.** s4 (split by source) and s5 (>=3 sources per class on held-out) cannot both hold with 3 sources. Clusters within each source are assigned wholly to dev (30%) or held-out (70%) by seeded hash. This weakens independence from source style; reported as a limitation. Source-level bootstrap clustering for G1 is unchanged.
3. **Version semantics (to be implemented in arm A):** an incident carries an optional `version`. Document `version` known and incident `version` known and different: not applicable (critical if presented as applicable). Incident version unknown: version-scoped documents are flagged applicability-unknown, never silently chosen, and lifecycle (effective window as of the incident time) decides what is current. Documents effective_from after the incident time are out-of-window ("not yet effective").
4. **Arms N0/N1** remain frozen as specified in s2; neither gains version or lifecycle logic.
5. **Expected-inconclusive classes** are listed in the config. wrong-version has only two versioned sources (S1, S2) so it is expected to be **inconclusive** unless a third versioned source is registered by a further amendment before generation. Thresholds are not lowered.
6. **Known threat to validity** (also in config): query text is derived from the gold page title; the N1 gap on versioned corpora is partly by construction. Interpretation requires the reported prevalence and the ablations.

### Amendment 2 (2026-10-14): generator allocation and timezone, before any arm run
First S1 generation run (counts only, no arm executed, no expectations evaluated) showed (a) F1 consumed the whole deduped pool leaving F2 with 1 case and F3 with 0; (b) window timestamps used the local timezone. Corrections, made before any arm ran on these cases:
1. Each family draws an independent seeded sample (cap 150) from the same deduped pool; the same gold document may appear in different families (distinct failure classes, analysed separately). Within-class independence is unchanged.
2. All committer dates are converted to UTC.
These are generator implementation fixes and do not change thresholds, seeds, dedupe, splits or arm semantics. Seeing the counts is disclosed here.
