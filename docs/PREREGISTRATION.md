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

### Amendment 3 (2026-10-14): version-unknown semantics, registered before arm A code or any run
Amendment 1.3 and the F2 expectations in `S1_cases.json` conflict. Resolution (a policy choice made before any arm output exists):
1. **Incident version absent:** arm A defaults to the revision whose effective window contains the incident time, and records `version_defaulted` in the applicability note. It is not silent. It supersedes the "flagged applicability-unknown" wording of 1.3 for the case where a unique in-window revision exists.
2. **F2 is policy-grounded, not externally grounded.** Gold under F2 = "latest revision effective at T" by documented policy; real teams may run older supported versions. F2 results therefore measure lifecycle handling under that policy, not user intent. Reported with this label.
3. **Cross-path ambiguity:** if two or more different documents are simultaneously current and applicable, arm A reports `conflicting_evidence` (existing behaviour); this will be counted as a non-correct outcome for F1-F3 and is expected to cost coverage on generic titles.
4. **Outcome taxonomy for public cases** (fixed now): `correct` (F1-F3: applicable == gold; F4: no applicable doc); `critical` (applicable is a listed distractor under its relation; or a forbidden restricted doc appears anywhere in output); `abstained` (no applicable doc where gold expected; counted as unnecessary abstention, not critical); `wrong_doc` (applicable is neither gold nor a listed distractor; non-critical failure). Failure = not `correct`.
5. **Retrieval speed cache** (index reuse for identical candidate sets) must not change results; verified by comparing cached and uncached outputs on a sample.

### Amendment 4 (2026-10-14): sensitivity metric and retrieval diagnostics, registered before the first full dev run
A 6-case dev smoke run and a 25-case dev retrieval check (no held-out data, no gate computation) showed that (a) gold path is in top-10 for 18/25 cases because ~7 near-identical versions per path crowd the slots, and (b) many N1 top-1 results are the same path at another version with insignificantly different text, which the strict taxonomy scores as `wrong_doc`.
1. The **strict taxonomy of Amendment 3.4 remains primary** for all gate computations.
2. Additionally report a **content-equivalent sensitivity** failure rate for F1-F3: an applicable document at the same path as gold whose change ratio to gold is below the registered significance threshold counts as correct. Not applied to F4. Reported beside the strict rate, never instead of it.
3. Report **retrieval diagnostics** per family and arm: gold retrieved in top-10, any same-path document retrieved in top-10.
4. **Not changed:** arm definitions, k, query construction. A version pre-filter on retrieval would likely raise recall for arm A but changes the arm contract; it is a candidate Phase 5 variant and requires its own amendment and a matching N1 control.

### Amendment 5 (2026-10-14): support windows and F1 redesign, registered before regeneration
Finding (RESULTS_PUBLIC.md): in v1 cases F1 and F2 coincide, because ticket time T was sampled inside the gold version's own release-to-next-release span. Ablating `applicability` or `lifecycle` changed nothing in F1. Held-out cases were generated from the same flawed design and **have not been run**; the v1 cases are superseded and not used for any gate.
1. **Support windows.** For versioned documentation, `effective_to` = `effective_from` of the version `support_versions` releases later (S1: 3, S2: 5), capped at the retrieval date. Several versions are therefore effective at once. Config v2.
2. **Lineage rule (arm A, lifecycle check).** When the incident version is absent and several in-window documents share a lineage (same path), only the newest by `effective_from` is current; older ones are reported as superseded. This replaces the single-window reading in Amendment 3.1. Disabled by ablating `lifecycle`.
3. **F1 redesign.** Ticket version is an older supported version u; T is sampled after u+1's release and before u's end of support. Gold = page at u. The latest version at T is a distractor that the lifecycle check alone would choose. F1 now needs `applicability`; F2 needs `lifecycle`.
4. **Disclosure.** I had seen v1 dev results (including ablation tables) when designing this; no held-out output has been seen. Regeneration changes both splits. Splits are re-derived by the same seeded cluster hash, so cluster assignment is unchanged.
5. **No threshold, seed, dedupe, or arm-semantics change.** Outcome taxonomy (Amendments 3.4, 4) is unchanged.

### Amendment 6 (2026-10-14): two variants and a metadata-filter control, registered before their code
Motivation (dev S1+S2 results, `docs/RESULTS_PUBLIC.md`): arm A treats several simultaneously eligible, *distinct* documents as a conflict and abstains (S2 F2: 29/29 conflict abstentions; S2 A failure 0.93-1.00 vs N1 0.72-0.90). Disabling `conflict` cut A's failure to 0.42-0.50. This is a design limitation of the conflict rule on document corpora, not evidence against safety. The variants below are **chosen after seeing dev results** (disclosed); they are evaluated on dev and a single variant may then be carried to the one held-out run.
1. **A2 (`ranked_alternatives`)**. In versioned-document corpora (where `lineage` is defined), if more than one current, applicable document remains and all have distinct lineages, report the top-ranked as applicable and list the others as `alternatives`; `conflicting_evidence` is reserved for >=2 eligible documents sharing a lineage that the lineage rule cannot order. Corpora without `lineage` (legacy runbooks) keep legacy conflict behaviour, so the frozen contract is unchanged.
2. **Metadata pre-filter (`meta_prefilter`)** applied *before ranking*: keep only documents whose effective window contains the incident time and, if the ticket carries a version, whose version equals it. No other governance logic. Run on **both** sides as matched controls:
   - `N1P` = N1 + meta_prefilter (ACL + metadata filter, no governance decisions, top-ranked output).
   - `AP` = A + meta_prefilter; `A2P` = A2 + meta_prefilter.
