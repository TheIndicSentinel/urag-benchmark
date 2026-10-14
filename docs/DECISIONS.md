# Decisions

| ID | Date | Decision | Status | Evidence | Next |
|---|---|---|---|---|---|
| D1 | 2026-10-14 | Stdlib Python + SQLite FTS5, unittest (pytest/ollama absent; avoid installs) | Proposed | FTS5 verified locally | Revisit if deps are warranted |
| D2 | 2026-10-14 | Authorization filters the candidate set before the FTS index is built per request | Validated (simulated only) | C2, fail-closed test | Add timing/score side-channel tests |
| D3 | 2026-10-14 | Change records are in scope; logs/metrics/CMDB excluded | Proposed | C3 needs change data | Revisit after interviews |
| D4 | 2026-10-14 | Unknown service/env => flagged, never authoritative | Proposed | C4 | Measure entity-resolution accuracy |

# Risks
| Risk | Mitigation / test | Status |
|---|---|---|
| Self-authored cases are tautological | Independent + held-out cases (C5-C10) | open |
| Pipeline is too simple vs real metadata mess | Dirty-metadata corpus | open |
| Customer demand unvalidated | Interviews start now | open |
| 8 GB RAM limits local LLM | Small quantized model; B optional | open |
| Always-abstain passes safety | Coverage-vs-risk gate | open |
