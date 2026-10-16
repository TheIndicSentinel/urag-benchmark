# Announcement kit (prepared 2026-10-16; nothing has been posted)

**Owner decides:** which venue, when, and the announcement date (which starts the 4-week G4 clock, Amendment 10). Nothing here is posted by any tool. After posting, add one row to `PUBLICATION_LOG.md` (venue, date, link; never who replied).

**Pre-post checklist (every venue):**
1. Re-read that venue's own rules page the same day; rules change, and most pages below could **not** be read in the environment that prepared this kit.
2. Repo is public with LICENSE and NOTICE (true as of `ced2504`); link to the README or `docs/WRITEUP.md`, not to a raw results file.
3. Use the short text in `ANNOUNCEMENT_DRAFT.md` (adapt tone per venue). Lead with the critical-share result and the negative findings; always carry the prevalence caveat.
4. Never ask for votes, upvotes or stars. Never post the same text in several venues at once; stagger them and reuse nothing that reads as marketing.
5. Be available to discuss for a few hours after posting. Replies are handled only as described in `FEEDBACK_PROCEDURE.md` (owner forwards; roles only; no contact details).

## What was verified, and what was not
| Status | Meaning |
|---|---|
| **Verified** | Read on the venue's own page during preparation (2026-10-16) |
| **Partly verified** | Some purpose text read from a primary page; posting mechanics not |
| **Unverified** | Primary page could not be read (domain blocked or timed out); only third-party descriptions seen, which disagree. **Read the rules before posting** |

## Ranked shortlist (by fit to the roles we want to hear from, then by rule risk)
| # | Venue | Role fit | Link post allowed? | Rules status | Notes and risks |
|---|---|---|---|---|---|
| 1 | **r/sre** (Reddit) | SRE and application-support engineers: highest | Unknown | **Unverified**. Rules page `https://www.reddit.com/r/sre/about/rules` could not be read | Third-party guides say self-promotion is policed and that account history matters; treat as unconfirmed. Lead with the write-up, not the repo |
| 2 | **Hacker News** (regular post, or Show HN) | Broad engineering readership, not role-specific | **Yes** for a regular submission of the write-up. Show HN only for something people can run | **Verified** for Show HN (`https://news.ycombinator.com/showhn.html`): must be non-trivial, ready for users to try, and the poster must be around to discuss; blog posts and reading material are off topic for Show HN and go in as regular posts; "please don't ask friends to upvote or comment"; title must start "Show HN". The general guidelines page could not be read | The write-up fits a regular post. The repo is runnable locally but needs a source-fetch step (`scripts/fetch_sources.py`), so a Show HN is borderline; do not use it unless the repo is easy to try |
| 3 | **r/devops** (Reddit) | DevOps and platform engineers: medium-high | Unknown | **Unverified** (`https://www.reddit.com/r/devops/about/rules` not readable) | Third-party guides describe moderate to strict self-promotion handling and advise some prior participation; unconfirmed |
| 4 | **PostgreSQL `pgsql-docs`** mailing list | Maintainers of one source we used (S2) | A short message, not a link-only post | **Partly verified**: purpose is "Discussion regarding PostgreSQL documentation" (`https://www.postgresql.org/list/pgsql-docs/`); posting mechanics (subscription, moderation) not on the page | Courtesy heads-up that their docs were used and how versioning behaved, framed as a question about version/lifecycle metadata. Borderline on-topic; `pgsql-general`'s stated purpose is a "general discussion area for users", so it is not obviously the right place for an announcement (its posting rules were not readable) |
| 5 | **Kubernetes**: discussion forum (`discuss.kubernetes.io`) or contributor Slack | Maintainers of S1 | Unknown | **Unverified**. Guidelines exist at `https://kubernetes.dev/docs/comms/slack` and `https://kubernetes.dev/docs/comms`; a secondary description says conversations must match channel topics and that spam and sales pitches are not tolerated | The SIG Docs channel is, as far as I know, for docs authoring (unverified), so a retrieval benchmark is likely off topic there. Read the guidelines and use an ecosystem-appropriate forum category if one exists |
| 6 | **Django Forum** | Maintainers of S4 | Unknown | **Unverified**. No self-promotion rule found in searches; a search result described the "Packages" category as scoped to package maintainers (unverified) | Weak fit: this is not a Django package. A courtesy note is possible but optional |
| 7 | **ITSM / knowledge-management user communities** (vendor user groups, practitioner associations) | The original target profiles: ITSM admins, knowledge owners | Unknown | **Not researched.** Owner should pick a community where they already have an account and read its rules | Highest role fit for the original IT-operations framing, but our corpora are documentation sets, not ITSM data; say so |
| 8 | **Lobsters** | Programmers, mixed | Unknown | **Unverified**; reported secondhand to be invite-only with strict limits on posting your own work | Likely not available without an invitation; lowest priority |

**Recommended order if the owner wants a minimal plan:** r/sre (after reading its rules), then a regular Hacker News submission of the write-up. Treat the source-maintainer courtesies (4-6) as separate, optional, and framed as notices rather than promotion.

## Link targets and framing
- Primary link: the repository README, or `docs/WRITEUP.md` where a write-up is preferred. The write-up leads with the limited result.
- Lead sentence: "when top-ranked retrieval over versioned documentation returns a page you should not rely on, and what rule-based governance does about it". Do not describe it as a product, a platform, or evidence of demand.
- Always carry the prevalence caveat next to the ~35% critical-error share and the "version-blind index" wording.
