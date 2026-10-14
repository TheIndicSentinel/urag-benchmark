"""Canonicalizer and mechanical case generator for versioned-documentation sources (S1 Kubernetes, S2 PostgreSQL).

Reads only local, untracked extracts. Writes pointer-only cases (no source text).
Run as:  python3 -I src/urag/gen/docs_gen.py S1|S2  (stdlib only; treats extracted files as data).
All parameters come from configs/generator.json (registered before generation).
"""
import hashlib, json, os, random, re, sqlite3, subprocess, sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CFG = json.load(open(os.path.join(ROOT, "configs", "generator.json")))
LOCAL = os.path.join(ROOT, ".local_sources")
SID = S = GIT = VERSIONS = None
NEXT = {}
META = {"S1": {"prefix": "k8s", "service": "kubernetes-docs", "git": "k8s-website.git", "dir": "s1"},
        "S2": {"prefix": "pg", "service": "postgresql-docs", "git": "pg.git", "dir": "s2"}}


def configure(sid):
    global SID, S, GIT, VERSIONS
    SID, S = sid, CFG["sources"][sid]
    GIT = os.path.join(LOCAL, META[sid]["git"])
    VERSIONS = list(S["versions"])
    NEXT.clear()
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


def parse_sgml(raw):
    raw = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)
    m = re.search(r"<title>(.*?)</title>", raw, re.S)
    title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else None
    body = re.sub(r"&[A-Za-z0-9._-]+;", " ", re.sub(r"<[^>]+>", " ", raw))
    return title, norm(body)


def eff_from(v):
    ref = S["versions"][v]
    if SID == "S2":  # tag commit date
        d = subprocess.check_output(["git", "--git-dir", GIT, "log", "-1", "--format=%cI", f"refs/tags/{ref}"]).decode().strip()
        return datetime.fromisoformat(d).astimezone(timezone.utc).replace(tzinfo=None).replace(microsecond=0)
    mb = subprocess.check_output(["git", "--git-dir", GIT, "merge-base", f"refs/heads/{ref}", "refs/heads/main"]).decode().strip()
    d = subprocess.check_output(["git", "--git-dir", GIT, "log", "-1", "--format=%cI", mb]).decode().strip()
    return datetime.fromisoformat(d).astimezone(timezone.utc).replace(tzinfo=None).replace(microsecond=0)


def load_canon():
    cap = datetime(2026, 10, 14)  # retrieval date caps open windows
    windows = {}
    for v in VERSIONS:
        windows[v] = [eff_from(v), None]
    n = S["support_versions"]
    for i, v in enumerate(VERSIONS):
        windows[v][1] = windows[VERSIONS[i + n]][0] if i + n < len(VERSIONS) else cap
    NEXT.update({v: (windows[VERSIONS[i + 1]][0] if i + 1 < len(VERSIONS) else cap) for i, v in enumerate(VERSIONS)})
    docs = {}
    pre = META[SID]["prefix"]
    for v in VERSIONS:
        if SID == "S1":
            base = os.path.join(LOCAL, "s1", v, "content", "en", "docs")
            files = [os.path.join(dp, f) for dp, _, fs in os.walk(base) for f in fs if f.endswith(".md")]
        else:  # S2: top-level doc/src/sgml/*.sgml only (registered path_glob)
            base = os.path.join(LOCAL, "s2", v, "doc", "src", "sgml")
            files = [os.path.join(base, f) for f in os.listdir(base) if f.endswith(".sgml")]
        for p in files:
            if True:
                rel = os.path.relpath(p, base)
                raw = open(p, encoding="utf-8", errors="replace").read()
                title, text = parse(raw) if SID == "S1" else parse_sgml(raw)
                docs[f"{pre}:{rel}@{v}"] = {"id": f"{pre}:{rel}@{v}", "path": rel, "version": v, "title": title, "text": text,
                                          "hash": hashlib.sha256(text.encode()).hexdigest()[:16], "next_release": NEXT[v].isoformat(),
                                          "effective_from": windows[v][0].isoformat(), "effective_to": windows[v][1].isoformat()}
    return docs, windows


def cluster_of(path):
    if SID == "S2":
        return re.split(r"[-.]", path)[0]
    return "/".join(path.split("/")[:2]) if "/" in path else path


def split_of(cluster):
    h = int(hashlib.sha256(f"{CFG['seeds']['split']}|{SID}|{cluster}".encode()).hexdigest(), 16) % 100
    return "dev" if h < CFG["split"]["dev_fraction"] * 100 else "heldout"


