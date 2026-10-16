# v2 candidates: planning document only (prepared 2026-10-16)

**Status:** planning and analysis. **Nothing here is started and nothing here changes D40** (no new arms, sources, runs or refactor unless the owner asks). No code is written and no run is made. Every candidate below needs a new pipeline digest and an amendment registered **before** its code or run, because the S1, S2 and S4 held-out splits are spent and the digest guard refuses them.

**Order of value, stated first.** The highest-value gap is practitioner evidence (G4): whether people running incident or support operations recognise the problem, and whether incumbent tools already filter by version, date and access. None of the candidates below can supply that, and none should start before the owner decides what G4 returned.

## Candidates
| # | Candidate | What it would test | Rough cost | A result that would change a decision | Why it needs a new digest and amendment |
|---|---|---|---|---|---|
| 1 | **Corrected-rule replication** (lineage-scoped conflict rule, A2/A2P) on additional fresh sources | Whether the version-unspecified benefit seen on one source (S4) repeats elsewhere | Small to medium: one adapter per source (as S4), licence verification, one registered held-out run each. Compute is light | A replication would justify publishing the lineage rule as a tested default for version-unspecified queries; a non-replication would limit or qualify the S4 reading (it would not by itself invalidate the S4 result) | New sources change `configs/generator.json` and the case files, hence the digest; S1/S2/S4 held-outs cannot be reused |
| 2 | **Hybrid or dense retrieval arm** | How much of every failure rate is retrieval quality (gold in top-10 was .57-.64 with title queries, .81-.96 with lead queries) | Medium to large on this hardware: an embedding model plus an index on an 8 GB machine that is often CPU- and swap-starved (G2 took hours under load); needs a licence-checked local model | If gold-in-top-10 rises and the critical share of plain top-1 retrieval falls, the "cost of not filtering" figure would be revised downward; contrasts between arms that share one retriever would keep their direction by construction, though their sizes could change | Changes `pipeline.py` / the runner (digest) and adds an arm; must be pre-registered as exploratory or confirmatory on a **fresh** source |
| 3 | **Passage-level evidence** (chunking, spans, passage citations) | Whether passage granularity changes eligibility errors and enables evidence-level citation | Large: new unit of evidence means new gold (passage-level), new generators and parsers, new metrics | It would produce a **new benchmark**, not a correction: page-level results cannot be compared directly | Different gold and unit; new digest and a new pre-registration from scratch |
| 4 | **More versioned sources** (to reach three per class) | Whether G1 becomes evaluable and whether results generalise across documentation styles | Medium per source (licence check, parser, generation, floors); only meaningful with fresh held-out sources | G1 could finally be reported per class (including wrong-version, inconclusive today); contradictory source behaviour would narrow the claims | Each source changes config and cases (digest); the held-out claim lock applies per source |
| 5 | **Governance-engine refactor** (D19: a pure `decide()` with a rule list, interfaces, a versioned policy file) | Nothing scientific: engineering reuse | Medium; needs output-equivalence checking on all regression and benchmark cases | Only if the code is meant to be reused: it would make ablations rule removal instead of flags; it cannot change any reported result | Edits digested files, so a new digest; kept as a separate package to leave the frozen reference implementation untouched |

## Dependencies and a suggested order if the owner ever asks
1. Decide from G4 whether any of this matters before spending effort.
2. Candidate 4 (sources) before 2 (retrieval): a fresh source is needed to confirm anything about a retrieval change anyway.
3. Candidate 1 can ride on candidate 4's sources.
4. Candidates 3 and 5 are separate projects, not extensions.

## Constraints that apply to all of them
- Pre-register (hypothesis, decision rule, minimum sample, time-box) before any ingestion or generation, and push the amendment so its timestamp precedes data handling.
- No claim stronger than the README; keep the "cost of not filtering" caveat attached to any prevalence figure.
- Licence verification per file header before ingesting a source; pointers only in the repository.
- No change to the registered Amendments above their sections, to the existing digests, or to the position of `v1.0-benchmark`.
