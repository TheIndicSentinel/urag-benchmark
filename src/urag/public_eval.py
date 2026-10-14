"""Runner for mechanically generated public-source cases (S1 so far).

  python3 -I src/urag/public_eval.py --split dev [--ablate]
  python3 -I src/urag/public_eval.py --split heldout --confirm-frozen   # once per pipeline hash

Source text is read from untracked local extracts; outputs contain ids only.
Outcome taxonomy is fixed by Amendment 3 of docs/PREREGISTRATION.md.
"""
import argparse, hashlib, json, os, pickle, random, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from urag import pipeline  # noqa: E402
from urag.gen import s1  # noqa: E402

CACHE = os.path.join(ROOT, ".local_sources", "s1", "canon.pkl")
ANALYST = {"id": "analyst", "groups": ["it-ops"]}
BOOT_SEED, BOOT_N = 20261018, 2000


def build_base():
    if os.path.exists(CACHE):
        docs = pickle.load(open(CACHE, "rb"))
    else:
        docs, _ = s1.load_canon()
        pickle.dump(docs, open(CACHE, "wb"))
    out = []
    for d in docs.values():
        out.append({"id": d["id"], "type": "runbook", "title": d["title"] or d["path"], "body": d["text"],
                    "service": "kubernetes-docs", "environment": None, "approval_state": "approved",
                    "effective_from": d["effective_from"], "effective_to": d["effective_to"],
                    "acl_groups": ["it-ops"], "version": d["version"], "source_version": d["version"],
                    "lineage": d["path"]})
    return docs, out


def classify(case, out):
    a = (out.get("applicable_runbook") or {}).get("id")
    exp = case["expect"]
    dist = {d["id"] for d in case.get("distractors", [])}
    blob = json.dumps(out)
    for f in exp.get("forbidden_docs", []):
        if f in blob:
            return "critical"
    if case["family"].startswith("F4"):
        if a is None:
            return "correct"
        return "critical" if a in dist else "wrong_doc"
    if a == exp["applicable"]:
        return "correct"
    if a is None:
        return "abstained"
    return "critical" if a in dist else "wrong_doc"


def run_case(case, base_docs, docs_by_id, arm, disable):
    docs = base_docs
    if case.get("restricted_overlay"):
        o = case["restricted_overlay"]["doc"]
        docs = [dict(d, acl_groups=[case["restricted_overlay"]["group"]]) if d["id"] == o else d for d in docs]
    if case.get("remove_docs"):
        rm = set(case["remove_docs"])
        docs = [d for d in docs if d["id"] not in rm]
    corpus = {"service_catalog": {"kubernetes-docs": []}, "environment_aliases": {}, "applicability_dims": ["service", "version"],
              "cache_index": True, "docs": docs}
    title = docs_by_id[case["query_from"]["doc"]]["title"]
    inc = {"id": case["id"], "summary": title, "service": "kubernetes-docs", "environment": None,
           "opened_at": case["ticket"]["opened_at"], "version": case["ticket"].get("version")}
    tr = {}
    out = pipeline.investigate(corpus, ANALYST, inc, trace=tr, arm=arm, disable=frozenset(disable))
    return classify(case, out), out, tr.get("retrieved", [])


def equivalent(case, out, change_ratio_by_id):
    """Sensitivity (Amendment 4): same path as gold, other version, change below significance threshold."""
    a = (out.get("applicable_runbook") or {}).get("id")
    if a is None or case["family"].startswith("F4"):
        return False
    gp = case["gold"]["path"]
    if a.split("@")[0] != "k8s:" + gp:
        return False
    return a != case["gold"]["id"] and a not in {d["id"] for d in case.get("distractors", [])}


def boot_ci(pairs):
    """pairs: list of (cluster, a_fail, n1_fail). Cluster bootstrap of mean paired difference."""
    by = {}
    for c, a, n in pairs:
        by.setdefault(c, []).append(a - n)
    cl = list(by.values())
    if len(cl) < 2:
        return None
    rng = random.Random(BOOT_SEED)
    means = []
    for _ in range(BOOT_N):
        samp = [x for _ in cl for x in cl[rng.randrange(len(cl))]]
        means.append(sum(samp) / len(samp))
    means.sort()
    allv = [x for c in cl for x in c]
    return {"mean_diff": round(sum(allv) / len(allv), 4), "ci95": [round(means[int(0.025 * BOOT_N)], 4), round(means[int(0.975 * BOOT_N)], 4)],
            "clusters": len(cl)}