def main(sid):
    configure(sid)
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
    last = VERSIONS[-1]

    def build_pool(fname, accept):
        r = random.Random(f"{CFG['seeds']['sampling']}|pool|{fname}")
        per = {}
        for c in cands:
            if accept(c):
                per.setdefault(c["path"], []).append(c)
        chosen = [r.choice(per[p_]) for p_ in sorted(per)]
        r.shuffle(chosen)
        seen, kept_, shs, pc = set(), [], {}, {}
        dr = {"exact_dup": 0, "near_dup": 0, "cluster_cap": 0}
        for c in chosen:
            g = docs[c["gold"]]; cl = cluster_of(c["path"])
            if g["hash"] in seen:
                dr["exact_dup"] += 1; continue
            if any(jacc(sh[g["id"]], x) >= DD["threshold"] for x in shs.get(cl, [])):
                dr["near_dup"] += 1; continue
            if pc.get(cl, 0) >= DD["per_template_cap_per_cluster"]:
                dr["cluster_cap"] += 1; continue
            seen.add(g["hash"]); shs.setdefault(cl, []).append(sh[g["id"]]); pc[cl] = pc.get(cl, 0) + 1
            kept_.append(dict(c, cluster=cl))
        return kept_, dr

    cap = SM["max_cases_per_family_per_source"]
    margin = timedelta(days=SM["windows_days_margin"])
    pools, drops = {}, {}
    pools["F1_wrong_version"], drops["F1_wrong_version"] = build_pool("F1_wrong_version", lambda c: c["version"] != last)
    pools["F2_stale_or_not_yet_effective"], drops["F2_stale_or_not_yet_effective"] = build_pool("F2_stale_or_not_yet_effective", lambda c: True)
    pools["F3_acl_exposure"], drops["F3_acl_exposure"] = build_pool("F3_acl_exposure", lambda c: True)
    stats["pool_sizes"] = {k: len(v) for k, v in pools.items()}
    stats["drops"] = drops
    fam = {k: v[:cap] for k, v in pools.items()}
    cases = []
    conn = None
    if fam["F3_acl_exposure"]:  # neutral BM25 over whole corpus for the ACL overlay
        conn = sqlite3.connect(":memory:")
        conn.execute("create virtual table t using fts5(id unindexed, content)")
        conn.executemany("insert into t values (?,?)", [(d["id"], f'{d["title"] or ""} {d["text"]}') for d in docs.values()])
    for fname, items in fam.items():
        for c in items:
            g = docs[c["gold"]]; v = c["version"]
            if fname == "F1_wrong_version":  # after u+1 is released, before u's end of support
                nxt = datetime.fromisoformat(g["next_release"])
                lo = nxt + margin
                hi = datetime.fromisoformat(g["effective_to"]) - margin
            else:  # v is the latest released version at T
                lo = datetime.fromisoformat(g["effective_from"]) + margin
                hi = datetime.fromisoformat(g["next_release"]) - margin
            if hi <= lo:
                continue
            T = lo + (hi - lo) * rng.random()
            case = {"id": SID + "-" + fname[:2] + "-" + hashlib.sha1(c["gold"].encode()).hexdigest()[:8],
                    "family": fname, "source": SID, "cluster": c["cluster"], "split": split_of(c["cluster"]),
                    "ticket": {"service": META[SID]["service"], "opened_at": T.replace(microsecond=0).isoformat()},
                    "query_from": {"field": "title", "doc": c["gold"]},
                    "gold": {"id": c["gold"], "path": c["path"], "version": v},
                    "origin": "mechanical generator configs/generator.json v1"}
            if fname in ("F1_wrong_version", "F3_acl_exposure"):
                case["ticket"]["version"] = v
            rel = []
            for d in c["distractors"]:
                if fname == "F1_wrong_version":
                    r = "not_yet_effective" if datetime.fromisoformat(docs[d["id"]]["effective_from"]) > T else "wrong_version"
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
    base = [c for c in cases if c["family"].startswith("F1")]  # Amendment 8.4
    for c in r4.sample(base, k=max(1, round(0.2 * len(base)))):
        t = json.loads(json.dumps(c))
        t["id"] = c["id"].replace("-F1-", "-F4-") + "t"; t["family"] = "F4_constructed_abstention"
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
    out = {"source": SID, "config_version": CFG["config_version"], "windows": {v: [w[0].isoformat(), w[1].isoformat()] for v, w in windows.items()},
           "stats": stats, "cases_by_family_split": summary, "distinct_clusters_by_family": eff, "n_cases": len(cases)}
    json.dump(cases, open(os.path.join(ROOT, "data", "public", f"{SID}_cases.json"), "w"), indent=1)
    json.dump(out, open(os.path.join(ROOT, "data", "public", f"{SID}_report.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "S1")
