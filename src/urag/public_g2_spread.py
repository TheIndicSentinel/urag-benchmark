"""SUPPLEMENTARY seed-level spread for G2 (not part of the gate; the gate is public_g2_report.py).

  python3 -I src/urag/public_g2_spread.py [--style title|lead]

Refuses to read anything unless all 36 task checkpoints exist. Reports, per (mode, level) and per seed, the
matched-coverage risk gap (filter risk minus governance risk; positive = governance lower), plus min/max
across the 3 seeds and the number of seeds with a positive gap. Descriptive only: no test, no interval,
no change to the registered strict-inequality verdict.
"""
import json, os, random, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STYLE = "lead" if "--style" in sys.argv and sys.argv[sys.argv.index("--style") + 1] == "lead" else "title"
PARTS = os.path.join(ROOT, "results", "g2_parts" if STYLE == "title" else "g2_parts_lead")
LEVELS, SEEDS, MODES, SRC = [10, 25, 50], [11, 12, 13], ["drop", "corrupt"], ["S1", "S2"]
ERR = ("critical", "wrong_doc")
PAIRS = [("A", "N1P"), ("A", "N1P-closed"), ("A2", "N1P"), ("A2", "N1P-closed")]

want = {f"{s}_{k}_{m}_{sd}.json" for s in SRC for k in LEVELS for m in MODES for sd in SEEDS}
have = {f for f in os.listdir(PARTS) if f.endswith(".json")} if os.path.isdir(PARTS) else set()
if have != want:
    sys.exit(f"INCOMPLETE or unexpected files: {len(have & want)}/36 tasks; not reading results.")


def risk(cells):
    return sum(c["o"] in ERR for c in cells) / len(cells) if cells else 0.0


def matched(cx, cy, rng, draws=100):
    ax = [c for c in cx if c["answered"]]; ay = [c for c in cy if c["answered"]]
    k = min(len(ax), len(ay))
    rx = sum(risk(rng.sample(ax, k)) for _ in range(draws)) / draws if len(ax) > k else risk(ax)
    ry = sum(risk(rng.sample(ay, k)) for _ in range(draws)) / draws if len(ay) > k else risk(ay)
    return rx, ry


rng = random.Random(20261020)
out, lines = {}, []
for m in MODES:
    for k in LEVELS:
        for gov, flt in PAIRS:
            gaps = []
            for sd in SEEDS:
                rows = []
                for s in SRC:
                    rows += json.load(open(os.path.join(PARTS, f"{s}_{k}_{m}_{sd}.json")))["rows"]
                rg, rf = matched([r["arms"][gov] for r in rows], [r["arms"][flt] for r in rows], rng)
                gaps.append(round(rf - rg, 4))
            key = f"{m}/{k}/{gov}|{flt}"
            out[key] = {"gaps_by_seed": dict(zip(map(str, SEEDS), gaps)), "mean": round(sum(gaps) / 3, 4),
                        "min": min(gaps), "max": max(gaps), "seeds_positive": sum(g > 0 for g in gaps)}
            lines.append(f"{key:26s} gaps {gaps}  min {min(gaps):+.3f} max {max(gaps):+.3f}  positive {sum(g > 0 for g in gaps)}/3")
print(f"SUPPLEMENTARY seed spread ({STYLE}-style); positive = governance risk lower at matched coverage")
print("\n".join(lines))
json.dump({"label": "supplementary; not a gate", "style": STYLE, "results": out},
          open(os.path.join(ROOT, "results", f"public_G2_dev_spread{'' if STYLE == 'title' else '_lead'}.json"), "w"), indent=1)
