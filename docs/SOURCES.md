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

### S4 licence verification record (2026-10-15; Amendments 13b.6, 13c)
Fetched with `scripts/fetch_sources.py --sources S4` (depth-1, blob-less, pinned peeled release-tag commits for 4.2, 5.0, 5.1, 5.2, 6.0; docs tree only; `docs/releases/`, `docs/_theme/`, `docs/_ext/` and `docs/requirements.txt` removed).
| Check | Result |
|---|---|
| Repository `LICENSE` at pinned 5.2 commit | BSD-3-Clause; header read; no documentation carve-out; no CC/GPL/Apache marker |
| Other licence files | `LICENSE.python` at repo root (outside `docs/`); `docs/_theme/djangodocs/static/fontawesome/LICENSE.txt` (Font Awesome Free: CC BY 4.0 / OFL / MIT, third party) |
| Documentation-specific licence statement | none found in the docs tree or `docs/README.rst` |
| `.txt` pages after all exclusions (13c) | 267 (4.2), 268 (5.0), 268 (5.1), 270 (5.2), 275 (6.0); the parser titled 270/270 pages of 5.2 |
| Third-party text in repo | none; cases are pointers only, source text stays in git-ignored `.local_sources/` |
Not legal advice; re-verify before any publication of derived text (none is published).


---
## Extraction ledger (2026-10-16; read-only scan of the pinned local extracts with the generator's own parsers and read method)
Counts only; no text published. No re-run, regeneration or exclusion was performed (the digest and the spent splits are unchanged).
| Source | Files scanned | Decode failures (`errors="replace"` triggered) | No title | Under 30 words after normalisation |
|---|---|---|---|---|
| S1 Kubernetes (7 releases, `.md`) | 10,440 | 0 | 946 (9.1%) | 2,389 (22.9%) |
| S2 PostgreSQL (5 tags, top-level `.sgml`) | 836 | 0 | 5 (0.6%) | 7 (0.8%) |
| S4 Django (5 releases, `.txt` after exclusions) | 1,348 | 0 | 0 (0.0%) | 50 (3.7%) |

Notes:
- **S1 short pages:** 359 of the 2,389 are `_index.md`; 163 contain a shortcode; the remaining ~1,900 are short pages not further classified. They are *not* all "index stubs".
- **Untitled pages** are indexed with their path as the title (`d["title"] or d["path"]` in the runner). They can never be gold (gold requires a title and at least 30 words).
- **Known limitation:** short and untitled pages were **left in the index** and are a known source of retrieval noise, plausibly part of why gold-in-top-10 is 0.57-0.64 with title queries on dev. They were not excluded after the fact because that would change the pipeline digest and the held-out splits are spent.
- **Silent decode loss:** none observed (0 files needed replacement characters). Front matter with CRLF line endings is normalised by text-mode reading.
- **Verification status of these counts (stated plainly):** every extraction count above (the table and the notes; not the gold-in-top-10 evaluation figure) was produced by the generator's own parsers and read method (`src/urag/gen/docs_gen.py`) and was **not independently re-verified**, with one exception: the S1 file count (10,440) was cross-checked against the extracted directory by a separate reviewer pass. The S2 and S4 counts, and all title and word-count figures, rest on the generator's parsers alone.
