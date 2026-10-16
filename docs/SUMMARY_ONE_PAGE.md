# URAG in one page

**Question.** When a retriever returns the top-ranked page for an incident-style query over multi-version documentation, how often is it a page you should not rely on (wrong version, superseded, not yet effective, not authorised), and does rule-based "governance" help?

**What was done.** A pre-registered benchmark on Kubernetes, PostgreSQL and (as a fresh confirmatory source) Django documentation. Expected answers are scripted from version and date metadata. The repository holds pointers only, no third-party text. Held-out splits were each run once on a pre-published digest.

**Result.**
- **Plain top-1 retrieval, ACL-filtered, presented a critical-error page in about 35% of held-out cases** (150 of 423 on Kubernetes and PostgreSQL; 30-41% per family on Django), over an index holding every release. Governance had **zero**, mostly by abstaining.
- **Governance was not more accurate.** A plain version-and-date metadata filter applied before ranking did better on clean metadata (failure about .20 against about .8 for governance on wrong-version and ACL cases).
- Under degraded metadata, governance had lower risk than the filter when values were corrupted and was not reliably different under heavy dropped fields; the registered rule returned **false**.
- On Django, governance on top of the filter removed the filter's critical failures only in the version-unspecified family, whose correct answer is defined by that same rule.

**Read this with the limits.** The ~35% is the cost of not filtering by version and date, not a production rate. Expected answers share the filter's fields; ACLs and approval state are simulated; queries come from the gold page; documents (not passages) are the unit; one retriever. The registered value gate (G1) is **not evaluable** (two main sources). Whether real products already filter this way, and whether practitioners recognise the problem, is **untested**.

**Not claimed.** Production readiness, security assurance, compliance, practitioner demand, commercial value.

**Where to look.** `README.md` (results with caveats), `docs/WRITEUP.md` (narrative), `docs/LIFECYCLE_POLICY.md` (the rules), `docs/PREREGISTRATION.md` (design and 13 numbered amendments, 19 dated sections including the lettered ones), `docs/RESULTS_PUBLIC.md` (every number, including deviations).

**What would help.** A short, anonymised account of a stale, wrong-version or inaccessible document causing trouble during an incident.
