# Announcement draft (for the author to post; not posted by any tool)

Amendment 10: the G4 clock starts only when the repository is public with LICENSE and NOTICE **and** this is announced in at least one public venue. After posting, log venue, date and link in `PUBLICATION_LOG.md` (never who replied).

## Short version (forum / social)
> I published a small pre-registered benchmark on a question I couldn't find measured: when a retriever returns the top-ranked page for an incident-style query over multi-version documentation, how often is that page one you shouldn't rely on (wrong version, superseded, not yet effective, not authorised), and does rule-based governance help?
>
> Result on Kubernetes + PostgreSQL docs (423 held-out cases, run once on a pre-published digest): plain top-1 retrieval picked a critical-error page in about a third of cases; rule-based governance had zero, but mostly by abstaining. It was **not** more accurate than the baseline, and a plain version/date metadata filter did better on clean metadata. Under heavily degraded metadata governance was no longer reliably better than the filter.
>
> It's a negative result for the idea I started with, published with the deviations and limits. Repo (code, pre-registration with timestamped amendments, results): https://github.com/TheIndicSentinel/urag-benchmark
>
> What I'm missing is practitioner input: if you've been burned by a stale or wrong-version runbook or doc during an incident, a short account (no names, nothing confidential) would help me judge whether this matters outside a benchmark.

## Longer version (README-style post)
Same content plus: the question; the arms (top-1, ACL-filtered, governance, plain metadata filter); sources and what is simulated; headline numbers with the prevalence caveat ("the cost of not filtering, not a production rate"); what it does not show (G1 not evaluable, incumbents untested, queries derived from gold pages); the disclosed deviations (G2 first ran with the wrong query style; post-hoc arms); and the specific ask.

## Things not to say
- Do not describe it as a product, a platform, or evidence of demand, security or compliance.
- Do not describe governance as "beating" filters; the held-out result says the opposite on clean metadata.
- Do not quote the ~0.8 figure without the prevalence caveat.
