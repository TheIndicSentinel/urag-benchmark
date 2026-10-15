"""Runner for mechanically generated public-source cases (S1 Kubernetes, S2 PostgreSQL).

  python3 -I src/urag/public_eval.py --split dev [--ablate] [--sources S1,S2]
  python3 -I src/urag/public_eval.py --split heldout --confirm-frozen   # once per pipeline hash

Source text is read from untracked local extracts; outputs contain ids only.
Outcome taxonomy is fixed by Amendment 3 of docs/PREREGISTRATION.md.
"""
import argparse, hashlib, json, os, pickle, random, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from urag import pipeline  # noqa: E402
from urag.gen import docs_gen  # noqa: E402

def _cache(sid):
    return os.path.join(ROOT, ".local_sources", f"canon_{sid}.pkl")



ANALYST = {"id": "analyst", "groups": ["it-ops"]}
BOOT_SEED, BOOT_N = 20261018, 2000


def pipeline_manifest(root=ROOT):
    """Amendment 11: files whose bytes define 'the same pipeline' for the one-held-out-run rule."""
    import glob
    rels = ["src/urag/pipeline.py", "src/urag/public_eval.py", "src/urag/gen/docs_gen.py", "configs/generator.json"]
    rels += sorted(os.path.relpath(p, root) for p in glob.glob(os.path.join(root, "data", "public", "*_cases.json")))
    return {r: hashlib.sha256(open(os.path.join(root, r), "rb").read()).hexdigest() for r in sorted(rels)}


def pipeline_digest(manifest):
    return hashlib.sha256("\n".join(f"{p} {h}" for p, h in sorted(manifest.items())).encode()).hexdigest()


# Sources whose held-out split was claimed under digest 8a12b347...; closed permanently even if the log is lost.
SPENT_HELDOUT_SOURCES = frozenset({"S1", "S2"})
# Amendment 13a fixed held-out arm list (primary contrast A2P vs N1P; context arms A, AP, N1, N0, N1P-closed)
HELDOUT_ARMS = ["A", "N1", "N0", "N1P", "N1P-closed", "AP", "A2P"]


def claim_heldout_run(root, digest_short):
    """Amendment 11a: atomically claim the single held-out run for this pipeline digest."""
    lock = os.path.join(root, "results", f"HELDOUT_LOCK_{digest_short}")
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        sys.exit(f"held-out already claimed for pipeline digest {digest_short}; a rerun must be logged as an amendment")
    os.write(fd, b"claimed\n"); os.close(fd)
    return lock


