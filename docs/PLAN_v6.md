# URAG Plan v6 (adopted; supersedes PLAN.md v4.1 scope)

## Thesis
Retrieval finds relevant text; URAG decides whether it may be relied on (authorized, current, approved, applicable, sufficient) and says so when it cannot decide. Evidence-governance layer for RAG, not another RAG platform. All claims are hypotheses until the gates in PREREGISTRATION.md pass.

## Positioning (hypotheses)
- First wedge: IT incident investigation (public data exists; failures concrete and measurable).
- Adjacent domains (versioned authoritative documents): untested; not marketed until G3.
- Alternatives: ITSM vendor AI, permission-aware enterprise search, generic RAG frameworks, manual work.
- Do not claim: compliance, enterprise security, production readiness, ROI.
- Commercial order: open benchmark -> paid bounded evaluation on a team's own sanitized data -> platform only if pull is shown.

## Decisions
Open benchmark + reference implementation first. Source/licence survey before building on any source. One config-only second-corpus test is the only "multi-industry" work. No registry service, connectors, UI, multi-agent, pack marketplace, pricing. Discovery planned for 0-2 reachable practitioners; gate is 3 conversations in 4 weeks.

## Architecture (target; build incrementally)
Governance is a pure decision function over (candidates, principal, context, policy) returning decisions with reasons, independent of retriever, index or model.
Sources -> connectors -> ingestion (passage spans) -> canonical evidence store (versions, lifecycle, ACL, provenance) -> derived rebuildable indexes (lexical, dense).
Query: principal+context -> authz filter -> hybrid retrieval (+rerank) -> governance engine -> evidence set + manifest -> optional constrained LLM -> validator -> release recheck + audit.
Extension contracts: connector protocol, policy pack (config), retriever interface, eval harness.
Scale path: now Python + SQLite FTS5 + flat/sqlite-vec + optional Ollama; next (if needed) Postgres+pgvector, workers; later (if measured) dedicated search, per-tenant isolation. Revocation, deletion consistency and tenant isolation are designed for, not claimed.

## Roadmap
| Phase | Work | Exit |
|---|---|---|
| 0 | Adopt plan; pre-register gates (PREREGISTRATION.md) | Registered and committed |
| 1 | N0/N1/ablation arms on existing runner; fix change-environment scoping via pre-registered case | Arms run on 14 regression cases (not evidence) |
| 2 | Source + licence survey; SOURCES.md; dedupe/diversity tooling | >= 2 usable sources, else smaller scope |
| 3 | Mechanical generator; commit expectations; dev run, held-out run once | G1 verdict per class |
| 4 | Metadata-degradation sweep | G2 |
| 5 | Hybrid + rerank arms; keep only what is measured to help | Retriever decision |
| 6 | Constrained local LLM, stronger validator, injection cases (only if A leaves a measured gap) | B vs A on critical failures |
| 7 | Second-corpus config-only test | G3 |
| 8 | Publish benchmark + write-up; continue/narrow/stop | Written decision |
Discovery runs in parallel from Phase 0 (interview guide, no pitch, log within 24h).

## Risks
A ~ N1 on held-out or negligible prevalence (reframe/stop); sources unusable (smaller benchmark); real metadata too poor (value shifts to metadata quality); no practitioner pull (stop rule); 8 GB hardware (drop LLM/rerank arms).


## Status note (2026-10-14, after Phase 2 dev results)
The surviving, benchmark-supportable claims are narrower than the thesis above: lifecycle/lineage policy, ACL and applicability behaviour. `Sufficient` is not demonstrated by any arm and is removed from the thesis wording (Amendment 9). A metadata filter (ACL + version/window) matches governance on clean metadata for wrong-version and ACL cases by construction; whether governance differs under degraded metadata is the registered G2 test. If G2 does not favour governance, the project adopts the benchmark-plus-policy framing (Amendment 9.2). Whether real incumbents lack these behaviours is not answerable by the benchmark; it needs practitioner conversations (G4), and none have taken place.


## Status note (2026-10-15): reframe rule fired
The lead-style G2 verdict (gate-relevant, Amendment 12) is **false** for both A and A2 (one cell, drop at level 50, where governance is not lower-risk than the open metadata filter at matched coverage). Under the pre-registered rule (Amendment 9.2) the project adopts the **benchmark-plus-policy framing**: the deliverable is a published benchmark of eligibility-failure prevalence and behaviour under degraded metadata, plus a documented lifecycle/lineage policy and a reference implementation. The platform thesis in the sections above is superseded and is not a goal. Practitioner evidence (G4) remains absent and is not required for this artifact.
