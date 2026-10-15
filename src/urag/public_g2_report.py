"""Aggregate G2 checkpoints per Amendment 7.5-7.6 (stdlib only).

Refuses to compute (and prints no metrics) unless all 36 expected tasks are present exactly once,
each with the full case set and all five arms. Read once, when complete.
"""
import hashlib, json, os, random, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXPECT = {"levels": [10, 25, 50], "seeds": [11, 12, 13], "modes": ["drop", "corrupt"], "sources": ["S1", "S2"],
          "arms": ["N1", "A", "A2", "N1P", "N1P-closed"]}
REGISTERED_PRIMARY_STYLE = "lead"  # Amendment 9.1; D21 guard against the Amendment 12 deviation
STYLE = "lead" if "--style" in sys.argv and sys.argv[sys.argv.index("--style") + 1] == "lead" else "title"
PARTS = os.path.join(ROOT, "results", "g2_parts" if STYLE == "title" else "g2_parts_lead")


UNRECORDED = []


def load_complete():
    want = {f"{s}_{k}_{m}_{sd}.json" for s in EXPECT["sources"] for k in EXPECT["levels"]
            for m in EXPECT["modes"] for sd in EXPECT["seeds"]}
    have = sorted(f for f in os.listdir(PARTS) if f.endswith(".json")) if os.path.isdir(PARTS) else []
    missing = sorted(want - set(have)); extra = sorted(set(have) - want)
    if extra:
        sys.exit(f"unexpected checkpoint files (possible duplicates): {extra}")
    if missing:
        sys.exit(f"INCOMPLETE: {len(want) - len(missing)}/{len(want)} tasks; not reading results. Missing {len(missing)}.")
    ncases = {}
    for s in EXPECT["sources"]:
        cs = json.load(open(os.path.join(ROOT, "data", "public", f"{s}_cases.json")))
        ncases[s] = {c["id"] for c in cs if c["split"] == "dev"}
    results, digests = [], {}
    for f in sorted(want):
        raw_b = open(os.path.join(PARTS, f), "rb").read()
        digests[f] = hashlib.sha256(raw_b).hexdigest()[:16]
        r = json.loads(raw_b)
        rec = r.get("query_style")  # newer checkpoints may record it; older ones do not
        if rec is not None and rec != STYLE:
            sys.exit(f"{f}: checkpoint records query_style={rec!r} but --style {STYLE!r} was requested")
        if rec is None:
            UNRECORDED.append(f)
        key = f"{r['source']}_{r['level']}_{r['mode']}_{r['seed']}.json"
        if key != f:
            sys.exit(f"{f}: content key {key} does not match file name")
        ids = [row["id"] for row in r["rows"]]
        if len(ids) != len(set(ids)) or set(ids) != ncases[r["source"]]:
            sys.exit(f"{f}: case set mismatch (duplicates or missing cases)")
        for row in r["rows"]:
            if sorted(row["arms"]) != sorted(EXPECT["arms"]):
                sys.exit(f"{f}: incomplete arms for {row['id']}")
        results.append(r)
    return {"arms": EXPECT["arms"], "levels": EXPECT["levels"], "seeds": EXPECT["seeds"], "modes": EXPECT["modes"],
            "results": results, "digests": digests}


raw = load_complete()
ARMS = raw["arms"]
ERR = ("critical", "wrong_doc")
PAIRS = [("A", "N1P"), ("A", "N1P-closed"), ("A2", "N1P"), ("A2", "N1P-closed")]


def metrics(cells):
    n = len(cells)
    ans = [c for c in cells if c["answered"]]
    err = [c for c in ans if c["o"] in ERR]
    return {"n": n, "coverage": len(ans) / n, "critical": sum(c["o"] == "critical" for c in cells) / n,
            "wrong_doc": sum(c["o"] == "wrong_doc" for c in cells) / n, "correct": sum(c["o"] == "correct" for c in cells) / n,
            "silent_error": sum(c["silent"] for c in cells) / n,
            "risk_answered": (len(err) / len(ans)) if ans else 0.0}