3. **Contrasts reported (dev):** A-N1 (registered), A2-N1, AP-N1P, A2P-N1P. **Falsification reading:** if `N1P` is not materially worse than `A2P` on critical failures and failure rate, the governance layer's incremental value over a metadata filter is not demonstrated; this is reported as such.
4. **Held-out discipline:** variants may not be selected using held-out output. Exactly one variant (the dev-best by critical failures then failure rate, ties to the simpler) is run on held-out together with registered arms A, N1, N0, N1P.
5. Arms N0/N1/A semantics are unchanged; variants are additional named configurations, not edits to frozen arms.

### Amendment 7 (2026-10-14): G2 procedure and fail-open/fail-closed controls, registered before G2 code
Responds to review: G2 outcomes depend on how a metadata filter treats missing fields, so both defaults are registered and compared.
1. **Controls.** `N1P-open`: pre-filter keeps a document whose version or window bounds are missing. `N1P-closed`: drops a document with a missing `version` when the ticket version is known, or with a missing `effective_from`. (`N1P` in Amendment 6 = `N1P-open`.) Neither emits flags; any error is silent by construction.
2. **Arm A under missing metadata (registered semantics):** missing document `version` -> applicability-unknown flag (existing); missing `effective_from` -> flagged "lifecycle unknown", not current; missing `effective_to` is treated as open-ended (a dropped end date is **indistinguishable** from an open-ended document: stated limitation); missing `approval_state` -> excluded (existing fail-closed).
3. **Degradation.** Per the config: levels 0/10/25/50%, seeds 11/12/13, fields `version, effective_from, effective_to, approval_state` (service is single-valued per corpus and is not degraded: limitation), modes `drop` and `corrupt` (replace with another value present for that field in the same corpus), applied to documents and to ticket `version` independently, per (record, field) with probability k.
4. **Arms in G2:** N1, N1P-open, N1P-closed, A, A2 (and A2 with prefilter is not run). 
5. **Metrics.** Coverage (answered); critical rate; wrong_doc rate; correct rate; **silent error** = wrong_doc or critical outcome with no applicability flag and status `ok`; **flagged error** = abstained or flagged. **Matched-coverage risk:** risk of the higher-coverage arm recomputed after seeded random abstention down to the lower arm's coverage (100 draws, mean reported). Results are means over seeds with per-seed values kept.
6. **Reading rule (fixed now).** G2 favours governance only if, at matched coverage and under both `drop` and `corrupt`, A or A2 shows a lower critical+wrong risk than **both** N1P-open and N1P-closed. If A merely flags what the filters silently drop, that is reported as "flagging, not accuracy". Corrupted values are undetectable by every arm; that is expected and reported.

### Amendment 8 (2026-10-14): sufficiency definition, query style, F4 correction; registered before code
1. **Sufficiency (mechanical).** Let Q be the query's content tokens (lowercase alphanumerics, length >= 3, minus the pipeline stopword list). For an eligible candidate d, `cov(d) = |Q ∩ tokens(title + body of d)| / |Q|`. Candidates with `cov < 0.70` are removed after eligibility; if none remain arm A reports `insufficient_evidence`. Threshold fixed a priori at 0.70; not tuned. Implemented as a variant flag `relevance_floor` (so legacy arms are unchanged) and reported as arms `A-S`, `A2-S`.
2. **Known weakness (stated before measuring).** With title-derived queries every page that contains the title words passes, and gold is derived from the same title: sufficiency is nearly tautological there. Therefore a second **query style** is registered: `lead` = the first 15 content words of the gold page's body (after title), run as an alternative factor on the *same* cases (no regeneration). Sufficiency results are reported only for `lead` as primary, `title` as secondary.
3. **If sufficiency cannot reduce F4 answered-wrong without a coverage loss larger than its F4 gain on dev, it is declared dropped** and the thesis is restated with four claims, not five. No post-hoc threshold search.
4. **F4 correction.** Twins are generated from F1 cases only (ticket version known: other versions are wrong-version, so abstention is unambiguous). F2-derived twins are removed because an older revision is a legitimate fallback under the lineage rule. F4 expectations of S1 and S2 are regenerated; F1-F3 cases are unchanged (checked by diff). No arm has been run on the regenerated F4; held-out remains unrun.
5. **Conflict rule.** Recorded as a scoping flaw of the frozen arm (RESULTS_PUBLIC.md). Not edited; A2 remains the variant.

