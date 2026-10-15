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

### Amendment 11 (2026-10-14): what "the same pipeline" means for the one-held-out-run rule; registered before the held-out run and before G2 was read
Gap found in review: the held-out guard keys "once per pipeline version" on `pipeline.py` and `public_eval.py` only. Case files, generator config and the generator could change without changing that key, which would allow a re-run on altered cases to look like a first run.
1. **Pipeline digest D.** SHA-256 over the sorted lines `<repo-relative path> <sha256 of file bytes>` for: `src/urag/pipeline.py`, `src/urag/public_eval.py`, `src/urag/gen/docs_gen.py`, `configs/generator.json`, and every `data/public/*_cases.json`. The held-out guard refuses a second run for the same D.
2. **Deliberately excluded from D:** `docs/PREREGISTRATION.md` and other docs (so adding an amendment cannot reset the guard), runner/report scripts for G2, and tests. The digest of `docs/PREREGISTRATION.md` and the git HEAD are **logged** with each run for audit, not used as the key.
3. **Log record.** Each held-out run appends one JSON line to `results/HELDOUT_RUNS.log`: UTC time, D, the per-file manifest, prereg digest, git HEAD, sources and arms run. The file is tracked and is committed immediately after the run.
4. **Pre-run publication.** `public_eval.py --print-pipeline-digest` prints D and the manifest without running anything. D is published (with the tag hashes) **before** the held-out run, so it can be shown that the run used the published pipeline.
5. **Rerun rule unchanged:** any rerun after a change to D is logged as an amendment stating why; a rerun motivated by having seen held-out output is contamination and reclassifies the affected cases as dev (s4).
6. **Scope.** Applies only to `public_eval.py --split heldout`. The G2 sweep, dev runs and legacy regression runs are unaffected. The G2 results that existed when this was written were produced by the previous guard-logging code; the code path that produces outcomes (`run_case`, pipeline) is unchanged by this amendment.

### Amendment 12 (2026-10-15): G2 was executed with title queries; disclosure and consequence. Written AFTER the title-style G2 result was read
1. **Deviation.** Amendment 9.1 fixed `lead` as the primary query style for gate computations. The G2 runner (`src/urag/public_g2.py:65`) passes `"title"`; it was written before Amendment 9 and I did not update it. The completed 36-task G2 sweep therefore used **title** queries. This was noticed at read time, not before.
2. **What was read.** The title-style G2 result was read once, mechanically, with `public_g2_report.py` (all 36 tasks validated first). Its registered verdict (Amendment 7.6 / 9.2) is `favours_governance = true` for both A and A2 under title queries.
3. **Consequence (stated now, before any lead-style G2 output exists).** The title-style result is **secondary**. The gate-relevant result is the **lead-style G2**, run with the identical procedure (levels, seeds, modes, arms, matched-coverage rule, reading rule). The reframe rule (9.2) is evaluated on the **lead-style** verdict. If the lead-style verdict is false for both A and A2, or mixed, the benchmark-plus-policy framing is adopted even though the title-style verdict was true. If it is true for A or A2, the platform thesis remains open (still subject to G1 and G4).
4. **Disclosed risk.** Having seen the title-style outcome creates a motivated-reading risk. It is mitigated only by the mechanical rule above and by publishing both verdicts regardless of agreement. No part of the rule, arms, thresholds or seeds changes for the lead-style run.
5. **Implementation.** The runner gains a `--query-style` option (default `title`, so existing checkpoints stay valid); lead-style checkpoints go to a separate directory; the report script selects the directory with `--style`. These files are outside the Amendment 11 digest.

### Amendment 11a (2026-10-15): hardening of the held-out guard; registered before the digest was published and before any held-out run
Found by the pre-push review (no held-out output exists; `results/HELDOUT_RUNS.log` does not exist). Changes to `src/urag/public_eval.py` (guard code only; `run_case` and the pipeline are unchanged):
1. **`--limit` is rejected for `--split heldout`.** A partial held-out run would reveal output and then block the full run for that digest.
2. **Claim before computing.** The run is claimed with an atomically created lock file `results/HELDOUT_LOCK_<digest16>` (exclusive create) and the log record is written **before** any evaluation. A crash after the claim consumes the run (a rerun needs an amendment): the conservative direction. Two simultaneous runs cannot both claim.
3. **Record the corpus snapshot.** The log record includes the SHA-256 of each `canon_<source>.pkl` cache used, so the run identifies which local corpus it read. These caches are not part of digest D (they are untracked); the record is informational.
4. **Consequence:** the digest D changes. The earlier printed digest `dae48c94…` is superseded; the current D is printed by `--print-pipeline-digest` and is the value to publish. Amendment 11.6's statement about G2 provenance is unchanged: G2 results came from earlier versions of guard code with identical outcome-producing code.

