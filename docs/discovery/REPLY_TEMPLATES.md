# Reply templates (prepared 2026-10-16; for use only on feedback the owner forwards)

Drafts are stored in the git-ignored `docs/discovery/replies.local.md` and are never sent by the assistant. All replies: roles only, no names; **never ask for contact details**; never ask for anything confidential; never solicit votes or stars; keep claims no stronger than the README; do not describe the work as a product or as evidence of demand. Replies in public threads are visible to everyone, so do not quote private messages without consent (Amendment 10.6).

## A. A real incident account (the kind that can qualify under Amendment 10.3)
> Thank you, this is useful. I only want to understand what happened, so please skip anything confidential or identifying.
> A few optional questions, answer whichever you can:
> 1. What did you need to know, and where did you look first?
> 2. Was any document stale, for the wrong version or environment, contradictory, or one you could not access? How did you decide which one to trust?
> 3. Roughly how long did that part take, and what did it cost (escalation, rework, downtime)?
> 4. What were you using (ticketing, wiki, search, an assistant), and where did it fall short?
>
> I will note your reply by role only ("e.g. SRE") and will not quote it without asking. If you would rather it was not recorded, say so and I will delete it. If you are open to a 20-30 minute conversation about it, I am happy to do that; there is nothing to sell and no product.

*Logging:* see `FEEDBACK_PROCEDURE.md`. This type usually maps to A1 (and sometimes A2).

## B. A challenge to the method
> Fair challenge, and several of these are limits I list myself: expected answers come from the same version and date fields a metadata filter uses (so wrong-version and ACL cases cannot separate filtering from governance on clean metadata); one family's correct answer is defined by the policy being tested; ACLs and approval state are simulated; queries are derived from the gold page; documents are the unit of evidence; two main sources plus one confirmatory source. The full list is in `docs/RESULTS_PUBLIC.md` (threats to validity).
> On your specific point ({restate it in one line}): {answer only what the repository supports, with the file or amendment}. If you have a test that would change the conclusion, tell me what it would show and what result would change my mind; I would rather record it than argue.
> Note that the held-out splits are spent, so a re-test on them would be exploratory and needs a new pre-registration; I am happy to take it as an issue.

*Do not:* defend a result beyond what the write-up says; claim governance beats a metadata filter; cite the dev sanity run as evidence.

## C. A request for data
> There is no customer or operational data in this project and none is held. The repository contains pointer-only case files (source, path, version) and the scripts to rebuild everything from the pinned upstream releases: `scripts/fetch_sources.py`, then `src/urag/gen/docs_gen.py`. Result files contain ids and metrics only, no third-party text. Licences and attributions are in `NOTICE` and `docs/SOURCES.md`.
> If you want to run the arms yourself, the README lists the commands. Please do not send me confidential data: I cannot accept it, and I do not take raw customer data in any form.

## D. Interest in using it, or asking whether there is a product
> This is a research artifact, not a product, and I am not offering one or making commitments about future work. If it is useful as a baseline or a checklist, the policy document (`docs/LIFECYCLE_POLICY.md`) and the benchmark are MIT-licensed. If you have a concrete problem with stale or wrong-version documents, an account of it (no names, nothing confidential) would still be valuable to me.

## E. A compliment, a star or a generic opinion about AI
> Thanks. If you have a specific incident where a stale, wrong-version or inaccessible document caused trouble, a short account would help; if not, no problem.

*Logging:* not a qualifying reply (Amendment 10.3: stars, likes, compliments and generic opinions do not count).

## F. A request to appear, be quoted, or collaborate
> Thanks, I would rather keep this simple: I am recording replies by role only and not quoting anyone. For anything beyond that I would need to think about scope; for now the artifact is complete and I am not starting new work.

## G. A reply that volunteers an email address, an employer, a username or other identifying detail
Do not copy it into any log, do not repeat it in your reply, and do not contact anyone through it unless they explicitly invited a private follow-up (then keep it out of every file). In a public thread you may add: "Thanks. For your own privacy you may want to edit out identifying details; I only record roles." Then treat the substance as type A.
