"""Deterministic authority-aware investigation pipeline (Baseline A).

Order is deliberate: authorization -> retrieval (FTS over authorized set only)
-> lifecycle/authority -> applicability -> change correlation -> validation.
"""
import json, re, sqlite3, hashlib
from datetime import datetime, timedelta

CHANGE_LOOKBACK = timedelta(hours=24)
# change types that can plausibly affect runtime behavior; missing type is kept but flagged
RUNTIME_CHANGE_TYPES = {"deployment", "config", "infrastructure", "schema"}
_STOP = {"a", "an", "the", "on", "of", "to", "and", "or", "in", "is", "for"}


def load(path):
    with open(path) as f:
        return json.load(f)


def _dt(s):
    return datetime.fromisoformat(s) if s else None


def resolve_service(name, catalog):
    """Return canonical service id, or None if unknown/ambiguous."""
    if not name:
        return None
    hits = {c for c, aliases in catalog.items()
            if name.lower() == c.lower() or name.lower() in (a.lower() for a in aliases)}
    return hits.pop() if len(hits) == 1 else None


def canonical_env(name, env_aliases):
    """Canonical environment id, or None if absent/unrecognized (never guessed)."""
    if not name:
        return None
    n = name.strip().lower()
    for canon, aliases in (env_aliases or {}).items():
        if n == canon.lower() or n in (a.lower() for a in aliases):
            return canon
    return None


def authorize(docs, user):
    """Tenant-free simulated ACL: a doc is visible iff the user shares a group. Fail closed."""
    groups = set(user.get("groups") or [])
    return [d for d in docs if groups & set(d.get("acl_groups") or [])]


def retrieve(candidates, text, k=10):
    """Keyword retrieval over the authorized candidate set only (index built per request)."""
    db = sqlite3.connect(":memory:")
    db.execute("create virtual table t using fts5(id unindexed, content)")
    db.executemany("insert into t values (?,?)",
                   [(d["id"], f'{d["title"]} {d["body"]}') for d in candidates])
    toks = [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in _STOP]
    if not toks:
        return []
    q = " OR ".join(toks)
    rows = db.execute("select id from t where t match ? order by bm25(t) limit ?", (q, k)).fetchall()
    by_id = {d["id"]: d for d in candidates}
    return [by_id[r[0]] for r in rows]


# Governance checks that arm A performs; each can be disabled for ablation (docs/PREREGISTRATION.md s2).
CHECKS = ("lifecycle", "authority", "applicability", "conflict", "sufficiency")
ARMS = ("A", "N1", "N0")


def classify_runbook(d, inc, catalog, env_aliases=None, disable=frozenset()):
    """Return (label, reason). Authority and applicability kept as separate checks."""
    at = _dt(inc["opened_at"])
    if "lifecycle" not in disable and d["approval_state"] in ("superseded", "deprecated"):
        return "historical", f'{d["approval_state"]} (superseded_by={d.get("superseded_by")})'
    if "authority" not in disable and d["approval_state"] != "approved":  # fail closed: draft, unreviewed, unknown
        return "excluded", f'approval_state={d["approval_state"]!r}: not approved guidance'
    ef, et = _dt(d.get("effective_from")), _dt(d.get("effective_to"))
    if "lifecycle" not in disable and ((ef and at < ef) or (et and at >= et)):
        return "historical", "outside effective window at incident time"
    if "applicability" in disable:
        return "current_guidance", "applicability check disabled (ablation)"
    inc_svc = resolve_service(inc.get("service"), catalog)
    inc_env = canonical_env(inc.get("environment"), env_aliases)
    doc_env = canonical_env(d.get("environment"), env_aliases)
    if d.get("service") is None or doc_env is None or inc_svc is None or inc_env is None:
        return "applicability_unknown", "service/environment could not be established; not treated as authoritative"
    if d["service"] != inc_svc or doc_env != inc_env:
        return "excluded", "not applicable to this service/environment"
    return "current_guidance", "approved, in effective window, service and environment match"


def _naive(hits, incident, visible_ids):
    """N0/N1 output rule: the top-ranked runbook is the answer; no governance decisions."""
    out = {"incident_id": incident["id"], "facts": [], "applicable_runbook": None,
           "applicability_flags": [], "historical": [], "hypotheses": [],
           "missing_information": [], "status": "ok", "manifest": []}
    top = next((d for d in hits if d["type"] == "runbook"), None)
    if top:
        out["applicable_runbook"] = {"id": top["id"], "title": top["title"]}
        out["manifest"].append(top["id"])
    else:
        out["missing_information"].append("No runbook retrieved.")
    return out


