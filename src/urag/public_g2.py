"""G2 degradation sweep (Amendment 7). Dev split only.

  python3 -I src/urag/public_g2.py [--sources S1,S2] [--workers 4]
"""
import argparse, json, multiprocessing as mp, os, random, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from urag import public_eval as pe  # noqa: E402

ARMS = ["N1", "A", "A2", "N1P", "N1P-closed"]  # adjacent arms share candidate sets (index cache)
LEVELS, SEEDS, MODES = [10, 25, 50], [11, 12, 13], ["drop", "corrupt"]
FIELDS = ["version", "effective_from", "effective_to", "approval_state"]
BASE, BYID, CASES, VERS = {}, {}, {}, {}


def degrade_docs(docs, k, mode, seed):
    rng = random.Random(f"{seed}|{k}|{mode}|docs")
    uni = {f: sorted({d[f] for d in docs if d.get(f) is not None}) for f in FIELDS}
    out = []
    for d in sorted(docs, key=lambda x: x["id"]):
        nd = None
        for f in FIELDS:
            if rng.random() < k / 100.0:
                if nd is None:
                    nd = dict(d)
                if mode == "drop":
                    nd[f] = None
                else:
                    others = [v for v in uni[f] if v != d.get(f)]
                    if others:  # single-valued field (approval_state) -> no-op, as registered
                        nd[f] = others[rng.randrange(len(others))]
        out.append(nd or d)
    return out


def ticket_version(case, k, mode, seed, versions):
    v = case["ticket"].get("version")
    if v is None:
        return None
    rng = random.Random(f"{seed}|{k}|{mode}|{case['id']}")
    if rng.random() < k / 100.0:
        if mode == "drop":
            return None
        others = [x for x in versions if x != v]
        return others[rng.randrange(len(others))]
    return v


PART_DIR = os.path.join(ROOT, "results", "g2_parts")


def task(args):
    sid, k, mode, seed = args
    part = os.path.join(PART_DIR, f"{sid}_{k}_{mode}_{seed}.json")
    if os.path.exists(part):  # resumable
        return json.load(open(part))
    pe.pipeline._INDEX_CACHE_MAX = 2
    docs = degrade_docs(BASE[sid], k, mode, seed)
    rows = []
    for c in CASES[sid]:
        tv = ticket_version(c, k, mode, seed, VERS[sid])
        r = {"id": c["id"], "family": c["family"], "cluster": f'{sid}:{c["cluster"]}', "arms": {}}
        for arm in ARMS:
            oc, out, _ = pe.run_case(c, docs, BYID[sid], arm, [], "title", tv)
            flagged = bool(out.get("applicability_flags")) or out.get("status") not in ("ok", None)
            r["arms"][arm] = {"o": oc, "answered": out.get("applicable_runbook") is not None, "flagged": flagged,
                              "silent": oc in ("critical", "wrong_doc") and not flagged}
        rows.append(r)
    res = {"source": sid, "level": k, "mode": mode, "seed": seed, "rows": rows}
    os.makedirs(PART_DIR, exist_ok=True)
    json.dump(res, open(part + ".tmp", "w")); os.replace(part + ".tmp", part)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", default="S1,S2")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    sids = a.sources.split(",")
    for sid in sids:
        docs, base = pe.build_base(sid)
        BASE[sid] = base
        BYID[sid] = {d["id"]: d for d in base}
        VERS[sid] = sorted({d["version"] for d in base})
        cs = [c for c in json.load(open(os.path.join(ROOT, "data", "public", f"{sid}_cases.json"))) if c["split"] == "dev"]
        CASES[sid] = cs[:a.limit] if a.limit else cs
    tasks = [(s, k, m, sd) for s in sids for k in LEVELS for m in MODES for sd in SEEDS]
    with mp.get_context("fork").Pool(a.workers) as pool:
        res = pool.map(task, tasks, chunksize=1)
    json.dump({"arms": ARMS, "levels": LEVELS, "seeds": SEEDS, "modes": MODES, "fields": FIELDS, "results": res},
              open(os.path.join(ROOT, "results", "public_G2_dev_raw.json"), "w"))
    print("tasks", len(res))


if __name__ == "__main__":
    main()
