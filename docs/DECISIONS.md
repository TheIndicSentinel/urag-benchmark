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

| ID | Date | Decision | Status | Evidence | Next |
|---|---|---|---|---|---|
| D10 | 2026-10-14 | Public evaluation proceeds on branch phase2/generator; no merge/tag/push without user approval | Active | brief s0 | await approval |
| D11 | 2026-10-14 | Value claim restated as critical-error reduction, not accuracy | Proposed | RESULTS_PUBLIC.md items 1-2 | confirm on S2/S3 |
| D12 | 2026-10-14 | F1 generator redesign needed (T after gold window) before held-out is run | Open | F1/F2 redundancy in ablation | Amendment 5 + regenerate |

| ID | Date | Decision | Status | Evidence | Next |
|---|---|---|---|---|---|
| D13 | 2026-10-14 | F1/F3 reported as "no difference by construction", not as falsification | Active | review; RESULTS_PUBLIC labels | G2 is the real test |
| D14 | 2026-10-14 | Sufficiency kept as a stated-but-undemonstrated claim; lexical floor 0.70 fixed a priori | Active | v4 results | needs content-level ground truth or drop |
| D15 | 2026-10-14 | Conflict rule recorded as a scoping flaw of frozen arm A; A2 is a variant, arm A not edited | Active | S2 over-abstention | none |
| D16 | 2026-10-14 | Do not add a third versioned source to make F1 conclusive | Active | review; F1 is non-informative by construction | none |
| D17 | 2026-10-14 | No push before user confirms remote; origin is PUBLIC | Blocked on user | gh repo view | user decision |

| ID | Date | Decision | Status | Evidence | Next |
|---|---|---|---|---|---|
| D18 | 2026-10-15 | No refactor of frozen files (`pipeline.py`, `public_eval.py`, `docs_gen.py`) before the held-out run; they are in the Amendment 11 digest | Active | architecture review; digest definition | after held-out |
| D19 | 2026-10-15 | After held-out: build new package (e.g. `urag_core`) as one change set: pure `decide()` governance engine + interfaces + versioned policy file; frozen files kept as reference; validated by output equivalence on all regression and S1/S2 cases | Proposed | review items 2-4 | after held-out |
| D20 | 2026-10-15 | Known limitations, not fixed pre-held-out: (a) arm A raises KeyError on an *absent* `approval_state` key (G2 uses `None`, so G2 is unaffected); (b) module-level index cache mutated from `public_g2.py`; (c) dropping `effective_to` is indistinguishable from open-ended, so metadata loss can raise confidence (Amendment 7.2), a monotonicity property must encode this | Active | verified in code 2026-10-15 | fix in D19 change set |

| ID | Date | Decision | Status | Evidence | Next |
|---|---|---|---|---|---|
| D21 | 2026-10-15 | Add a report-script assertion that the query style recorded in each result equals the registered primary; also record the style inside each checkpoint. Done AFTER the held-out run so gate-script behaviour stays stable during the gate | Deferred | G2 ran with the wrong style (Amendment 12) | after held-out |
| D22 | 2026-10-15 | Seed-level spread reported as supplementary beside the strict-inequality verdict; never replaces it | Active | `public_g2_spread.py` | run on lead after 36/36 |
| D23 | 2026-10-15 | Product implication carried forward: the surviving claim is "abstain and flag under uncertain metadata"; whether teams accept an answer rate of ~30-45% is a G4 question the benchmark cannot answer | Active | G2 title-style read | G4 after publication |

| ID | Date | Decision | Status | Evidence | Next |
|---|---|---|---|---|---|
| D24 | 2026-10-15 | Held-out record lists arms as a literal that mirrors the arm construction in `public_eval.py`; accepted as a known minor drift risk rather than changing the digest again. The record also carries the full args, so a mismatch would be visible | Accepted | final guard review (PASS) | build arms first and record from the list in the post-held-out refactor (D19) |
| D25 | 2026-10-15 | Exact held-out command to use after the digest is published: `python3 -I src/urag/public_eval.py --split heldout --confirm-frozen --query-style lead` (sources default to all available; warm the canon caches with a dev run first). Do not run it before the hashes are public and G2 lead-style is read | Active | Amendment 11b | after push + gist |