### Amendment 11b (2026-10-15): the held-out invocation is fixed, not caller-chosen; registered before the code and before any held-out run
Reason: the claim lock is keyed on digest D only, so a held-out invocation with the wrong flags would consume the single run.
1. **Fixed configuration for `--split heldout`:** query style `lead` (Amendment 9.1); arms exactly `A`, `N1`, `N0`, `N1P` (= N1P-open) and `N1P-closed` (Amendments 6.4, 7.1, 11); sources = every `data/public/*_cases.json` present. `--ablate`, `--variants`, `--limit` and a non-`lead` `--query-style` are rejected for held-out. The carried variant under Amendment 6.4 is arm A itself.
2. **Everything is computed before the claim** (digest, corpus cache hashes, prereg digest, git HEAD); the claim and the log append happen together, immediately before evaluation.
3. **The log record includes the full argument set** and the arm list actually run.
4. **Exploratory arms** (A2, A2P, A-S, A2-S, AP) are not run on held-out. If wanted later, that is a second, separately registered run on a new digest and is labelled exploratory.

### Amendment 13 (2026-10-15): confirmatory test of post-hoc arms on one fresh source (S4, Django docs); registered before any ingestion or generation
**Label (to be used everywhere it is reported):** *confirmatory test of post-hoc arms on a single source.* It is not G1, not a platform decision (that thesis was dropped by Amendment 9.2 / D26), not an IT-operations corpus, and cannot make G1 evaluable (the S1 and S2 held-out splits are spent for digest `8a12b347…`).
1. **Question.** Does governance on top of a version/window metadata filter (A2P) add anything over the filter alone (N1P) on a source no arm design has seen?
2. **Arms (frozen at this amendment; semantics exactly as registered in Amendments 5, 6, 7; no change to the corrected conflict rule, which is A2's `ranked_alternatives`):** N0, N1, N1P (open), N1P-closed, A, AP, A2P. **Primary contrast: A2P versus N1P.** AP, A, N0, N1 are context. Queries: `lead` (Amendment 9.1).
3. **Hypothesis H.** A2P has fewer critical failures than N1P in family F2 (version unspecified) **and** is not worse overall in F1, F2 and F3.
4. **Pre-stated decision rule, per family, on the held-out split of S4 only:**
   - **Supported:** F2 paired critical-failure indicator difference (A2P minus N1P) has a 95% cluster-bootstrap CI whose upper bound is below 0, **and** for F1, F2 and F3 the paired failure-rate difference (A2P minus N1P) has a CI upper bound below +0.05 (non-inferiority margin).
   - **Falsified:** F2 critical failures of A2P are greater than or equal to N1P's, **or** the failure-rate difference CI upper bound is at or above +0.05 in any of F1-F3.
   - **Inconclusive:** a family has fewer than **20 eligible held-out cases or fewer than 15 distinct clusters**, or the evidence is neither of the above.
   - Reported with it: coverage (answered share), critical-failure counts per arm, and matched-coverage risk (Amendment 7.5) as secondary.
5. **Known non-informativeness, stated in advance.** F1 and F3 expectations come from the same fields the filter uses, so N1P has no critical failures there by construction; only F2 can show a governance benefit, and its gold is policy-defined (Amendment 3.2). A "Supported" verdict therefore means "the lineage policy removes critical failures N1P has, without hurting overall", nothing more.
6. **Source and parsing.** S4 pins in `configs/generator.json` v3 (peeled release-tag commits 4.2, 5.0, 5.1, 5.2, 6.0). Documents: `docs/**/*.txt` excluding `docs/releases/` (version-specific by design). Windows: tag commit date; `support_versions = 3` is a convention. Title: first underlined heading. Dedupe, caps, significance thresholds, seeds and split fraction are those of config v2, unchanged. Clusters: first two path components under `docs/`; 30% dev / 70% held-out by the registered seeded hash.
7. **Held-out discipline.** Held-out claim lock as in Amendments 11/11a/11b: a new pipeline digest D2 (computed by Amendment 11's procedure over the manifest at run time) is published, with the tag hashes, **before** the run; a fixed invocation profile (sources **S4 only**, arms of item 2, `lead`, no `--limit/--ablate/--variants`) is implemented before the run; the claim lock and log record are written before evaluation; no held-out output is read before the single run. Dev cases are used for parser sanity only: no arm, threshold or rule may change after dev results are seen without a new amendment.
8. **Time-box.** If licence verification per file header, the rst parser, case generation and a dev sanity run are not complete by **2026-10-22**, the test is abandoned and recorded as **not performed**. No extension without an amendment.
9. **Order of events.** This amendment is pushed to the public repository before ingestion or generation begins, so the external timestamp precedes any S4 data handling.

### Amendment 13a (2026-10-15): spent sources are refused regardless of digest; registered before the held-out profile is implemented
Found immediately after Amendment 13: adding S4 to `configs/generator.json` changes the Amendment 11 digest, so the existing guard (keyed on digest) would accept a second held-out run of the **spent** S1 and S2 splits under the new digest.
1. **Rule.** A held-out run is refused if any source it would use already appears in a record of `results/HELDOUT_RUNS.log` (any digest). S1 and S2 are therefore permanently closed; only sources with no log record (S4) can be claimed.
2. **Profile.** The S4 confirmatory test uses a fixed profile: sources S4 only; arms N0, N1, N1P, N1P-closed, A, AP, A2P; `lead`; no `--limit/--ablate/--variants`. The Amendment 11b "all available sources" rule is replaced by "all sources without a prior record".
3. **Interim.** Until this is implemented, **no held-out run of any kind is to be started.**

### Amendment 13b (2026-10-15): precision of the Amendment 13 decision rule; registered before S4 ingestion, from the pre-push review
Clarifies Amendment 13 items 4 and 7. It **narrows 'Falsified'** (a result Amendment 13 would have called Falsified on imprecision alone becomes 'Not supported') and leaves 'Supported' unchanged; it is registered before any S4 data exists. No S4 data has been fetched.
1. **Precedence.** The sample floor is checked first and overrides everything: a family with fewer than 20 eligible held-out cases or fewer than 15 clusters is **inconclusive**, whatever its interval says.
2. **"Falsified" means evidence of harm; imprecision is "not supported".** Replace the three outcomes of item 4 by: **Supported** (as written); **Falsified** only if, in some family meeting the floor, the 95% CI *lower* bound of the paired difference A2P minus N1P is above 0 for the failure rate (F1-F3) or for the critical-failure indicator (F2); **Not supported** otherwise (including failure to show non-inferiority); **Inconclusive** by item 1. **Precedence: sample floor, then Falsified, then Supported, then Not supported** (so a result meeting both the non-inferiority bound and the harm condition is Falsified).
3. **Interval specification.** All intervals are two-sided 95% percentile cluster bootstraps over path clusters, paired by case, 2000 resamples, seed 20261018 (the registered bootstrap in `public_eval.py`). The "upper bound below +0.05" and "upper bound below 0" conditions use the upper end of that two-sided interval. The F2 critical-failure comparison uses the **paired per-case indicator difference**, not raw counts.
4. **Combination.** Per-family results are reported separately. The overall hypothesis is **Supported** only if all of F1, F2, F3 meet the floor and every condition of item 4 holds; **Falsified** if any family is falsified; **Inconclusive** if any family is below the floor and none is falsified; otherwise **Not supported**.
5. **Case visibility.** The generator writes `data/public/S4_cases.json` with dev and held-out cases (pointers and scripted expectations only; no arm output exists). It may be committed before the run, because the pipeline digest D2 covers it. Held-out cases are not to be run through any arm, and no arm behaviour on them is to be examined, before the single run.
6. **Pending before ingestion:** per-file licence-header verification for the Django `docs/` tree, recorded in `docs/SOURCES.md`.
7. **Held-out arm list** is fixed in code as N0, N1, N1P, N1P-closed, A, AP, A2P and is the list written to the log record (Amendment 13a).
8. **Paired critical-indicator CI** for the F2 criterion is computed in `summarize()` (key `<arm>_minus_<arm>_critical`) so that it is covered by the pipeline digest D2; no analysis step is left to analyst discretion.
9. **Permanent closure.** `SPENT_HELDOUT_SOURCES = {S1, S2}` is hard-coded in `public_eval.py`; the spent sources stay closed even if `results/HELDOUT_RUNS.log` is lost.

### Amendment 13c (2026-10-15): S4 file exclusions found during licence verification; registered before any S4 case generation
Per Amendment 13b.6, per-file licence verification was done on the five pinned Django trees (`docs/` only, fetched with `scripts/fetch_sources.py --sources S4`). Findings, all recorded in `configs/generator.json` (`licence_verification`) and `docs/SOURCES.md`:
1. `docs/_theme/djangodocs/static/fontawesome/LICENSE.txt` is a **third-party** licence file (Font Awesome Free: CC BY 4.0 / OFL / MIT) with a `.txt` extension that the registered glob would have ingested as a "document".
2. `docs/requirements.txt` is a pip requirements file, not a documentation page.
3. No documentation-specific licence statement exists in the docs tree; the repository `LICENSE` (BSD-3-Clause, no carve-out) applies. `LICENSE.python` sits at the repository root, outside `docs/`.
**Registered refinement of Amendment 13.6:** exclude `docs/releases/`, `docs/_theme/`, `docs/_ext/` and the file `docs/requirements.txt`. Nothing else changes. No cases had been generated and no arm had been run on any S4 data.
