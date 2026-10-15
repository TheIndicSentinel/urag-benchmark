# Sources (Phase 2 survey, 2026-10-14)

Status (updated 2026-10-14): S1 and S2 were ingested locally and cases generated from them (pointers only); S3 is still a candidate and has not been ingested. The original survey text below is kept as written.

Original survey status: **candidates only. No data had been ingested and no case generated.** Licence status: V = confirmed on a primary page this session; S = secondary source only; U = unverified. Re-check each licence file and record the commit SHA and retrieval date at ingestion time. Not legal advice.

## Publication rule
Published benchmark artifacts contain case IDs, source pointers (repo, path, commit SHA / version, URL) and rebuild scripts, **not** republished source text. Local working copies stay out of the repo. This avoids share-alike obligations on derived text and keeps attribution simple.

## Core set (IT benchmark; satisfies >=3 sources, >=2 families)
| ID | Source | Family | Licence | Status | Mechanical ground truth | Main tautology / noise risk |
|---|---|---|---|---|---|---|
| S1 | Kubernetes website docs (github.com/kubernetes/website, release branches) | doc-versioning | CC-BY-4.0 (attribution) | V (repo sidebar/root LICENSE; code-file licence not checked) | Page at the tag/branch for the ticket's resolved version is the applicable one; a path changed/removed in a later tag marks the earlier one superseded | Many pages byte-identical across versions: filter to cases where text differs; version must be implicit (simulated ticket field), not in the query |
| S2 | PostgreSQL documentation | doc-versioning | PostgreSQL Licence; permission grant explicitly covers "software and its documentation"; requires copyright notice + licence paragraphs in copies | V (postgresql.org/about/licence) | Same as S1; release notes give explicit deprecation/removal signals | Same as S1; version-path format at ingestion still to confirm |
| S3 | GitLab runbooks (gitlab.com/gitlab-com/runbooks) | runbook-history | MIT | V (per survey; re-check LICENSE at ingestion) | As-of-date content = blob at last commit before incident time; later commit on same path = superseded; deletion = retired; path/dir = service | A commit is not a semantic supersession: diff-significance filter required; "approved" state is simulated, no external truth |

## Optional / conditional
| ID | Source | Licence | Status | Role | Condition |
|---|---|---|---|---|---|
| O1 | Wikimedia incident reports (wikitech) | CC BY-SA ("additional terms may apply") | S (survey fetch; version not stated) | incident-timeline family, small | Pointers only; timestamp-ordering rule only (no "cause" extraction) |
| O2 | Stack Exchange dump (serverfault/superuser/unix/devops) | CC BY-SA 4.0 on archive.org; AI-use terms of dump access unresolved | S | Q&A staleness, vocabulary mismatch | **Deferred.** Use only if terms are verified to permit it; local only, no redistribution; must not block the benchmark |
| P1 | legislation.gov.uk | Open Government Licence v3.0 (via secondary pages; one attribution caveat for Westlaw-contributed data) | S | portability corpus (config-only test, G3) | Verify OGL on primary page and the point-in-time URI syntax and rate limits before use (developer pages did not load this session) |
| P2 | eCFR (US) | U | U | portability fallback | Confirm access terms and versioner API |

## Excluded or not usable as corpus
- danluu/post-mortems: no licence file; index of third-party posts. URL index only.
- GitLab docs (`doc/` in gitlabhq): MIT repo, but `doc/` is CC BY-SA 4.0 (V, LICENSE file). Share-alike; not in core set.
- GitLab handbook: licence unverified.
- Terraform docs: BUSL-era licence unverified; avoid.
- Company postmortems linked from lists: third-party copyright; do not republish.

## Gaps (classes with no mechanically grounded source)
- Approved vs draft: no real approval state anywhere; simulated and labelled as such.
- Causal-overclaim: needs prose interpretation; only timestamp-ordering is mechanical. Expect **inconclusive**.
- Environment applicability: weak (version tags only).
- Unresolved-conflict: only via paired runbooks or Q&A; frequency uncertain.
- Insufficient-evidence / unnecessary-abstention: constructed by removing the gold document; mechanical but synthetic, labelled so.
Per PREREGISTRATION s5, classes below the minimum sample are reported as inconclusive; thresholds are not lowered.


## Ingestion verification record (2026-10-14T13:59Z)
Checked against primary files in local blob-less clones (untracked, `.local_sources/`):
| ID | Licence file checked | Result | Pinned ref |
|---|---|---|---|
| S1 | `LICENSE` at repo root, branch release-1.34 | Creative Commons Attribution 4.0 International. No licence note found in README. Individual files may carry other terms (e.g. code samples); only pointers are published. | release-1.30..1.36, SHAs in `configs/generator.json` |
| S2 | `COPYRIGHT` at tag REL_17_0 | PostgreSQL Licence; grant covers "software and its documentation" with copyright and paragraphs retained in copies. | REL_14_0..REL_18_0 tags, SHAs in config |
| S3 | `LICENSE` at master | MIT, Copyright GitLab, Inc. | master @ 4cfd1ca7, 983 commits visible, 26,761 files of which 983 `.md` at HEAD (counts from local clone) |
Re-verify before any publication. Not legal advice.
S1 scale check: content/en/docs holds 1,343 (v1.30) to 1,672 (v1.36) `.md` files per release.

---
## Candidate S4 for a fresh held-out comparison (survey 2026-10-15; not ingested, nothing generated)
Purpose (if pursued): a source never seen by any arm design, to test the post-hoc arms (governance on top of a metadata filter, lineage-scoped conflict rule) on fresh held-out data. It cannot make G1 evaluable: the S1 and S2 held-out splits are spent for digest `8a12b347…`, so G1's "3 sources on held-out" cannot be reconstituted. It would be a single-source confirmatory test.

| Candidate | Licence (checked at primary) | Release structure | Docs volume | Verdict |
|---|---|---|---|---|
| **Django** (`django/django`, `docs/`) | BSD-3-Clause; `LICENSE` header read, no documentation carve-out in it; no licence note found in `docs/README.rst` | `stable/X.Y.x` branches and release tags | 603 (4.2), 608 (5.0), 631 (5.1), 656 (5.2) `.txt` files under `docs/` | **Recommended.** Verify per-file headers and the docs-specific statement before ingestion |
| Flask (`pallets/flask`) | BSD-3-Clause (`LICENSE.txt`) | tags | much smaller docs tree | Possible but small; fewer changed pages |
| NumPy | `NOASSERTION` (composite `LICENSE.txt`) | tags | large | Needs manual licence review (bundled third-party terms) |
| CPython `Doc/` | `NOASSERTION` (PSF composite) | branches 3.x | large | Needs manual licence review; docs terms differ from code |
| Node.js `doc/api` | `NOASSERTION` (composite) | tags | medium | Needs manual licence review |

Known weaknesses for Django as a test source: web-framework documentation, not IT operations; reStructuredText with Sphinx directives (needs a parser like the SGML one); release notes pages are version-specific by design (exclude or treat separately); no ACL or approval state, so those stay simulated as before. Domain mismatch bears on the "IT incident" framing but not on version/lifecycle behaviour.

Pin by **release tag commit SHAs**, not branch tips, as for S2. Whichever source is chosen, ingestion needs: licence verification recorded here, an amendment registering the new arm(s) and digest **before** any generation, and a held-out claim lock as in Amendments 11/11a/11b.
