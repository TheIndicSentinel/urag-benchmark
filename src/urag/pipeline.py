"""Deterministic authority-aware investigation pipeline (Baseline A).

Order is deliberate: authorization -> retrieval (FTS over authorized set only)
-> lifecycle/authority -> applicability -> change correlation -> validation.
"""
import json, re, sqlite3, hashlib
from datetime import datetime, timedelta

CHANGE_LOOKBACK = timedelta(hours=24)
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


def classify_runbook(d, inc, catalog):
    """Return (label, reason). Authority and applicability kept as separate checks."""
    at = _dt(inc["opened_at"])
    if d["approval_state"] == "draft":
        return "excluded", "draft: not approved guidance"
    if d["approval_state"] in ("superseded", "deprecated"):
        return "historical", f'{d["approval_state"]} (superseded_by={d.get("superseded_by")})'
    ef, et = _dt(d.get("effective_from")), _dt(d.get("effective_to"))
    if (ef and at < ef) or (et and at >= et):
        return "historical", "outside effective window at incident time"
    inc_svc = resolve_service(inc.get("service"), catalog)
    if d.get("service") is None or d.get("environment") is None or inc_svc is None or not inc.get("environment"):
        return "applicability_unknown", "service/environment could not be established; not treated as authoritative"
    if d["service"] != inc_svc or d["environment"] != inc["environment"]:
        return "excluded", "not applicable to this service/environment"
    return "current_guidance", "approved, in effective window, service and environment match"


def investigate(corpus, user, incident, trace=None):
    catalog = corpus["service_catalog"]
    visible = authorize(corpus["docs"], user)
    hits = retrieve([d for d in visible if d["type"] in ("runbook", "incident")],
                    incident["summary"] + " " + (incident.get("service") or ""))
    if trace is not None:  # eval-only; never part of user-visible output
        trace["retrieved"] = [d["id"] for d in hits]
    out = {"incident_id": incident["id"], "facts": [], "applicable_runbook": None,
           "applicability_flags": [], "historical": [], "hypotheses": [],
           "missing_information": [], "status": "ok", "manifest": []}
    out["facts"].append({"claim": f'Incident opened at {incident["opened_at"]}; service={incident.get("service")}; '
                                  f'environment={incident.get("environment")}.', "evidence": []})
    current = []
    for d in hits:
        if d["type"] == "incident":
            out["historical"].append({"id": d["id"], "note": "historical incident, not current guidance"})
            out["manifest"].append(d["id"]); continue
        label, reason = classify_runbook(d, incident, catalog)
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
        if ct and timedelta(0) <= at - ct <= CHANGE_LOOKBACK:
            mins = int((at - ct).total_seconds() // 60)
            out["facts"].append({"claim": f'{d["title"]} occurred {mins} minutes before the incident opened.', "evidence": [d["id"]]})
            out["hypotheses"].append({"claim": f'The change {d["id"]} may have contributed; causality is not established.',
                                      "supporting": [d["id"]],
                                      "needed_to_test": ["error onset time vs deploy completion", "error signature diff between versions", "rollback or canary result"]})
            out["manifest"].append(d["id"])
    if out["applicable_runbook"] is None and not out["hypotheses"] and not out["historical"]:
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