def matched(cx, cy, rng, draws=100):
    """Reduce the higher-coverage arm by random abstention to the lower arm's answered count."""
    ax = [c for c in cx if c["answered"]]; ay = [c for c in cy if c["answered"]]
    k = min(len(ax), len(ay))
    def risk(cells):
        return (sum(c["o"] in ERR for c in cells) / len(cells)) if cells else 0.0
    rx = sum(risk(rng.sample(ax, k)) for _ in range(draws)) / draws if len(ax) > k else risk(ax)
    ry = sum(risk(rng.sample(ay, k)) for _ in range(draws)) / draws if len(ay) > k else risk(ay)
    return {"answered_matched": k, "risk_x": rx, "risk_y": ry}


def main():
    if STYLE != REGISTERED_PRIMARY_STYLE:
        print(f"*** SECONDARY RESULT: query style {STYLE!r} is not the registered primary {REGISTERED_PRIMARY_STYLE!r} (Amendments 9.1, 12). Do not use as the gate verdict. ***")
    if UNRECORDED:
        print(f"note: {len(UNRECORDED)}/36 checkpoints do not record their query style; it is taken from the checkpoint directory.")
    out = {"by_mode_level": {}, "verdict": {}}
    rng = random.Random(20261019)
    groups = {}
    for r in raw["results"]:
        groups.setdefault((r["mode"], r["level"]), {}).setdefault(r["seed"], []).extend(r["rows"])
    for (mode, level), by_seed in sorted(groups.items()):
        entry = {"arms": {}, "matched": {}}
        for arm in ARMS:
            ms = [metrics([row["arms"][arm] for row in rows]) for rows in by_seed.values()]
            entry["arms"][arm] = {k: round(sum(m[k] for m in ms) / len(ms), 4) for k in ms[0]}
        for x, y in PAIRS:
            vs = [matched([r["arms"][x] for r in rows], [r["arms"][y] for r in rows], rng) for rows in by_seed.values()]
            entry["matched"][f"{x}|{y}"] = {k: round(sum(v[k] for v in vs) / len(vs), 4) for k in vs[0]}
        out["by_mode_level"][f"{mode}/{level}"] = entry
    # reading rule (7.6): governance arm must beat BOTH filters at matched coverage under both modes
    for gov in ("A", "A2"):
        wins = {}
        for mode in raw["modes"]:
            ok = []
            for level in raw["levels"]:
                m = out["by_mode_level"][f"{mode}/{level}"]["matched"]
                ok.append(all(m[f"{gov}|{f}"]["risk_x"] < m[f"{gov}|{f}"]["risk_y"] for f in ("N1P", "N1P-closed")))
            wins[mode] = ok
        out["verdict"][gov] = {"wins_by_mode_and_level": wins, "favours_governance": all(all(v) for v in wins.values())}
    out["task_digests"] = raw["digests"]
    out["query_style"] = STYLE
    out["is_registered_primary_style"] = STYLE == REGISTERED_PRIMARY_STYLE
    out["checkpoints_without_recorded_style"] = len(UNRECORDED)  # style then rests on the directory it was read from
    json.dump(out, open(os.path.join(ROOT, "results", "public_G2_dev_summary.json" if STYLE == "title" else "public_G2_dev_summary_lead.json"), "w"), indent=1)
    for k, e in out["by_mode_level"].items():
        print(k)
        for arm in ARMS:
            m = e["arms"][arm]
            print(f"  {arm:11s} cov {m['coverage']:.3f} crit {m['critical']:.3f} wrong {m['wrong_doc']:.3f} correct {m['correct']:.3f} silent {m['silent_error']:.3f} risk@ans {m['risk_answered']:.3f}")
        for p, m in e["matched"].items():
            print(f"  matched {p:16s} n={m['answered_matched']:.0f} risk {m['risk_x']:.3f} vs {m['risk_y']:.3f}")
    print(json.dumps(out["verdict"], indent=1))


if __name__ == "__main__":
    main()
