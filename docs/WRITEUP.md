# When top-ranked retrieval over versioned documentation is the wrong page, and what rule-based governance does about it

*Written for engineers building retrieval-augmented systems over versioned or lifecycle-managed documents (runbooks, product docs, policies). It summarises a pre-registered benchmark; all numbers are in [`RESULTS_PUBLIC.md`](RESULTS_PUBLIC.md), the registered design and its 13 numbered amendments in [`PREREGISTRATION.md`](PREREGISTRATION.md). This is a research artifact, not a product, and nothing here is evidence of production readiness, security assurance, compliance, practitioner demand or commercial value.*

## The limited result, first
- **Governance did not make answers more accurate.** On held-out data, a rule-based "governance" arm had no better failure rate than ACL-filtered top-1 retrieval (the intervals include zero), and it left most queries unanswered.
- **What it did do is remove the critical errors:** zero cases (out of 423 held-out) where it presented a wrong-version, superseded or not-yet-effective page as the answer, against 150 for ACL-filtered top-1 retrieval. It achieved that mostly by abstaining.
- **A plain metadata filter (restrict candidates by version and effective window *before* ranking) did better than the governance rules on clean metadata** for the wrong-version and ACL cases (failure 0.20 and 0.22 against 0.81 and 0.76), with no critical failures there.
- **The one place a *rule* changed outcomes on a fresh source, once the filter was already applied,** was the case where the query does not say which version it is about, and there the correct answer is *defined* by the rule ("latest revision effective at the incident time"). So that result shows the rule does what it says, not that it is what your users want.

If you take one thing from this (a reading of this benchmark, not a tested recommendation): filter by version and date before you rank, treat that as the baseline, and be sceptical of governance layers that cannot show they beat it.

## The question
When an analyst describes an incident and a retriever returns the top-ranked page, how often is that page one you should not rely on: the wrong version, a superseded revision, a revision that is not yet effective, or a document the principal may not see? And does adding explicit lifecycle, applicability and authority rules on top of retrieval fix it?

## What was measured
- **Corpora:** Kubernetes website docs (7 releases) and PostgreSQL docs (5 releases) for the main study; Django docs (5 releases) as a fresh confirmatory source. Cases are generated mechanically from version and date metadata, as pointers only; no third-party text is in the repository.
- **Arms (same index, same BM25 retriever, k=10):** N0 top-ranked; N1 top-ranked after ACL; A governance (ACL, lifecycle, applicability, authority, conflict, mechanical sufficiency floor, flags); N1P a version/window pre-filter plus ACL, no governance decisions; A2P governance on top of that filter with a conflict rule scoped by lineage.
- **Simulated:** ACLs (seeded overlays) and approval state (every document is `approved`).
- **Queries:** the page title, then the first sentences of the page (`lead`, the registered primary).

## Results
**1. Plain top-1 retrieval presents a critical-error page in about a third of cases in a version-blind index.** On the Kubernetes/PostgreSQL held-out data, ACL-filtered top-1 retrieval presented a wrong-version, superseded or not-yet-effective page (a *critical* error) in about 34-37% of cases (48/135, 45/134, 49/131); on Django 30-41% (18/51, 21/51, 15/50). That share is the honest headline: a critical error needs a listed distractor with significantly different text, so it is not an artefact of near-identical versions tying. The *strict* failure rate (any page other than the gold) was 0.78-0.84, but a large part of it is near-identical sibling versions returned instead of the gold; under the registered equivalence sensitivity it is **0.56-0.60** on Kubernetes/PostgreSQL and **0.40-0.51** on Django. The gold page is in the top-10 for 0.81-0.82 (K8s/PG) and 0.96 (Django) of cases for the unfiltered retriever; with title queries on dev it was 0.57-0.64, so absolute rates depend heavily on retrieval quality. **Caveat that matters:** this is a version-blind retriever over an index holding every release (5-7 versions of each page); a deployment that indexes one version, or filters by version and date, would see far less of it (the filter arm shows 0.20-0.22 on the wrong-version and ACL families). Read it as the cost of *not* filtering, not as a production rate.

**2. Governance trades answers for safety.** Zero critical failures, but it abstained in 100/135, 112/134 and 91/131 held-out cases (wrong-version, stale, ACL). A known flaw contributes: the frozen conflict rule treats several eligible *distinct* pages as a conflict, which over-abstains on documentation corpora.

**3. On clean metadata, a filter beats it.** See the limited result above. This is partly by construction (the expected answers come from the same fields the filter uses), which is why the wrong-version and ACL families cannot separate filtering from governance when metadata is clean.

