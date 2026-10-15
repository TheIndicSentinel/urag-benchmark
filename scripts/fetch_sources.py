#!/usr/bin/env python3
"""Rebuild the local, untracked source extracts used by the generators (pointers-only repo).

  python3 -I scripts/fetch_sources.py [--out DIR] [--pg-mirror] [--sources S1,S2]

Reads configs/generator.json (pinned SHAs), creates blob-less bare clones and extracts only the documentation
trees into DIR/s1/<version>/ and DIR/s2/<version>/ (default DIR = <repo>/.local_sources, which is git-ignored).
Every extracted ref is verified against the pinned SHA before use. Extracted files are data: nothing is executed.

--pg-mirror fetches PostgreSQL tags from github.com/postgres/postgres (same objects; upstream
git.postgresql.org was unreliable). The pinned SHA check still applies.
After extraction, regenerate cases and compare:  python3 -I src/urag/gen/docs_gen.py S1 && git diff --exit-code data/public/
"""
import argparse, json, os, shutil, subprocess, sys, tarfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CFG = json.load(open(os.path.join(ROOT, "configs", "generator.json")))


def git(gitdir, *args, check=True):
    return subprocess.run(["git", "--git-dir", gitdir, *args], check=check, capture_output=True, text=True).stdout.strip()


def extract(gitdir, sha, pathspec, dest):
    if os.path.isdir(dest):
        shutil.rmtree(dest)  # never mix files from an earlier run into a verified extraction
    os.makedirs(dest, exist_ok=True)
    p = subprocess.Popen(["git", "--git-dir", gitdir, "archive", sha, pathspec], stdout=subprocess.PIPE)
    with tarfile.open(fileobj=p.stdout, mode="r|") as tf:
        tf.extractall(dest, filter="data")  # refuses absolute paths, links outside dest, etc.
    if p.wait() != 0:
        sys.exit(f"git archive failed for {sha} {pathspec}")


def s1(out):
    c = CFG["sources"]["S1"]
    bare = os.path.join(out, "k8s-website.git")
    if not os.path.isdir(bare):
        subprocess.run(["git", "clone", "--bare", "--filter=blob:none", "--no-tags", c["repo"], bare], check=True)
    for ver, branch in c["versions"].items():
        sha = c["pinned_shas"][branch]
        if git(bare, "cat-file", "-t", sha, check=False) != "commit":
            sys.exit(f"S1 {branch}: pinned commit {sha} not present in clone")
        dest = os.path.join(out, "s1", ver)
        extract(bare, sha, "content/en/docs", dest)
        n = sum(f.endswith(".md") for _, _, fs in os.walk(dest) for f in fs)
        print(f"S1 {ver}: {n} .md files @ {sha[:10]}")


def s2(out, mirror):
    c = CFG["sources"]["S2"]
    bare = os.path.join(out, "pg.git")
    url = "https://github.com/postgres/postgres.git" if mirror else c["repo"]
    if not os.path.isdir(bare):
        os.makedirs(bare, exist_ok=True)
        git(bare, "init", "--bare", "-q")
    for ver, tag in c["versions"].items():
        want = c["pinned_shas"][tag]
        if git(bare, "rev-parse", "-q", "--verify", f"refs/tags/{tag}^{{commit}}", check=False) != want:
            subprocess.run(["git", "--git-dir", bare, "fetch", "-q", "--depth", "1", url, f"refs/tags/{tag}:refs/tags/{tag}"], check=True)
        got = git(bare, "rev-parse", f"refs/tags/{tag}^{{commit}}")
        if got != want:
            sys.exit(f"S2 {tag}: fetched {got} != pinned {want}")
        dest = os.path.join(out, "s2", ver)
        extract(bare, want, "doc/src/sgml", dest)
        n = sum(f.endswith(".sgml") for f in os.listdir(os.path.join(dest, "doc", "src", "sgml")))
        print(f"S2 {ver}: {n} top-level .sgml files @ {want[:10]}")


def s4(out):
    """S4 Django docs (Amendment 13): depth-1, blob-less fetch of each pinned release-tag commit; docs/ only."""
    c = CFG["sources"]["S4"]
    bare = os.path.join(out, "django.git")
    if not os.path.isdir(bare):
        os.makedirs(bare, exist_ok=True)
        git(bare, "init", "--bare", "-q")
    for ver, sha in c["pinned_shas"].items():
        if git(bare, "cat-file", "-t", sha, check=False) != "commit":
            subprocess.run(["git", "--git-dir", bare, "fetch", "-q", "--depth", "1", "--filter=blob:none", c["repo"], sha], check=True)
        if git(bare, "cat-file", "-t", sha, check=False) != "commit":
            sys.exit(f"S4 {ver}: pinned commit {sha} not present after fetch")
        dest = os.path.join(out, "s4", ver)
        extract(bare, sha, "docs", dest)
        for ex in c.get("exclude_prefixes", []):
            shutil.rmtree(os.path.join(dest, ex.rstrip("/")), ignore_errors=True)
        n = sum(f.endswith(".txt") for _, _, fs in os.walk(os.path.join(dest, "docs")) for f in fs)
        print(f"S4 {ver}: {n} .txt files @ {sha[:10]} (excluded: {c.get('exclude_prefixes')})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, ".local_sources"))
    ap.add_argument("--pg-mirror", action="store_true")
    ap.add_argument("--sources", default="S1,S2", help="S1,S2,S4")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for s in a.sources.split(","):
        {"S1": lambda: s1(a.out), "S2": lambda: s2(a.out, a.pg_mirror), "S4": lambda: s4(a.out)}[s]()
    print("done. Next: python3 -I src/urag/gen/docs_gen.py S1 ; python3 -I src/urag/gen/docs_gen.py S2 ; git diff --exit-code data/public/")


if __name__ == "__main__":
    main()
