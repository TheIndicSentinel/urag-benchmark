# Decisions

| ID | Date | Decision | Status | Evidence | Next |
|---|---|---|---|---|---|
| D1 | 2026-10-14 | Stdlib Python + SQLite FTS5, unittest (pytest/ollama absent; avoid installs) | Proposed | FTS5 verified locally | Revisit if deps are warranted |
| D2 | 2026-10-14 | Authorization filters the candidate set before the FTS index is built per request | Validated (simulated only) | C2, fail-closed test | Add timing/score side-channel tests |
| D3 | 2026-10-14 | Change records are in scope; logs/metrics/CMDB excluded | Proposed | C3 needs change data | Revisit after interviews |
| D4 | 2026-10-14 | Unknown service/env => flagged, never authoritative | Proposed | C4 | Measure entity-resolution accuracy |
| D5 | 2026-10-14 | Wedge: open benchmark + reference implementation first; platform only if pull is shown | Proposed | Solo/free/no-data constraint | Phase 3 results, G4 |
| D6 | 2026-10-14 | Evidence base is public data with mechanically scripted ground truth, split by source | Proposed | PREREGISTRATION.md | Source/licence survey (Phase 2) |
| D7 | 2026-10-14 | Gates G1-G4 and minimum sample (>=20 cases, >=3 sources, >=2 families per class) fixed before expanded run | Registered | PREREGISTRATION.md | Commit; amend only via Amendments section |
| D8 | 2026-10-14 | "Multi-industry" limited to one config-only second-corpus test (G3); no pack framework | Proposed | PLAN_v6.md | Phase 7 |
| D9 | 2026-10-14 | Near-term scope cut: no registry service, connectors, UI, multi-agent | Proposed | PLAN_v6.md | Revisit after G1 |

# Risks
| Risk | Mitigation / test | Status |
|---|---|---|
| Self-authored cases are tautological | Independent + held-out cases (C5-C10) | open |
| Pipeline is too simple vs real metadata mess | Dirty-metadata corpus | open |
| Customer demand unvalidated | Interviews start now | open |
| 8 GB RAM limits local LLM | Small quantized model; B optional | open |
| Always-abstain passes safety | Coverage-vs-risk gate | open |
| N1 fails lifecycle cases by construction, so delta alone is tautological | Report prevalence on real corpora with every delta (PREREG s5) | open |
| Public sources unusable or unlicensed | Source/licence survey before build; smaller benchmark fallback | open |
| Duplicated mechanical cases inflate sample | Dedupe, per-template cap, effective sample size by family | open |
