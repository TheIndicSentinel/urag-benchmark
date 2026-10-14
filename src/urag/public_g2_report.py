"""Aggregate results/public_G2_dev_raw.json per Amendment 7.5-7.6 (stdlib only)."""
import json, os, random, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
raw = json.load(open(os.path.join(ROOT, "results", "public_G2_dev_raw.json")))
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
    json.dump(out, open(os.path.join(ROOT, "results", "public_G2_dev_summary.json"), "w"), indent=1)
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
