"""S1 (Kubernetes docs) canonicalizer and mechanical case generator.

Reads only local, untracked extracts. Writes pointer-only cases (no source text).
Run as:  python3 -I src/urag/gen/s1.py  (stdlib only; treats extracted files as data).
All parameters come from configs/generator.json (registered before generation).
"""
import hashlib, json, os, random, re, sqlite3, subprocess, sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CFG = json.load(open(os.path.join(ROOT, "configs", "generator.json")))
S = CFG["sources"]["S1"]
LOCAL = os.path.join(ROOT, ".local_sources")
GIT = os.path.join(LOCAL, "k8s-website.git")
VERSIONS = list(S["versions"])  # ordered
DS = CFG["diff_significance"]; DD = CFG["dedupe"]; SM = CFG["sampling"]


def norm(t):
    t = re.sub(r"\{\{[<%].*?[>%]\}\}", " ", t, flags=re.S)
    t = re.sub(r"[^a-z0-9\s]", " ", t.lower())
    return re.sub(r"\s+", " ", t).strip()


def shingles(t, n=5):
    w = t.split()
    return {" ".join(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}


def jacc(a, b):
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def parse(raw):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    fm, body = (m.group(1), m.group(2)) if m else ("", raw)
    t = re.search(r"^title:\s*(.+)$", fm, re.M)
    title = t.group(1).strip().strip("'\"") if t else None
    return title, norm(body)


def eff_from(v):
    ref = S["versions"][v]
    mb = subprocess.check_output(["git", "--git-dir", GIT, "merge-base", f"refs/heads/{ref}", "refs/heads/main"]).decode().strip()
    d = subprocess.check_output(["git", "--git-dir", GIT, "log", "-1", "--format=%cI", mb]).decode().strip()
    return datetime.fromisoformat(d).astimezone(timezone.utc).replace(tzinfo=None).replace(microsecond=0)


def load_canon():
    windows = {}
    for i, v in enumerate(VERSIONS):
        windows[v] = [eff_from(v), None]
    for i in range(len(VERSIONS) - 1):
        windows[VERSIONS[i]][1] = windows[VERSIONS[i + 1]][0]
    windows[VERSIONS[-1]][1] = datetime(2026, 10, 14)  # retrieval date caps the open window
    docs = {}
    for v in VERSIONS:
        base = os.path.join(LOCAL, "s1", v, "content", "en", "docs")
        for dp, _, fs in os.walk(base):
            for f in fs:
                if not f.endswith(".md"):
                    continue
                p = os.path.join(dp, f)
                rel = os.path.relpath(p, base)
                title, text = parse(open(p, encoding="utf-8", errors="replace").read())
                docs[f"k8s:{rel}@{v}"] = {"id": f"k8s:{rel}@{v}", "path": rel, "version": v, "title": title, "text": text,
                                          "hash": hashlib.sha256(text.encode()).hexdigest()[:16],
                                          "effective_from": windows[v][0].isoformat(), "effective_to": windows[v][1].isoformat()}
    return docs, windows


def cluster_of(path):
    return "/".join(path.split("/")[:2]) if "/" in path else path


def split_of(cluster):
    h = int(hashlib.sha256(f"{CFG['seeds']['split']}|S1|{cluster}".encode()).hexdigest(), 16) % 100
    return "dev" if h < CFG["split"]["dev_fraction"] * 100 else "heldout"


def main():
    docs, windows = load_canon()
    by_path = {}
    for d in docs.values():
        by_path.setdefault(d["path"], {})[d["version"]] = d
    sh = {i: shingles(d["text"], DS["shingle_words"]) for i, d in docs.items()}

    def significant(a, b):
        sa, sb = sh[a["id"]], sh[b["id"]]
        ratio = 1 - jacc(sa, sb)
        changed = len(sa ^ sb)
        return ratio >= DS["min_change_ratio"] and changed >= DS["min_changed_shingles"], round(ratio, 3)

    rng = random.Random(CFG["seeds"]["sampling"])
    cands = []  # (path, version, distractors)
    for path, vs in sorted(by_path.items()):
        if len(vs) < 2:
            continue
        for v, g in sorted(vs.items()):
            if not g["title"] or len(g["text"].split()) < 30:
                continue
            ds = []
            for u, o in vs.items():
                if u == v:
                    continue
                ok, ratio = significant(g, o)
                if ok:
                    ds.append({"id": o["id"], "version": u, "change_ratio": ratio})
            if ds:
                cands.append({"path": path, "version": v, "gold": g["id"], "distractors": ds})
    stats = {"paths_with_multiple_versions": sum(len(v) > 1 for v in by_path.values()), "candidate_gold_docs": len(cands)}
    # one candidate per path (seeded), then dedupe + caps
    per_path = {}
    for c in cands:
        per_path.setdefault(c["path"], []).append(c)
    chosen = []
    for path in sorted(per_path):
        chosen.append(rng.choice(per_path[path]))
    rng.shuffle(chosen)
    seen_hash, kept, kept_sh_by_cluster, per_cluster = set(), [], {}, {}
    drops = {"exact_dup": 0, "near_dup": 0, "cluster_cap": 0}
    for c in chosen:
        g = docs[c["gold"]]; cl = cluster_of(c["path"])
        if g["hash"] in seen_hash:
            drops["exact_dup"] += 1; continue
        if any(jacc(sh[g["id"]], s) >= DD["threshold"] for s in kept_sh_by_cluster.get(cl, [])):
            drops["near_dup"] += 1; continue
        if per_cluster.get(cl, 0) >= DD["per_template_cap_per_cluster"]:
            drops["cluster_cap"] += 1; continue
        seen_hash.add(g["hash"]); kept_sh_by_cluster.setdefault(cl, []).append(sh[g["id"]]); per_cluster[cl] = per_cluster.get(cl, 0) + 1
        c["cluster"] = cl; kept.append(c)
    stats.update({"after_dedupe_and_caps": len(kept), "drops": drops, "clusters": len(per_cluster)})
    # family assignment: disjoint paths, F1 then F2 then F3, each capped
    cap = SM["max_cases_per_family_per_source"]
    margin = timedelta(days=SM["windows_days_margin"])
    # each family is a distinct failure class: seeded independent sample from the deduped pool (Amendment 2)
    fam = {}
    for fname in ("F1_wrong_version", "F2_stale_or_not_yet_effective", "F3_acl_exposure"):
        pool = list(kept)
        random.Random(f"{CFG['seeds']['sampling']}|{fname}").shuffle(pool)
        fam[fname] = pool[:cap]
    cases = []
    conn = None
    if fam["F3_acl_exposure"]:  # neutral BM25 over whole corpus for the ACL overlay
        conn = sqlite3.connect(":memory:")
        conn.execute("create virtual table t using fts5(id unindexed, content)")
        conn.executemany("insert into t values (?,?)", [(d["id"], f'{d["title"] or ""} {d["text"]}') for d in docs.values()])
    for fname, items in fam.items():
        for c in items:
            g = docs[c["gold"]]; v = c["version"]
            lo = datetime.fromisoformat(g["effective_from"]) + margin
            hi = datetime.fromisoformat(g["effective_to"]) - margin
            if hi <= lo:
                continue
            T = lo + (hi - lo) * rng.random()
            case = {"id": "S1-" + fname[:2] + "-" + hashlib.sha1(c["gold"].encode()).hexdigest()[:8],
                    "family": fname, "source": "S1", "cluster": c["cluster"], "split": split_of(c["cluster"]),
                    "ticket": {"service": "kubernetes-docs", "opened_at": T.replace(microsecond=0).isoformat()},
                    "query_from": {"field": "title", "doc": c["gold"]},
                    "gold": {"id": c["gold"], "path": c["path"], "version": v},
                    "origin": "mechanical generator configs/generator.json v1"}
            if fname == "F1_wrong_version" or fname == "F3_acl_exposure":
                case["ticket"]["version"] = v
            rel = []
            for d in c["distractors"]:
                if fname == "F1_wrong_version":
                    r = "wrong_version"
                else:
                    r = "superseded" if VERSIONS.index(d["version"]) < VERSIONS.index(v) else "not_yet_effective"
                rel.append({**d, "relation": r})
            case["distractors"] = rel
            if fname == "F3_acl_exposure":
                toks = " OR ".join(w for w in (g["title"] or "").lower().replace("-", " ").split() if re.fullmatch(r"[a-z0-9]+", w))
                rows = conn.execute("select id from t where t match ? order by bm25(t) limit 30", (toks,)).fetchall() if toks else []
                top = next((r[0] for r in rows if docs[r[0]]["path"] != c["path"]), None)
                if not top:
                    continue
                case["restricted_overlay"] = {"doc": top, "group": CFG["acl_simulation"]["restricted_group"]}
                case["expect"] = {"applicable": c["gold"], "forbidden_docs": [top]}
            elif fname == "F1_wrong_version":
                case["expect"] = {"applicable": c["gold"], "critical_if_applicable": [d["id"] for d in rel]}
            else:
                case["expect"] = {"applicable": c["gold"], "critical_if_current": [d["id"] for d in rel]}
            cases.append(case)
    # F4 constructed abstention twins from F1/F2 cases
    r4 = random.Random(CFG["seeds"]["constructed_abstention"])
    base = [c for c in cases if c["family"].startswith(("F1", "F2"))]
    for c in r4.sample(base, k=max(1, round(0.2 * len(base)))):
        t = json.loads(json.dumps(c))
        t["id"] = c["id"].replace("-F1-", "-F4-").replace("-F2-", "-F4-") + "t"; t["family"] = "F4_constructed_abstention"
        t["twin_of"] = c["id"]; t["remove_docs"] = [c["gold"]["id"]]
        t["expect"] = {"applicable": None, "critical_if_applicable": [d["id"] for d in c["distractors"]]}
        t["origin"] += "; constructed (gold removed), synthetic"
        cases.append(t)
    summary = {}
    for c in cases:
        k = (c["family"], c["split"]); summary.setdefault(c["family"], {}).setdefault(c["split"], 0); summary[c["family"]][c["split"]] += 1
    eff = {}
    for fm in {c["family"] for c in cases}:
        eff[fm] = len({c["cluster"] for c in cases if c["family"] == fm})
    out = {"source": "S1", "config_version": CFG["config_version"], "windows": {v: [w[0].isoformat(), w[1].isoformat()] for v, w in windows.items()},
           "stats": stats, "cases_by_family_split": summary, "distinct_clusters_by_family": eff, "n_cases": len(cases)}
    json.dump(cases, open(os.path.join(ROOT, "data", "public", "S1_cases.json"), "w"), indent=1)
    json.dump(out, open(os.path.join(ROOT, "data", "public", "S1_report.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
