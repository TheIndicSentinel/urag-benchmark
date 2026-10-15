# Lifecycle and lineage policy (as implemented by arm A)

**Status:** descriptive. This documents what the frozen reference implementation (`src/urag/pipeline.py`, arm A) does, so it can be reviewed, criticised and re-implemented. It is not a recommendation that these rules are right for any real system, and it is not validated against practitioners. Approval state and access control in the benchmark are simulated.

## 1. Inputs
**Per document:** `id`, `type`, `title`, `body`, `service`, `version` (and/or `environment`), `approval_state`, `effective_from`, `effective_to`, `acl_groups`, and `lineage` (the stable identity shared by successive revisions of one document; for the benchmark, the file path).
**Per request:** principal groups, query text, `opened_at`, `service`, optional `version`, optional `environment`.
**Per corpus:** `applicability_dims` (which of service / environment / version must match), service catalog with aliases, environment aliases.

## 2. Decision order (fixed)
1. **Authorization before retrieval.** The candidate set is restricted to documents whose `acl_groups` intersect the principal's groups. No groups means no documents (fail closed). Unauthorized records never enter the index, ranking, counts, snippets or citations.
2. **Retrieval** (BM25, k=10) over the authorized candidates only.
3. **Per candidate, in order:**
   | Check | Condition | Outcome |
   |---|---|---|
   | Lifecycle state | `approval_state` is `superseded` or `deprecated` | historical (never current) |
   | Authority | `approval_state` is anything other than `approved` (draft, unreviewed, missing, unknown) | excluded (fail closed) |
   | Lifecycle window | `effective_from` missing (document corpora) | flagged `applicability_unknown`, not current |
   | Lifecycle window | `opened_at` before `effective_from` or at/after `effective_to` | historical ("outside effective window"; includes not-yet-effective) |
   | Applicability: service | document or request service unresolved | flagged `applicability_unknown` |
   | Applicability: service | resolved services differ | excluded |
   | Applicability: environment (if required) | either side unrecognised | flagged `applicability_unknown` (never guessed) |
   | Applicability: environment | recognised and different | excluded |
   | Applicability: version (if required) | document version missing | flagged `applicability_unknown` |
   | Applicability: version | request version present and different | excluded ("wrong version") |
   | Applicability: version | request version absent | current, annotated `version_defaulted` |
   | otherwise | | **current guidance** |
4. **Lineage rule** (only when the request has no version): among current candidates that share a `lineage`, only the one with the latest `effective_from` stays current; the others are reported as superseded by a newer revision.
5. **Conflict rule:** more than one current candidate means `status = conflicting_evidence`, all are flagged, and **no single document is named**. Exactly one means it is named as the applicable document. None means "no approved, applicable document established" and, if nothing else was found, `insufficient_evidence`.
6. **Validation:** every cited id must be in the manifest and authorized; a fact may not assert causation.

## 3. Defaults and their rationale
- **Unknown is never authoritative.** Missing or unrecognised metadata is flagged, not silently matched or silently dropped (except `approval_state`, which is excluded).
- **No version in the request** defaults to the revision effective at the incident time, and says so (`version_defaulted`). This is a *policy choice*: teams running an older supported version are poorly served by it.
- **`effective_to` missing means open-ended.** A document whose end date was lost therefore looks current; this is a known limitation, not a feature.
- **Correlation is not causation** (runbook corpora): a change shortly before an incident is reported as a timing fact plus a hypothesis with the evidence needed to test it.

## 4. Registered variants (not part of arm A)
| Variant | Change | Registered in |
|---|---|---|
| A2 `ranked_alternatives` | distinct lineages are not a conflict: name the top-ranked document and list the others as alternatives | Amendment 6 |
| `meta_prefilter` / `_closed` | restrict candidates by window and known version *before* ranking; missing fields kept (open) or dropped (closed) | Amendments 6, 7 |
| `relevance_floor` | after eligibility, drop candidates containing less than 70% of the query's content tokens | Amendment 8 |

## 5. What this policy does not do
- No content-level contradiction detection: "conflict" means "several eligible documents", not "documents disagree". This over-abstains in document corpora (measured: see `docs/RESULTS_PUBLIC.md`).
- No sufficiency check that works: the lexical floor did not separate an on-topic near-duplicate from the answer.
- No passage-level evidence; documents are the unit.
- An absent `approval_state` key raises an error in this implementation (decision D20); `None` is handled.
- Dropping `effective_to` can raise confidence; corrupted values are undetectable by any rule here.

## 6. Adapting it
A different corpus needs only configuration: which dimensions apply (`applicability_dims`), aliases, the approval vocabulary, and the field mapping to the record above. Changing the rules themselves is a new arm with its own pre-registration (see `docs/PREREGISTRATION.md`).
