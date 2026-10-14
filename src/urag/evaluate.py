import copy, json
from . import pipeline


def _ids(out):
    ids = set(out.get("manifest", []))
    for h in out.get("hypotheses", []):
        ids |= set(h.get("supporting", []))
    for f in out.get("facts", []):
        ids |= set(f.get("evidence", []))
    return ids


def answered(out):
    return bool(out.get("applicable_runbook") or out.get("hypotheses"))


def should_answer(e):
    return bool(e.get("current_runbook") or e.get("hypotheses_support_exactly") or e.get("hypothesis_evidence"))


def check(case, out, corpus=None):
    e, fails = case["expect"], []
    cur = (out.get("applicable_runbook") or {}).get("id")
    if "current_runbook" in e and cur != e["current_runbook"]:
        fails.append(f"current runbook {cur!r} != {e['current_runbook']!r}")
    for bad in e.get("must_not_current", []):
        if cur == bad:
            fails.append(f"{bad} presented as current")
    if "status" in e and out.get("status") != e["status"]:
        fails.append(f"status {out.get('status')!r} != {e['status']!r}")
    flagged = {f["id"] for f in out.get("applicability_flags", [])}
    for i in e.get("flags_include", []):
        if i not in flagged:
            fails.append(f"{i} not flagged")
    blob = json.dumps(out)
    for s in e.get("forbidden_strings", []):
        if s in blob:
            fails.append(f"leak: {s!r}")
    sup = {s for h in out.get("hypotheses", []) for s in h.get("supporting", [])}
    if "hypothesis_evidence" in e and e["hypothesis_evidence"] not in sup:
        fails.append("deployment not presented as hypothesis")
    if "hypotheses_support_exactly" in e and sup != set(e["hypotheses_support_exactly"]):
        fails.append(f"hypothesis support {sorted(sup)} != {sorted(e['hypotheses_support_exactly'])}")
    for i in e.get("absent_ids", []) + ([e["unrelated_change_absent"]] if e.get("unrelated_change_absent") else []):
        if i in _ids(out) or i in blob:
            fails.append(f"{i} present in output")
    if e.get("no_causal_fact") and any(
            "cause" in f["claim"].lower() and "not established" not in f["claim"].lower()
            for f in out.get("facts", [])):
        fails.append("causal claim stated as fact")
    if e.get("flag_applicability_unknown") and not out.get("applicability_flags"):
        fails.append("uncertain applicability not flagged")
    if "noninterference_remove" in e and corpus is not None:
        c2 = copy.deepcopy(corpus)
        rm = set(e["noninterference_remove"])
        c2["docs"] = [d for d in c2["docs"] if d["id"] not in rm]
        ref = pipeline.investigate(c2, case["user"], case["incident"])
        if ref != out:
            fails.append("output differs from corpus without unauthorized records")
    if out.get("status") == "validation_failed":
        fails.append("validator rejected output: " + "; ".join(out["errors"]))
    return fails


def run(corpus, cases, split=None):
    rows = []
    for c in cases:
        if split and c.get("split", "dev") != split:
            continue
        tr = {}
        out = pipeline.investigate(corpus, c["user"], c["incident"], trace=tr)
        fails = check(c, out, corpus)
        rel = c.get("relevant", [])
        got = tr.get("retrieved", [])
        rec = None if not rel else round(sum(r in got for r in rel) / len(rel), 2)
        rows.append({"id": c["id"], "split": c.get("split", "dev"), "severity": c["severity"], "pass": not fails,
                     "failures": fails, "answered": answered(out), "should_answer": should_answer(c["expect"]),
                     "recall_at_10": rec, "status": out.get("status")})
    n = len(rows)
    ans = [r for r in rows if r["answered"]]
    recs = [r["recall_at_10"] for r in rows if r["recall_at_10"] is not None]
    summary = {
        "n": n, "passed": sum(r["pass"] for r in rows),
        "critical_failures": [r["id"] for r in rows if not r["pass"] and r["severity"] == "critical"],
        "coverage": round(len(ans) / n, 2) if n else None,
        "risk_among_answered": round(sum(not r["pass"] for r in ans) / len(ans), 2) if ans else None,
        "correct_abstentions": sum((not r["answered"]) and (not r["should_answer"]) and r["pass"] for r in rows),
        "unnecessary_abstentions": sum((not r["answered"]) and r["should_answer"] for r in rows),
        "mean_recall_at_10": round(sum(recs) / len(recs), 2) if recs else None,
        "note": "single operating point, small n; not a coverage-risk curve",
    }
    return {"cases": rows, "summary": summary}
