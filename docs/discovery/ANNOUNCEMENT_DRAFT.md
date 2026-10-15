# Announcement draft (for the author to post; NOT posted by any tool)

Amendment 10: the G4 clock starts only when the repository is public with LICENSE and NOTICE **and** this is announced in at least one public venue. After posting, log venue, date and link in `PUBLICATION_LOG.md` (never who replied). Replies are logged as roles only, no contact details (Amendments 10, 10a).

## Short version (forum / social)
> I published a small pre-registered benchmark on a question I couldn't find measured: when a retriever returns the top-ranked page for an incident-style query over multi-version documentation, how often is it a page you shouldn't rely on (wrong version, superseded, not yet effective), and does rule-based governance help?
>
> Result (Kubernetes + PostgreSQL docs, 423 held-out cases, run once on a pre-published digest): ACL-filtered top-1 retrieval over an index holding every release picked a critical-error page in about a third of cases. That is the cost of *not* filtering by version and date, not a production rate. Governance had zero such failures, but mostly by abstaining; it was **not** more accurate, and a plain version/date metadata filter did better on clean metadata. On the dev split with degraded metadata, governance had lower risk than the filter at every level when values were corrupted, and was not reliably different from the filter under heavy dropped fields.
>
> A fresh-source check on Django docs (registered before ingestion): governance on top of the filter matched it on wrong-version and ACL cases and removed the filter's critical failures in the version-unspecified family, whose correct answer is defined by that same rule, so it shows the rule behaves as specified, not that users want it. One source, not a replication of the main study.
>
> It's largely a negative result for the idea I started with, published with the deviations and limits: https://github.com/TheIndicSentinel/urag-benchmark (write-up: docs/WRITEUP.md).
>
> What I'm missing is practitioner input: if a stale or wrong-version runbook or doc has bitten you during an incident, a short account (no names, nothing confidential) would help me judge whether this matters outside a benchmark.

## Things not to say
- Do not describe it as a product, a platform, or evidence of demand, security or compliance.
- Do not say governance "beats" filters; the held-out result says the opposite on clean metadata.
- Do not quote the critical-failure share without the version-blind-index caveat.
- Do not describe the Django result as replication or as showing a critical-failure reduction on wrong-version or ACL cases.
