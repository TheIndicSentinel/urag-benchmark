import json
from . import pipeline


def check(case, out):
    e, fails = case["expect"], []
    cur = (out.get("applicable_runbook") or {}).get("id")
    if "current_runbook" in e and cur != e["current_runbook"]:
        fails.append(f"current runbook {cur!r} != {e['current_runbook']!r}")
    for bad in e.get("must_not_current", []):
        if cur == bad:
            fails.append(f"{bad} presented as current")
    blob = json.dumps(out)
    for s in e.get("forbidden_strings", []):
        if s in blob:
            fails.append(f"leak: {s!r}")
    if "hypothesis_evidence" in e and not any(e["hypothesis_evidence"] in h["supporting"] for h in out.get("hypotheses", [])):
        fails.append("deployment not presented as hypothesis")
    if e.get("no_causal_fact") and any("cause" in f["claim"].lower() and "not established" not in f["claim"].lower() for f in out.get("facts", [])):
        fails.append("causal claim stated as fact")
    if e.get("unrelated_change_absent") and e["unrelated_change_absent"] in blob:
        fails.append("unrelated change cited")
    if e.get("flag_applicability_unknown") and not out.get("applicability_flags"):
        fails.append("uncertain applicability not flagged")
    if out.get("status") == "validation_failed":
        fails.append("validator rejected output: " + "; ".join(out["errors"]))
    return fails


def run(corpus, cases):
    rows = []
    for c in cases:
        fails = check(c, pipeline.investigate(corpus, c["user"], c["incident"]))
        rows.append({"id": c["id"], "severity": c["severity"], "pass": not fails, "failures": fails})
    return {"cases": rows, "passed": sum(r["pass"] for r in rows), "total": len(rows)}
