# Feedback log procedure (prepared 2026-10-16; implements Amendments 10 and 10a; not yet in use)

**Roles.** The owner posts the announcement and forwards inbound replies. Replies are processed only when forwarded. Nothing in this document starts the clock: **P (publication date) is the announcement date the owner gives** (Amendment 10.2). The window is **4 weeks from P**.

## 1. What goes where
| Item | Where | Never contains |
|---|---|---|
| Announcement: venue, date, link | `docs/discovery/PUBLICATION_LOG.md` (tracked) | who replied, contact details, reply text |
| Reply content as facts, estimates, opinions, open questions | `docs/discovery/evidence_log.local.csv` (**git-ignored**, same columns as `evidence_log.template.csv`) | names, employers, customer identifiers, contact details |
| Counts of qualifying replies per venue | proposed tracked file `docs/discovery/G4_TALLY.md`, created only when the first qualifying reply arrives | identities of any kind |
| Raw messages | stay in the venue or the owner's own mail; copied nowhere | everything |

**Note on the brief:** the owner's note asked for replies to be recorded in `PUBLICATION_LOG.md`. Amendment 10a.2 limits that file to venue, date and link, and says it never records who replied, so replies are **not** recorded there. The tally file above is the proposed way to keep a counts-only public record; if the owner prefers to put counts in `PUBLICATION_LOG.md`, that is an amendment, not an edit.

## 2. Intake (per reply)
1. Owner forwards the reply text (or a paraphrase). Strip names, handles, employers and any contact detail **before** it is stored anywhere.
2. Classify the type (A-F in `REPLY_TEMPLATES.md`).
3. **Test for "qualifying" (Amendment 10.3):** it describes a *specific recent incident or workflow* **and** can be logged as at least one *fact* or *estimate*. Stars, likes, compliments and generic opinions about AI do not count. When in doubt it does **not** count; record it as an opinion or open question.
4. Log rows in `evidence_log.local.csv`: `date, interview_id (I-01, I-02...), role, org_type, category, statement, incident_ref, assumption_tag, confidence, follow_up`. Use roles ("SRE", "service desk lead"), never names. Keep `org_type` coarse (sector and size band only, e.g. "software, mid-size"): in a small community a specific organisation type plus an incident story could re-identify someone. `incident_ref` is an internal tag, not a ticket id.
5. If the replier offers a conversation, run it with `INTERVIEW_GUIDE.md` and log it the same way.
6. Delete any local note on request.

## 3. Mapping to the assumptions and to G4
The A-tags come from `docs/PLAN.md`. They were written for the platform thesis, which was dropped (Amendment 9.2, D26); they remain a useful lens for what a reply says about the *problem*, not about a product.
| Tag | A reply supports it if... | A reply contradicts it if... |
|---|---|---|
| **A1** stale, superseded or inapplicable evidence recurrently slows or misleads investigations | it gives a specific recent incident where that happened (fact) | it says the problem is rare or already handled, with a concrete example |
| **A2** incumbent tools do not already handle authority and applicability | it describes a tool in use that did *not* handle version, date or access correctly | it describes a tool that did handle it with normal configuration (falsifier) |
| A3, A4 (retrieval baseline, constrained LLM) | rarely testable by replies; log only if a reply says something concrete about retrieval vocabulary or assistants | n/a |
| **A5** a sanitized data path exists | the replier offers sanitized artifacts (log as open question; do not accept raw data) | says none can be shared |
| A6 (buyer commitment) | not expected from public replies; do not infer | n/a |
| A7 (schema generalises) | a reply from another domain (support KB, policy, compliance) with the same failure | n/a |
Tag `falsifier` if a reply contradicts an assumption. Replies map to **G4** only through the qualifying test above.

## 4. G4 counting
- Count **qualifying replies** received between P and P + 4 weeks (28 days), exactly as Amendment 10.1 and 10.3 say. Also report, as supplementary information, how many distinct anonymous repliers (I-01, I-02...) they came from. Counting *distinct people* instead would be stricter than the registered text and would need an amendment registered before the first reply is counted; it is proposed here, not adopted.
- **Pass:** at least 3 qualifying replies in the window. **Stop rule fires:** fewer than 3 at day 28 (Amendment 10.1, 10.5): the benchmark-plus-policy framing stands (already adopted), and G4 is reported as not met.
- State in every report: inbound replies are self-selected, not a representative sample, subject to publication bias, and cannot establish prevalence, willingness to pay, or that incumbents lack these behaviours. A pass supports only "some practitioners recognise the problem" (Amendment 10.4).

## 5. Cadence and reporting
- Weekly: owner forwards new replies; update the local evidence log and (if created) the tally. No outreach, no chasing.
- Day 28: a short report: replies received, qualifying replies, which assumption tags each touched, and the G4 outcome with the strength-of-evidence statement above. Publish counts only.
- Any change to these rules is an amendment, committed before it is used.

## 6. Example row (synthetic, for format only; not a real reply)
`2026-11-01, I-01, SRE, mid-size software company, fact, "Followed a runbook for the previous major version during an upgrade incident; the current one lived in a different wiki space.", INC-A, A1, medium, "ask how they decided which page to trust"`
