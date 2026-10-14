# Customer discovery: outreach plan

**Purpose:** learn how incident investigation actually works today and where it breaks. This is research, not a sales call. No product exists to show; do not imply one does.

## Target profiles (fill what is reachable; no slot is required)
| # | Profile | Target | Why |
|---|---|---|---|
| 1 | IT ops / incident-management practitioner | 2 | Owns the investigation workflow end to end |
| 2 | SRE or application-support engineer | 2 | Hands-on evidence gathering, runbook use |
| 3 | Service desk / incident-response lead | 1-2 | Triage, escalation, handoff cost |
| 4 | ITSM admin or knowledge-management owner | 1 | Runbook lifecycle, permissions, existing AI/search config |
| 5 | Potential buyer / pilot sponsor | 1-2 | Budget, security review, procurement path |

Fewer than 8 conversations is still useful; label findings accordingly.

## Sequencing
1. **You list reachable people by role only** (initials or a private list; nothing goes in the repo).
2. Rank by warmth: direct colleague/ex-colleague > one-intro-away > community (local SRE/ITSM meetups, public forums where you already participate) > cold.
3. Warm contacts first, and start with practitioners (profiles 1-3): they give the concrete incidents. Do buyers after you have 2-3 incident stories to anchor on.
4. Ask each interviewee for one further introduction at the end.
5. Target: first 3 invitations sent this week; 3 conversations done by end of week 2.

## Rules
- Ask for a **recent real incident**, not opinions about AI.
- No pitch, no demo, no pricing talk in the first conversation.
- Ask them to sanitize or describe, never to share confidential data. Do not accept raw customer data.
- Get permission before taking notes; record roles, not names. Keep notes in `docs/discovery/*.local.csv` (gitignored).
- A request for a free proof-of-concept is not a commitment. Record it as such.
- Log what is **fact / estimate / opinion / open question** separately (see `evidence_log.template.csv`).

## Invitation (adapt tone; 3 variants below)

**Warm, message or email**
> Hi [name], I'm researching how teams investigate IT incidents, specifically how people find the right runbook and supporting evidence under time pressure, and where the current process breaks down. Could I have 20-30 minutes to hear about one recent incident you handled? I'm not selling anything and there's nothing to demo; I just want to understand what actually happened and what got in the way. Nothing confidential needed. A rough description is plenty. Happy to work around your schedule.

**Introduction request (to a mutual contact)**
> Would you be willing to introduce me to someone on your ops/SRE/service desk side who'd be open to a 20-30 minute chat about a recent incident and how they investigated it? It's research only, no sales, and they can stay at whatever level of detail they're comfortable with.

**Community post**
> Researching how teams actually investigate incidents (finding the right runbook, stale docs, access gaps). Looking for 20-30 minute chats about one recent incident, no pitch, no product. DM if you'd be open to it.

## After each conversation
Within 24 hours: fill the evidence log, tag assumptions A1-A7 from PLAN.md as supported / contradicted / untested, and note any falsifier hit.