def build_base(sid):
    docs_gen.configure(sid)
    svc = docs_gen.META[sid]["service"]
    if os.path.exists(_cache(sid)):
        docs = pickle.load(open(_cache(sid), "rb"))
    else:
        docs, _ = docs_gen.load_canon()
        pickle.dump(docs, open(_cache(sid), "wb"))
    out = []
    for d in docs.values():
        out.append({"id": d["id"], "type": "runbook", "title": d["title"] or d["path"], "body": d["text"],
                    "service": svc, "environment": None, "approval_state": "approved",
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


VARIANTS = {"A2": ("A", {"ranked_alternatives"}), "N1P": ("N1", {"meta_prefilter"}),
            "AP": ("A", {"meta_prefilter"}), "A2P": ("A", {"ranked_alternatives", "meta_prefilter"}),
            "N1P-closed": ("N1", {"meta_prefilter_closed"}),
            "A-S": ("A", {"relevance_floor"}), "A2-S": ("A", {"ranked_alternatives", "relevance_floor"})}
_STOPW = set(pipeline._STOP)


def lead_query(doc, n=15):
    """Amendment 8.2: first n content words of the body after the title."""
    body = doc["body"]
    tn = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", (doc["title"] or "").lower())).strip()
    if tn and body.startswith(tn):
        body = body[len(tn):]
    toks = [w for w in re.findall(r"[a-z0-9]+", body.lower()) if len(w) >= 3 and w not in _STOPW]
    return " ".join(toks[:n])


def run_case(case, base_docs, docs_by_id, arm, disable, query_style="title", ticket_version="__case__"):
    variant = frozenset()
    if arm in VARIANTS:
        arm, v = VARIANTS[arm]; variant = frozenset(v)
    docs = base_docs
    if case.get("restricted_overlay"):
        o = case["restricted_overlay"]["doc"]
        docs = [dict(d, acl_groups=[case["restricted_overlay"]["group"]]) if d["id"] == o else d for d in docs]
    if case.get("remove_docs"):
        rm = set(case["remove_docs"])
        docs = [d for d in docs if d["id"] not in rm]
    svc = docs_by_id[case["query_from"]["doc"]]["service"]
    corpus = {"service_catalog": {svc: []}, "environment_aliases": {}, "applicability_dims": ["service", "version"],
              "cache_index": True, "docs": docs}
    gold_doc = docs_by_id[case["query_from"]["doc"]]
    title = gold_doc["title"] if query_style == "title" else lead_query(gold_doc)
    ver = case["ticket"].get("version") if ticket_version == "__case__" else ticket_version
    inc = {"id": case["id"], "summary": title, "service": svc, "environment": None,
           "opened_at": case["ticket"]["opened_at"], "version": ver}
    tr = {}
    out = pipeline.investigate(corpus, ANALYST, inc, trace=tr, arm=arm, disable=frozenset(disable), variant=variant)
    return classify(case, out), out, tr.get("retrieved", [])


def equivalent(case, out, change_ratio_by_id):
    """Sensitivity (Amendment 4): same path as gold, other version, change below significance threshold."""
    a = (out.get("applicable_runbook") or {}).get("id")
    if a is None or case["family"].startswith("F4"):
        return False
    gp = case["gold"]["path"]
    if a.split("@")[0] != case["gold"]["id"].split("@")[0]:
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
        for x_, y_ in (("A", "N1"), ("A2", "N1"), ("AP", "N1P"), ("A2P", "N1P"), ("A2", "N1P"), ("A2", "N1P-closed"), ("A-S", "A"), ("A2-S", "A2")):
            if x_ in entry and y_ in entry:
                pairs = [(r["cluster"], int(r["outcomes"][x_] != "correct"), int(r["outcomes"][y_] != "correct")) for r in fr]
                entry[f"{x_}_minus_{y_}"] = boot_ci(pairs)
                cpairs = [(r["cluster"], int(r["outcomes"][x_] == "critical"), int(r["outcomes"][y_] == "critical")) for r in fr]
                entry[f"{x_}_minus_{y_}_critical"] = boot_ci(cpairs)
        if "N1" in entry:
            entry["prevalence_N1_failure"] = entry["N1"]["failure_rate"]
        res[f] = entry
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["dev", "heldout"])
    ap.add_argument("--print-pipeline-digest", action="store_true", help="print D and manifest (Amendment 11); runs nothing")
    ap.add_argument("--ablate", action="store_true")
    ap.add_argument("--sources", default="S1,S2")
    ap.add_argument("--variants", action="store_true", help="also run A2, N1P, AP, A2P (Amendment 6) and N1P-closed, A-S, A2-S (7, 8)")
    ap.add_argument("--query-style", choices=["title", "lead"], default="title")
    ap.add_argument("--confirm-frozen", action="store_true", help="required for heldout")
    ap.add_argument("--limit", type=int, help="dev smoke runs only")
    a = ap.parse_args()
    if a.print_pipeline_digest:
        m = pipeline_manifest()
        print(json.dumps({"pipeline_digest": pipeline_digest(m), "manifest": m}, indent=1))
        return
    if not a.split:
        ap.error("--split is required unless --print-pipeline-digest")
    if a.split == "heldout":
        if a.limit is not None or a.ablate or a.variants or a.query_style != "lead":
            sys.exit("heldout runs use a fixed configuration: --query-style lead, no --limit/--ablate/--variants (Amendment 11b)")
        import glob
        avail = sorted(os.path.basename(f).split("_")[0] for f in glob.glob(os.path.join(ROOT, "data", "public", "*_cases.json")))
        logf = os.path.join(ROOT, "results", "HELDOUT_RUNS.log")
        spent = set(SPENT_HELDOUT_SOURCES)
        if os.path.exists(logf):
            for ln in open(logf):
                if ln.strip():
                    src = json.loads(ln).get("sources", [])
                    spent |= {src} if isinstance(src, str) else set(src)
        req = sorted(a.sources.split(","))
        if set(req) & spent:
            sys.exit(f"heldout sources already claimed in HELDOUT_RUNS.log: {sorted(set(req) & spent)} (Amendment 13a)")
        unspent = sorted(set(avail) - spent)
        if not unspent:
            sys.exit("no unspent held-out sources are available (Amendment 13a)")
        if req != unspent:
            sys.exit(f"heldout sources must be exactly the unspent sources {unspent} (Amendments 11b, 13a)")
    sids = a.sources.split(",")
    cases = []
    for sid in sids:
        cases += [c for c in json.load(open(os.path.join(ROOT, "data", "public", f"{sid}_cases.json"))) if c["split"] == a.split]
    if a.limit:
        cases = cases[:a.limit]
    manifest = pipeline_manifest()
    h = pipeline_digest(manifest)[:16]  # Amendment 11 digest D (short form in outputs)
    log = os.path.join(ROOT, "results", "HELDOUT_RUNS.log")
    if a.split == "heldout":
        if not a.confirm_frozen:
            sys.exit("heldout requires --confirm-frozen")
        if os.path.exists(log) and any(json.loads(l).get("digest", "").startswith(h) for l in open(log) if l.strip()):
            sys.exit(f"held-out already run for pipeline digest {h}; a rerun must be logged as an amendment")
        import datetime
        corpus = {sid: hashlib.sha256(open(_cache(sid), "rb").read()).hexdigest() for sid in sids if os.path.exists(_cache(sid))}
        prereg = hashlib.sha256(open(os.path.join(ROOT, "docs", "PREREGISTRATION.md"), "rb").read()).hexdigest()
        head = subprocess.check_output(["git", "-C", ROOT, "rev-parse", "HEAD"]).decode().strip()
        rec = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "digest": pipeline_digest(manifest),
               "manifest": manifest, "corpus_cache_sha256": corpus, "prereg_sha256": prereg, "git_head": head,
               "sources": sids, "args": {k: v for k, v in vars(a).items()},
               "arms": HELDOUT_ARMS, "status": "claimed-before-evaluation"}
        claim_heldout_run(ROOT, h)
        with open(log, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
    bases = {sid: build_base(sid) for sid in sids}
    by_ids = {sid: {d["id"]: d for d in bases[sid][1]} for sid in sids}
    arms = [("A", [])] + [("N1", []), ("N0", [])]
    if a.split == "heldout":
        arms = [(n, []) for n in HELDOUT_ARMS]  # Amendments 11b, 13a: one fixed list, also written to the log
    if a.variants:
        arms += [(v, []) for v in VARIANTS]
    if a.ablate:
        arms += [("A", [c]) for c in pipeline.CHECKS]
    rows = []
    for c in cases:
        r = {"id": c["id"], "family": c["family"], "source": c["source"], "cluster": f'{c["source"]}:{c["cluster"]}', "outcomes": {}}
        for arm, dis in arms:
            key = arm if not dis else f"A-{dis[0]}"
            oc, out, got = run_case(c, bases[c['source']][1], by_ids[c['source']], arm, dis, a.query_style)
            r["outcomes"][key] = oc
            r.setdefault("equiv", {})[key] = oc == "wrong_doc" and equivalent(c, out, None)
            if not dis:
                gp = c["gold"]["id"].split("@")[0]
                r.setdefault("retrieval", {})[arm] = {"gold_in_top10": c["gold"]["id"] in got,
                                                      "same_path_in_top10": any(x.split("@")[0] == gp for x in got)}
            if arm == "A" and not dis:
                r["status"] = out.get("status")
            if arm in VARIANTS:
                r.setdefault("status_by_arm", {})[arm] = out.get("status")
        rows.append(r)
    summ = summarize(rows)
    out = {"split": a.split, "pipeline_hash": h, "n_cases": len(rows), "sources": sids,
           "g1_status": ("NOT EVALUABLE: %d source(s) (< 3 required); dev/regression evidence only" % len(sids)) if len(sids) < 3
                        else "sources >= 3, but dev split is never G1 evidence; held-out single run required",
           "families": summ, "cases": rows}
    name = f"results/public_{'-'.join(sids)}_{a.split}{'_ablate' if a.ablate else ''}{'_variants' if a.variants else ''}{'_lead' if a.query_style == 'lead' else ''}.json"
    json.dump(out, open(os.path.join(ROOT, name), "w"), indent=1)
    print(json.dumps({"pipeline_hash": h, "families": summ}, indent=1))


if __name__ == "__main__":
    main()