### Amendment 9 (2026-10-14): primary query style, reframe rule, thesis wording; registered before G2 results are read and before held-out
Disclosure: both query styles' dev results (clean metadata) had been seen when this was written; G2 results had **not** been read (no G2 task had completed). The held-out split has not been run.
1. **Primary query style = `lead`; `title` secondary.** Rationale fixed by realism, not by performance: tickets are descriptive text, not page titles, and title queries are derived from the gold document's own title (more tautological). Both styles are reported; gate computations use `lead`. The dev-performance difference (gold@10 0.82-0.90 vs 0.57-0.64) is not the reason and must not be cited as one.
2. **Reframe rule (decided before G2 is read).** The G2 verdict of Amendment 7.6 is computed by `src/urag/public_g2_report.py` per arm (A, A2). If `favours_governance` is **false for both** A and A2, the project adopts the **benchmark-plus-policy framing**: the artifact is a published benchmark of eligibility-failure prevalence and a documented lifecycle/lineage policy; the evidence-governance-layer platform thesis is dropped, regardless of G1 or discovery enthusiasm. If it is true for either, the platform thesis stays open but still requires G1 (held-out, >=3 sources where applicable) and G4. A mixed picture (true only under one of `drop`/`corrupt`) is reported as such and counts as **false** for this rule.
3. **Thesis wording.** Claims that the benchmark can address: authorized, current (lifecycle/lineage under stated policy), applicable (service/version). `approved` rests on simulated state and has no external ground truth. **`Sufficient` is not demonstrated by any arm and is an open problem**; it is removed from the thesis wording and no further threshold work is done (Amendment 8.3 outcome: lexical floor not demonstrated).
4. **Conflict rule** is recorded as a scoping flaw of the frozen arm; arm A text is unchanged.
5. **Determinism.** G2 results must be independent of worker count, process, hash seed and cache size. Verified by running one task in two separate processes with different `PYTHONHASHSEED` and cache sizes and comparing digests; the digests are recorded in `docs/RESULTS_PUBLIC.md`. The running procedure is not changed.
6. **Incumbent claim.** Prevalence of N1 critical failure on this corpus is not evidence that real products lack version/lifecycle filtering; that is answerable only by practitioner conversations (G4).

### Amendment 10 (2026-10-14): G4 redefined for a solo author with no practitioner network; registered before any publication or announcement
Context: the author has no reachable practitioners to invite, so the stop rule of s5 ("8 invitations, 4 weeks, 0 conversations") can never start. G2 results had not been read when this was written.
1. **G4 (pull), as amended.** Passes if **>= 3 qualifying inbound replies** are received within **4 weeks of the publication date P**. Fails (stop rule fires) otherwise. **No outreach quotas** and no invitations are required or counted.
2. **Publication date P** = the date on which (a) the repository is public with LICENSE and NOTICE present, and (b) the benchmark has been announced in at least one public venue relevant to practitioners (venue and date logged in `docs/discovery/PUBLICATION_LOG.md`). The clock has **not started**.
3. **Qualifying reply.** A reply (issue, comment, message, email) counts only if it describes a specific recent incident or workflow and can be logged as at least one *fact* or *estimate* in the evidence log (`docs/discovery/evidence_log.template.csv` categories). Stars, likes, compliments and generic opinions about AI do not count. A reply that agrees to a follow-up conversation is run with `docs/discovery/INTERVIEW_GUIDE.md`.
4. **Strength of evidence, stated in advance.** Inbound replies are self-selected, are not a representative sample, are subject to publication bias, and cannot establish prevalence, willingness to pay, or that incumbent products lack the behaviours measured. A G4 pass supports only "some practitioners recognise the problem". It is **weaker evidence than interviews** and is reported as such.
5. **Consequence of failure.** If the stop rule fires, the project adopts the benchmark-plus-policy framing already provided for in Amendment 9.2; the platform thesis stays unsupported by practitioner evidence. G4 is not required for the benchmark-plus-policy artifact.
6. **Privacy.** Record roles, not names; no private messages are quoted without consent; real notes stay in git-ignored `*.local.*` files.
7. **Superseded text.** The invitation-count clause of s5 G4 and the stop rule in `docs/PLAN.md` ("8 invitations over 4 weeks") are superseded by this amendment for outreach counting; the 4-week duration is retained, measured from P.

### Amendment 10a (2026-10-14): clarifications to Amendment 10 (append-only; Amendment 10 text is unchanged)
1. **Wording.** Amendment 10's note that "G2 results had not been read" is restated precisely: the G2 sweep was in progress (some checkpoint files existed) and **no G2 output had been inspected or aggregated**.
2. **Contact details.** Email addresses, handles and other contact details of people who reply are **not recorded in tracked files**; local notes are deleted on request. `docs/discovery/PUBLICATION_LOG.md` records venue, date and link of announcements only, never who replied.
