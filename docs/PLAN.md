# URAG v4.1 — Experiment Plan (one page)

**Question:** Does authority-aware evidence selection (authorized + current + approved + applicable + sufficient) measurably improve IT incident investigation vs. what teams already use?
**Experiment:** local CLI over tickets + runbooks + change records; deterministic baseline A vs constrained-LLM variant B; independent/held-out cases; parallel discovery.
**Claim boundary:** no logs, metrics, CMDB, remediation, or writes. Synthetic results prove rule behavior only.

## Assumptions and falsifiers
| # | Assumption | Falsified if |
|---|---|---|
| A1 | Stale/superseded/inapplicable evidence is a recurring cause of slow or wrong investigations | <3 of 8 interviewees can cite a recent incident where it mattered |
| A2 | Incumbent ITSM/search/AI tools do not already handle authority + applicability | Incumbent matches on the same cases with normal configuration |
| A3 | Keyword retrieval is a usable baseline | Recall@5 on vocabulary-mismatch cases is poor and metadata filtering can't compensate |
| A4 | Constrained LLM adds value without new critical failures | B has any critical failure A lacks, or no usefulness gain over A |
| A5 | Authorized, sanitized data path exists | No interviewee can provide artifacts or pilot access |
| A6 | Buyer will commit (paid pilot / named sponsor) | Only free-POC interest after 8-12 interviews |
| A7 | Evidence schema generalizes | HR/compliance mapping needs new core fields |

## Corpus schema (data/corpus.json)
Doc: `id, type(incident|runbook|change), title, body, service, environment, approval_state(approved|draft|superseded|deprecated|n/a), effective_from, effective_to, supersedes/superseded_by, acl_groups, source_version`. Planned additions: `content_hash`, `author_trust`, `source_updated_at`, `provenance`. Case: `user{groups}, incident{...}, expect{...}, severity`.

## First ten scenarios
| ID | Scenario | Status |
|---|---|---|
| C1 | Current vs superseded/draft/staging runbook | implemented |
| C2 | Relevant unauthorized runbook, no leakage | implemented |
| C3 | Deploy before incident: fact vs hypothesis | implemented |
| C4 | Alias service + missing environment: flag uncertainty | implemented |
| C5 | Conflicting equally-approved runbooks: expose conflict | todo |
| C6 | Low-trust ticket comment contradicts approved runbook | todo |
| C7 | Prompt injection in ticket body / runbook table | todo (needs B) |
| C8 | Vocabulary mismatch (symptom vs procedure wording) | todo |
| C9 | Revocation mid-investigation / cached evidence | todo |
| C10 | Insufficient evidence: must abstain, plus a case that must NOT abstain (coverage) | todo |

Independence rule: C5-C10 and the held-out set are authored or reviewed by someone other than the implementer, or drawn from public postmortems.

## Interview guide (30 min, one recent incident)
1. Walk me through the last incident where finding the right procedure/evidence was slow. What happened?
2. Which systems did you check, in what order? Who had access to what?
3. Was any evidence stale, contradictory, missing, or inaccessible? Show me, sanitized.
4. What did you use (ITSM AI, search, copilot, chat)? What did it get wrong?
5. How long did it take; what did it cost (escalation, downtime, rework)?
6. What improvement would make you change tooling? What would make you reject this?
7. Who owns this problem, who pays, what security review is required?
8. Could you share sanitized artifacts or run a bounded test? Would you pay for it?
Record separately: fact / estimate / opinion / open question.

## Milestones
- [x] W1: skeleton CLI, deterministic pipeline, 4 cases, unittest (done, see below)
- [ ] W1: outreach started; list of 15 targets; DECISIONS/risk files maintained
- [ ] W1: change case variants, alias/dirty-metadata tests, PII/secret detector tests
- [ ] W2: C5-C10, public-source cases, held-out split, 2nd labeler
- [ ] W2: model B (needs small local model; 8 GB RAM => ~3-4B quantized), injection tests
- [ ] W3: coverage-vs-risk report, A vs B, portability mapping (1 hr), go/no-go

## Run
`python3 -m unittest discover -s tests` · `PYTHONPATH=src python3 -m urag.cli --eval` · `PYTHONPATH=src python3 -m urag.cli --case C3-correlation-not-causation`