**4. Under degraded metadata, the picture is mixed.** In a pre-registered sweep (dev split; fields dropped or corrupted at 10/25/50%), governance had lower matched-coverage risk than the filter when values were *corrupted* at every level (e.g. 0.40 versus 0.54 at 10%), and low silent-error rates when fields were *dropped* (0.7-4.5% against roughly 51-79% for the filters) because missing metadata is flagged. At the heaviest drop level its risk was not lower than the open filter's (0.748 versus 0.733). The registered rule, which requires every cell to win, returned **false**; a first run with the wrong query style returned true and both are published.

**5. A fresh source confirms only the policy.** On Django docs (registered before ingestion; 165 held-out cases), governance on top of the filter matched the filter in the wrong-version and ACL families (identical outcomes on every case) and removed all 10 critical failures of the filter in the version-unspecified family (failure 0.59 to 0.10; paired difference −0.49, CI [−0.61, −0.35]). Limits stated in advance: the first two families cannot show a critical-failure benefit by construction; the third family's gold is defined by the rule; one source; 50-51 cases per family. The overall label is "Supported on F1-F3 (per-family reading)" and "Inconclusive under a literal reading of Amendment 13b.4", both reported.

## What you might take from it (readings, not tested recommendations)
- **Filter by version and effective window before ranking.** It is cheap and was the strongest baseline here. Decide explicitly whether a missing field drops a document (fail closed) or keeps it (fail open); the two trade critical failures against wrong answers.
- **If queries often omit the version, make the default explicit.** "Latest effective revision" is a policy choice; it hurts teams on older supported releases. The lifecycle/lineage rules are written down in [`LIFECYCLE_POLICY.md`](LIFECYCLE_POLICY.md).
- **Flag unknown metadata instead of guessing,** and measure what that costs in coverage.
- **Do not equate "several eligible pages" with "conflict".** Distinct pages are not contradictory; detect contradiction on content, which this work did not do.
- **Measure with the prevalence caveat attached.** The headline failure rate depends mostly on whether your index is version-blind.

## Threats to validity
Expected answers share the filter's fields; one family's gold is policy-defined; ACLs and approval state are simulated; queries are derived from the gold page; documents are the unit (no passages); two main sources plus one confirmatory source, all unusually clean version-controlled documentation; held-out is split by path cluster *within* each source, not by source (Amendment 1.2), so dev and held-out share source style and this is not source-level independence; short and untitled pages (22.9% of Kubernetes files normalise to under 30 words; 9.1% have no title) were left in the index as a known retrieval-noise source; the constructed-abstention family meets the registered floor on Kubernetes/PostgreSQL (23 cases, 20 clusters) but not on Django (13 cases, 13 clusters); one retriever and k; arms A2, N1P and others were defined after seeing dev results; small cluster counts (about 38 to 68 per family); the registered minimum of three sources per failure class is not met, so the registered value gate (G1) is **not evaluable**. Full list: [`RESULTS_PUBLIC.md`](RESULTS_PUBLIC.md#prevalence-caveat-and-threats-to-validity-read-with-every-headline-number).

## What is untested
- **Incumbent products:** whether existing ITSM, search or assistant products already filter by version, date and access is unknown; this benchmark cannot say.
- **Practitioners:** there have been no conversations with people running incident or support operations. The inbound channel in Amendment 10 has not started.
- **Real tickets and real metadata quality:** queries are mechanically derived; real tickets are messier.
- **Generation:** no model produced an answer; the arms select and flag evidence only.
- **Sufficiency:** no arm demonstrated that retrieved evidence is *enough* to answer; the lexical floor did not work.

## Where further work would matter most
1. **Practitioner evidence.** The highest-value gap is whether people running incident or support operations recognise this problem and whether incumbent tools already filter by version, date and access. Retrieval work cannot supply that.
2. **Retrieval quality and granularity (v2 candidates, not fixes).** Hybrid or dense retrieval and passage-level evidence would raise gold-in-top-10 and allow passage citations, but passage-level evidence changes what "relied upon" means and invalidates the page-level gold, so it would be a new benchmark rather than a correction of this one.
3. **A corrected-rule replication on more sources** (the lineage-scoped conflict rule was confirmed on one source only).

## Process notes
The project began as a thesis for a governance platform; a rule registered in advance fired on the degraded-metadata result and the project became a benchmark with a documented policy. Deviations are disclosed (the first degradation sweep used the wrong query style; several arms were added after seeing dev results; one decision-rule clause was ambiguous). The held-out splits of S1/S2/S4 are spent: further use is exploratory and needs a new digest.

## Reproduce
`scripts/fetch_sources.py` rebuilds the pinned upstream extracts (verified against registered commit SHAs); `src/urag/gen/docs_gen.py` regenerates the cases; `tests/` and the runners are described in the README.
