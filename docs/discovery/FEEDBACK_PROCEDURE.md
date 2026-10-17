# Feedback log procedure (prepared 2026-10-16; implements Amendments 10 and 10a; not yet in use)

**Roles.** The owner posts the announcement and forwards inbound replies. Replies are processed only when forwarded. Nothing in this document starts the clock: **P (publication date) is the announcement date the owner gives** (Amendment 10.2). The window is **4 weeks from P**.

## 1. What goes where
| Item | Where | Never contains |
|---|---|---|
| Announcement: venue, date, link | `docs/discovery/PUBLICATION_LOG.md` (tracked) | who replied, contact details, reply text |
| Reply content as facts, estimates, opinions, open questions | `docs/discovery/evidence_log.local.csv` (**git-ignored**, same columns as `evidence_log.template.csv`) | names, employers, customer identifiers, contact details |
| Counts of qualifying replies per venue | proposed tracked file `docs/discovery/G4_TALLY.md`, created only when the first qualifying reply arrives | identities of any kind |
| Draft replies and stripped working notes | `docs/discovery/replies.local.md` (**git-ignored**) | anything not already stripped of identifiers |
| Raw messages | stay in the venue or the owner's own mail; copied nowhere | everything |

**Note on the brief:** the owner's note asked for replies to be recorded in `PUBLICATION_LOG.md`. Amendment 10a.2 limits that file to venue, date and link, and says it never records who replied, so replies are **not** recorded there. The tally file above is the proposed way to keep a counts-only public record; if the owner prefers to put counts in `PUBLICATION_LOG.md`, that is an amendment, not an edit.

## 2. Setup (once, before the first reply or the first dry run; safe to repeat)
1. **Check the path is ignored:** `git check-ignore -v docs/discovery/evidence_log.local.csv docs/discovery/replies.local.md` must print a matching `*.local.*` rule for both. If it prints nothing, stop.
2. **Create the log from line 1 of the template only, and only if it does not exist:** `[ -e docs/discovery/evidence_log.local.csv ] || head -1 docs/discovery/evidence_log.template.csv > docs/discovery/evidence_log.local.csv`. Never run a bare `head -1 ... > evidence_log.local.csv` once real rows exist: it would overwrite them. Copying the whole template drags its `#` comment lines into the data (found in the dry run).
3. **Write rows with a CSV-aware tool** (statements contain commas; quote them). Never hand-type rows into the file.
4. **Stage explicit paths only; never `git add -A`, `git add .` or `git add -f`** (`-f` is the one way an ignored `*.local.*` file could be staged). After writing, `git status --short` must show nothing new.

## 3. Intake (per reply)
1. Owner forwards the reply text (or a paraphrase). Strip names, handles, employers and any contact detail **before** it is stored anywhere. If a reply volunteers an email address, an employer or a username: do not copy it, do not repeat it in any reply, and do not contact anyone through it unless they explicitly invited a private follow-up (and then keep it out of every log and file).
2. Classify the type (A-F in `REPLY_TEMPLATES.md`).
3. **Test for "qualifying" (Amendment 10.3):** it describes a *specific recent incident or workflow* **and** can be logged as at least one *fact* or *estimate*. Stars, likes, compliments and generic opinions about AI do not count. When in doubt it does **not** count; record it as an opinion or open question.
4. Log rows in `evidence_log.local.csv` with the columns of the template header: `date, interview_id (I-01, I-02... one per person), role, org_type, category, statement, incident_ref, assumption_tag, confidence, follow_up, reply_ref (R-01... one per reply), venue, reply_date, counts_for_g4`. One assumption tag per row; if a statement bears on two assumptions, write two rows. New rows start as `counts_for_g4 = pending`. Use roles ("SRE", "service desk lead"), never names. Keep `org_type` coarse (sector and size band only, e.g. "software, mid-size"): in a small community a specific organisation type plus an incident story could re-identify someone. `incident_ref` is an internal tag, not a ticket id.
5. Draft the reply from `REPLY_TEMPLATES.md` and store the draft in `docs/discovery/replies.local.md`. The assistant never sends it.
6. If the replier offers a conversation, run it with `INTERVIEW_GUIDE.md` and log it the same way.
7. Delete any local note on request.

## 4. Mapping to the assumptions and to G4
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

## 5. G4 counting
- Set `counts_for_g4 = yes` on a reply's rows only after applying the qualifying test (Amendment 10.3) **and** checking `reply_date` lies in [P, P + 28 days]; otherwise `no`. The G4 count is the number of distinct `reply_ref` values with `counts_for_g4 = yes`. Rows whose `interview_id` starts with `DEMO-` (or whose `counts_for_g4` is `demo`) are synthetic dry-run rows and are excluded from every count, tally and report.
- Count **qualifying replies** received between P and P + 4 weeks (28 days), exactly as Amendment 10.1 and 10.3 say. Also report, as supplementary information, how many distinct anonymous repliers (I-01, I-02...) they came from. Counting *distinct people* instead would be stricter than the registered text and would need an amendment registered before the first reply is counted; it is proposed here, not adopted.
- **Pass:** at least 3 qualifying replies in the window. **Stop rule fires:** fewer than 3 at day 28 (Amendment 10.1, 10.5): the benchmark-plus-policy framing stands (already adopted), and G4 is reported as not met.
- State in every report: inbound replies are self-selected, not a representative sample, subject to publication bias, and cannot establish prevalence, willingness to pay, or that incumbents lack these behaviours. A pass supports only "some practitioners recognise the problem" (Amendment 10.4).

## 6. Cadence and reporting
- Weekly: owner forwards new replies; update the local evidence log and (if created) the tally. No outreach, no chasing.
- Day 28: a short report: replies received, qualifying replies, which assumption tags each touched, and the G4 outcome with the strength-of-evidence statement above. Publish counts only.
- **Tally file format** (`docs/discovery/G4_TALLY.md`, created on the first real reply; counts only, no identities, no text):
  | Venue | Replies received | Qualifying (`yes`) | Distinct anonymous repliers (supplementary) | Last updated |
  |---|---|---|---|---|
- **Day-28 report skeleton:** (1) window: P to P+28d; (2) per-venue counts from the tally; (3) qualifying total vs the threshold of 3; (4) assumption tags touched, with `falsifier` counts; (5) G4 outcome (met / not met); (6) the strength-of-evidence statement of Amendment 10.4 verbatim; (7) what was not done (no outreach, no chasing).
- Any change to these rules is an amendment, committed before it is used.

## 7. Example row (synthetic, for format only; not a real reply)
`2026-11-01, I-01, SRE, software mid-size, fact, "Followed a runbook for the previous major version during an upgrade incident; the current one lived in a different wiki space.", INC-A, A1, medium, "ask how they decided which page to trust", R-01, <venue as in PUBLICATION_LOG.md>, 2026-11-01, pending`

## 8. Dry run (2026-10-17) and what it changed
A synthetic reply labelled DEMO was processed end to end in the git-ignored local files (not committed, not counted). It found six gaps, fixed in this version: (1) copying the whole template put its comment lines in the data; (2) no step checked that the local paths are git-ignored; (3) the log had no reply id, venue, reply date or counts-for-G4 field, so a naive count would have scored the DEMO as 1 and per-venue tallies were impossible; (4) nothing covered replies that volunteer an email, employer or username; (5) draft replies had no stated home; (6) there was no tally format or day-28 skeleton. To repeat a dry run: use `interview_id` `DEMO-nn`, set `counts_for_g4 = demo`, delete the DEMO rows (or rely on the exclusion rule) before the first real reply.
