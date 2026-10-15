# URAG: a pre-registered benchmark of "evidence eligibility" in retrieval

**One-line summary.** When a retriever returns the top-ranked page for an incident-style query, how often is that page one you should not rely on (wrong version, superseded, not yet effective, or not authorised), and does rule-based governance fix that?

**Short answer, on this benchmark:** the failures are common, and rule-based governance removes the *critical* ones, but it does so mostly by abstaining. It did **not** improve overall accuracy, and a plain version/window metadata filter did better than the governance rules on clean metadata. The only place a governance *rule* changed outcomes on fresh data, on top of the metadata filter, was the version-unspecified family, where the gold is defined by that same rule. See [Results](#results) and the [write-up](docs/WRITEUP.md).

This is a research artifact, not a product. Nothing here is evidence of production readiness, security assurance, compliance, practitioner demand or commercial value.

## What is in here
| Path | Contents |
|---|---|
| `docs/PREREGISTRATION.md` | The registered question, arms, gates, and 12+ dated amendments. Amendments are append-only. |
| `docs/RESULTS_PUBLIC.md` | Every result, including the deviations and negative findings |
| `docs/WRITEUP.md` | Narrative write-up for engineers building RAG over versioned documentation |
| `docs/LIFECYCLE_POLICY.md` | The lifecycle/lineage policy arm A implements |
| `docs/DECISIONS.md` | Decision and risk log |
| `configs/generator.json` | Registered seeds, thresholds and sources for case generation |
| `data/public/*_cases.json` | Generated cases: **pointers only** (source, path, version). No third-party text. |
| `src/urag/` | Reference implementation: arms N0/N1/A, generators, runners, report scripts |
| `results/` | Raw outputs, the G2 summaries, the held-out run record |
| `NOTICE`, `LICENSE` | Attribution of upstream sources; MIT for this repository's own material |

## The question and the arms
Same corpus, queries and retriever (SQLite FTS5 BM25, k=10) for every arm:
- **N0:** top-ranked result.
- **N1:** top-ranked result after ACL filtering.
- **A:** ACL, lifecycle (effective windows, lineage), applicability (service/version), authority, conflict and a mechanical sufficiency floor, with structured flags.
- **N1P:** N1 plus a metadata pre-filter (version and effective window). Added after seeing dev results, so it is a post-hoc control; it turned out to be the strongest baseline.

Sources: Kubernetes website docs (S1, release branches 1.30-1.36) and PostgreSQL docs (S2, REL_14-REL_18). Expected behaviour is scripted from version and date metadata, not hand-written. ACL and approval state are **simulated**.

## Results
Held-out split, run once on a pre-published pipeline digest (`8a12b347d7b8422a…`), 423 cases, clean metadata, descriptive only:

| Family | N1 fail / critical | plain metadata filter (N1P) | governance (A) | A minus N1, 95% CI |
|---|---|---|---|---|
| wrong-version (135) | .84 / 48 | .20 / 0 | .81 / 0 | -0.02 [-0.12, +0.08] |
| stale / not-yet-effective (134) | .78 / 45 | .69 / 24 | .87 / 0 | +0.09 [-0.01, +0.20] |
| ACL exposure (131) | .80 / 49 | .22 / 0 | .76 / 0 | -0.04 [-0.13, +0.06] |
| constructed abstention (23) | 1.00 / 8 | 1.00 / 0 | .65 / 0 | -0.35 [-0.57, -0.17] |

- **Governance (A) had 0 critical failures in 423 cases; plain top-1 retrieval (N1) had 150.**
- **A is not more accurate than N1** (intervals include zero in the first three families) and abstains in most cases; a known flaw in its conflict rule contributes.
- **A metadata pre-filter beats A on clean metadata** for wrong-version and ACL cases. This is partly by construction because expectations come from the same fields.
- **Under degraded metadata** (registered G2 sweep, dev split): governance clearly lowers risk at matched coverage when values are *corrupted*, and is not reliably different from the open metadata filter under heavy *drop*. The registered rule returns **FALSE** for the lead-style primary run (the title-style run, which ran by mistake first, returned TRUE; both are published).

> **Prevalence caveat.** The ~0.8 failure rate for plain top-1 retrieval is for a version-blind retriever over an index holding every release (5-7 versions per page). Deployments that index one version or filter by version and date would see far less of this; the plain metadata filter above gives 0.20-0.22. Read the headline as the cost of *not* filtering, not as a typical production rate. Full list of threats to validity: [docs/RESULTS_PUBLIC.md](docs/RESULTS_PUBLIC.md#prevalence-caveat-and-threats-to-validity-read-with-every-headline-number).

### Confirmatory test on a fresh source (Django docs, S4)
Registered before ingestion, run once on a pre-published digest (`f071b924…`), 165 held-out cases, label: **confirmatory test of post-hoc arms on a single source** (not G1, not a platform decision). Primary contrast: governance on top of the metadata filter (A2P) versus the filter alone (N1P).

| Family (cases) | Filter alone (N1P): fail / critical | Governance on filter (A2P): fail / critical | A2P − N1P failure, 95% CI | Criterion met |
|---|---|---|---|---|
| wrong-version (51) | .10 / 0 | .10 / 0 | 0.00 [0.00, 0.00] | non-inferiority only; identical outcomes |
| version-unspecified (51) | .59 / 10 | .10 / 0 | −0.49 [−0.61, −0.35] | critical reduction and non-inferiority |
| ACL exposure (50) | .10 / 0 | .10 / 0 | 0.00 [0.00, 0.00] | non-inferiority only; identical outcomes |
| constructed abstention (13) | – | – | – | below the registered floor: inconclusive |

Limits, registered in advance: the wrong-version and ACL families **cannot show a critical-failure reduction** (the filter already has none, by construction); the version-unspecified family's gold is **defined by the policy A2P implements**, so the result shows the rule behaves as specified, not that users want it; one source with 50–51 cases per family. Plain top-1 retrieval (N1) again had a 30–41% critical share, over an index holding five Django releases: **the cost of not filtering by version and date, not a production rate** (same prevalence caveat as above). The overall label is "Supported on F1–F3 (per-family reading)" and "Inconclusive under a literal reading of Amendment 13b.4"; both are stated in [`docs/RESULTS_PUBLIC.md`](docs/RESULTS_PUBLIC.md).

## What this does not show
- **G1 (the registered value gate) is not evaluable:** it needs at least 3 sources per class; there are 2, and wrong-version is inconclusive by construction.
- Whether incumbent products already do this is **untested**; the benchmark cannot answer it.
- Cases are mechanically generated from public docs and queries are derived from gold pages; real tickets differ.
- The held-out split is spent for this pipeline digest; any further use is exploratory and labelled so.

## Known limitations of the reference implementation
- An **absent** `approval_state` key raises an error in arm A (a `None` value is handled and excluded).
- The retrieval index cache is module-level state, mutated from the G2 runner.
- Dropping `effective_to` is indistinguishable from "open-ended", so metadata loss can *raise* confidence; no rule can detect corrupted values.
- The conflict rule treats several eligible distinct pages as a conflict (over-abstains on documentation corpora).
- Sufficiency is not demonstrated by any arm; the lexical floor does not separate an on-topic near-duplicate from the answer.
- Documents are the unit of evidence; no passage-level citations; BM25 with k=10 only.
See `docs/DECISIONS.md` (D20) and the [lifecycle/lineage policy](docs/LIFECYCLE_POLICY.md).

## Honest history
The project began as a thesis for a governed-evidence platform. The registered reframe rule fired on the G2 result, so the project is now **benchmark-plus-policy**: a published measurement of eligibility-failure prevalence and behaviour under degraded metadata, with a [documented lifecycle/lineage policy](docs/LIFECYCLE_POLICY.md) and a reference implementation. Deviations (for example, G2 first ran with the wrong query style) are disclosed in Amendment 12.

## Reproducing
The repository does not contain upstream documentation. Rebuild locally from the pinned refs in `configs/generator.json`:
1. `python3 -I scripts/fetch_sources.py --pg-mirror` creates blob-less clones under the git-ignored `.local_sources/` and extracts only the documentation trees, verifying every ref against the pinned SHAs in `configs/generator.json`. A fresh run was checked byte-for-byte against the extracts the committed cases were generated from (S1: 1,343-1,672 `.md` files per release; S2: 162-170 `.sgml` files per tag). Needs about 300 MB. `--pg-mirror` uses the GitHub mirror of PostgreSQL; the fetched tag commits are verified against the pinned SHAs either way.
2. `python3 -I src/urag/gen/docs_gen.py S1`, then `... S2`, regenerate the case files; `git diff --exit-code data/public/` should report no differences.
3. `python3 -I src/urag/public_eval.py --split dev --sources S1,S2 --query-style lead --variants` runs the dev arms.
4. `python3 -I src/urag/public_g2.py --query-style lead` then `python3 -I src/urag/public_g2_report.py --style lead` reproduces the degradation sweep.
5. `python3 -m unittest discover -s tests` runs the regression and digest tests.
Held-out: `public_eval.py --split heldout` is guarded by a pipeline digest and a lock file; it will refuse a second run.

## Feedback
Issues are welcome, particularly accounts of real incidents where a stale, wrong-version or inaccessible document caused trouble. Please do not post confidential information or contact details; keep reports at the level of what happened and what was needed. Replies that describe a specific recent incident are logged (roles only, no names) as part of the registered discovery procedure (Amendment 10).

## Licence and attribution
MIT for this repository's own code, configuration and documents (`LICENSE`). Upstream sources are credited in `NOTICE`; no third-party documentation text is included.
