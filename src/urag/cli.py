import argparse, json, sys
from . import pipeline


def main(argv=None):
    p = argparse.ArgumentParser(prog="urag")
    p.add_argument("--corpus", default="data/corpus.json")
    p.add_argument("--cases", default="data/cases.json")
    p.add_argument("--case", help="case id to investigate")
    p.add_argument("--eval", action="store_true", help="run all cases against expectations")
    p.add_argument("--prefilter", action="store_true", help="restrict retrieval to resolved service (experimental)")
    p.add_argument("--split", choices=["dev", "heldout"], help="restrict --eval to a split")
    a = p.parse_args(argv)
    corpus = pipeline.load(a.corpus)
    cases = pipeline.load(a.cases)
    if a.case:
        c = next(x for x in cases if x["id"] == a.case)
        print(json.dumps(pipeline.investigate(corpus, c["user"], c["incident"]), indent=2))
        return 0
    if a.eval:
        from .evaluate import run
        res = run(corpus, cases, a.split, a.prefilter)
        print(json.dumps(res, indent=2))
        return 0 if all(r["pass"] for r in res["cases"]) else 1
    p.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