def investigate(corpus, user, incident, trace=None, prefilter=False, arm="A", disable=frozenset()):
    """arm: "A" governed, "N1" ACL-filtered retrieval only, "N0" retrieval only (no ACL).
    disable: subset of CHECKS to switch off in arm A (ablation)."""
    if arm not in ARMS:
        raise ValueError(f"unknown arm {arm!r}")
    disable = frozenset(disable)
    if not disable <= set(CHECKS):
        raise ValueError(f"unknown checks {sorted(disable - set(CHECKS))}")
    catalog = corpus["service_catalog"]
    visible = corpus["docs"] if arm == "N0" else authorize(corpus["docs"], user)
    cand = [d for d in visible if d["type"] in ("runbook", "incident")]
    svc = resolve_service(incident.get("service"), catalog)
    if prefilter and svc:  # optional metadata pre-filter; unscoped docs kept
        cand = [d for d in cand if d.get("service") in (svc, None)]
    hits = retrieve(cand,
                    incident["summary"] + " " + (incident.get("service") or ""))
    if trace is not None:  # eval-only; never part of user-visible output
        trace["retrieved"] = [d["id"] for d in hits]
    if arm != "A":
        return _naive(hits, incident, {d["id"] for d in visible})
    out = {"incident_id": incident["id"], "facts": [], "applicable_runbook": None,
           "applicability_flags": [], "historical": [], "hypotheses": [],
           "missing_information": [], "status": "ok", "manifest": []}
    out["facts"].append({"claim": f'Incident opened at {incident["opened_at"]}; service={incident.get("service")}; '
                                  f'environment={incident.get("environment")}.', "evidence": []})
    current = []
    for d in hits:
        if d["type"] == "incident":
            if svc is None or d.get("service") != svc:  # applicability: same resolved service only
                continue
            out["historical"].append({"id": d["id"], "note": "historical incident, not current guidance"})
            out["manifest"].append(d["id"]); continue
        label, reason = classify_runbook(d, incident, catalog, corpus.get("environment_aliases"), disable)
        if label == "current_guidance":
            current.append(d)
        elif label == "historical":
            out["historical"].append({"id": d["id"], "note": reason})
            out["manifest"].append(d["id"])
        elif label == "applicability_unknown":
            out["applicability_flags"].append({"id": d["id"], "note": reason})
            out["manifest"].append(d["id"])
    if len(current) == 1:
        out["applicable_runbook"] = {"id": current[0]["id"], "title": current[0]["title"]}
        out["manifest"].append(current[0]["id"])
    elif len(current) > 1 and "conflict" in disable:  # ablation: take the top-ranked eligible runbook
        out["applicable_runbook"] = {"id": current[0]["id"], "title": current[0]["title"]}
        out["manifest"].append(current[0]["id"])
    elif len(current) > 1:
        out["status"] = "conflicting_evidence"
        out["applicability_flags"] += [{"id": d["id"], "note": "multiple equally eligible runbooks"} for d in current]
        out["manifest"] += [d["id"] for d in current]
    else:
        out["missing_information"].append("No approved, applicable runbook established.")
    # change correlation: timing is a fact, causation is only a hypothesis
    inc_svc = resolve_service(incident.get("service"), catalog)
    at = _dt(incident["opened_at"])
    for d in visible:
        if d["type"] != "change" or inc_svc is None or d.get("service") != inc_svc:
            continue
        ct = _dt(d["effective_from"])
        ctype = d.get("change_type")
        if ctype is not None and ctype not in RUNTIME_CHANGE_TYPES:
            continue
        if ct and timedelta(0) <= at - ct <= CHANGE_LOOKBACK:
            mins = int((at - ct).total_seconds() // 60)
            out["facts"].append({"claim": f'{d["title"]} occurred {mins} minutes before the incident opened.', "evidence": [d["id"]]})
            out["hypotheses"].append({"claim": f'The change {d["id"]} may have contributed; causality is not established.',
                                      "supporting": [d["id"]],
                                      "relevance_note": None if ctype else "change type unknown; relevance unverified",
                                      "needed_to_test": ["error onset time vs deploy completion", "error signature diff between versions", "rollback or canary result"]})
            out["manifest"].append(d["id"])
    if "sufficiency" not in disable and out["status"] == "ok" and out["applicable_runbook"] is None and not out["hypotheses"] and not out["historical"]:
        out["status"] = "insufficient_evidence"
    out["manifest"] = sorted(set(out["manifest"]))
    errors = validate(out, {d["id"] for d in visible})
    if errors:
        out = {"incident_id": incident["id"], "status": "validation_failed", "errors": errors}
    return out


def validate(out, authorized_ids):
    """Citations must be in the manifest and authorized; facts may not assert causation."""
    errs = []
    for sec in ("facts", "hypotheses"):
        for c in out.get(sec, []):
            for e in c.get("evidence", []) + c.get("supporting", []):
                if e not in out["manifest"] or e not in authorized_ids:
                    errs.append(f"citation {e} not in manifest/authorized")
            if sec == "facts" and re.search(r"\b(caused|root cause)\b", c["claim"], re.I):
                errs.append("fact asserts causation")
    return errs