def summarize(rows):
    res = {}
    fams = sorted({r["family"] for r in rows})
    for f in fams:
        fr = [r for r in rows if r["family"] == f]
        entry = {"n": len(fr), "clusters": len({r["cluster"] for r in fr})}
        for arm in sorted({k for r in fr for k in r["outcomes"]}):
            oc = [r["outcomes"][arm] for r in fr]
            eq = [r.get("equiv", {}).get(arm, False) for r in fr]
            entry[arm] = {"failure_rate": round(sum(o != "correct" for o in oc) / len(oc), 3),
                          "failure_rate_equiv_sensitivity": round(sum(o != "correct" and not e for o, e in zip(oc, eq)) / len(oc), 3),
                          "critical": sum(o == "critical" for o in oc), "abstained": sum(o == "abstained" for o in oc),
                          "wrong_doc": sum(o == "wrong_doc" for o in oc)}
        for arm in ("A", "N1", "N0"):
            rt = [r["retrieval"][arm] for r in fr if arm in r.get("retrieval", {})]
            if rt and arm in entry:
                entry[arm]["gold_in_top10"] = round(sum(x["gold_in_top10"] for x in rt) / len(rt), 3)
                entry[arm]["same_path_in_top10"] = round(sum(x["same_path_in_top10"] for x in rt) / len(rt), 3)
        if "A" in entry and "N1" in entry:
            pairs = [(r["cluster"], r["outcomes"]["A"] != "correct", r["outcomes"]["N1"] != "correct") for r in fr]
            entry["A_minus_N1"] = boot_ci([(c, int(a), int(n)) for c, a, n in pairs])
            entry["prevalence_N1_failure"] = entry["N1"]["failure_rate"]
        res[f] = entry
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["dev", "heldout"], required=True)
    ap.add_argument("--ablate", action="store_true")
    ap.add_argument("--confirm-frozen", action="store_true", help="required for heldout")
    ap.add_argument("--limit", type=int, help="dev smoke runs only")
    a = ap.parse_args()
    cases = [c for c in json.load(open(os.path.join(ROOT, "data", "public", "S1_cases.json"))) if c["split"] == a.split]
    if a.limit:
        cases = cases[:a.limit]
    h = hashlib.sha256(open(os.path.join(ROOT, "src/urag/pipeline.py"), "rb").read() +
                       open(os.path.join(ROOT, "src/urag/public_eval.py"), "rb").read()).hexdigest()[:16]
    log = os.path.join(ROOT, "results", "HELDOUT_RUNS.log")
    if a.split == "heldout":
        if not a.confirm_frozen:
            sys.exit("heldout requires --confirm-frozen")
        if os.path.exists(log) and h in open(log).read():
            sys.exit(f"held-out already run for pipeline hash {h}; a rerun must be logged as an amendment")
    docs, base = build_base()
    by_id = {d["id"]: d for d in base}
    arms = [("A", [])] + [("N1", []), ("N0", [])]
    if a.ablate:
        arms += [("A", [c]) for c in pipeline.CHECKS]
    rows = []
    for c in cases:
        r = {"id": c["id"], "family": c["family"], "cluster": c["cluster"], "outcomes": {}}
        for arm, dis in arms:
            key = arm if not dis else f"A-{dis[0]}"
            oc, out, got = run_case(c, base, by_id, arm, dis)
            r["outcomes"][key] = oc
            r.setdefault("equiv", {})[key] = oc == "wrong_doc" and equivalent(c, out, None)
            if not dis:
                gp = "k8s:" + c["gold"]["path"]
                r.setdefault("retrieval", {})[arm] = {"gold_in_top10": c["gold"]["id"] in got,
                                                      "same_path_in_top10": any(x.split("@")[0] == gp for x in got)}
            if arm == "A" and not dis:
                r["status"] = out.get("status")
        rows.append(r)
    summ = summarize(rows)
    out = {"split": a.split, "pipeline_hash": h, "n_cases": len(rows), "sources": ["S1"],
           "g1_status": "NOT EVALUABLE: 1 source (< 3 required); regression/dev evidence only",
           "families": summ, "cases": rows}
    name = f"results/public_S1_{a.split}{'_ablate' if a.ablate else ''}.json"
    json.dump(out, open(os.path.join(ROOT, name), "w"), indent=1)
    if a.split == "heldout":
        open(log, "a").write(f"{h} {subprocess.check_output(['git','-C',ROOT,'rev-parse','HEAD']).decode().strip()}\n")
    print(json.dumps({"pipeline_hash": h, "families": summ}, indent=1))


if __name__ == "__main__":
    main()
