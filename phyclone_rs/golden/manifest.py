"""Write or check MANIFEST.json's inputs_and_runs_sha256: the sha256 of every file under
golden/cases/ and golden/runs/. Other MANIFEST fields are kept as they are.

  manifest.py            rewrite the table from the files on disk
  manifest.py --check    list files whose sha256 differs from MANIFEST.json, and files missing
                         on either side; exit 1 if any
  manifest.py --check --against REV
                         same, against MANIFEST.json at git revision REV (e.g. HEAD), for the
                         files that revision lists; new files are not an error there

Usage (from anywhere): python3 phyclone_rs/golden/manifest.py [--check [--against REV]]
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

G = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(G))
PATH = os.path.join(G, "MANIFEST.json")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def on_disk():
    out = {}
    for top in ("cases", "runs"):
        for d, _, files in os.walk(os.path.join(G, top)):
            for f in files:
                p = os.path.join(d, f)
                out[os.path.relpath(p, ROOT)] = sha256(p)
    return dict(sorted(out.items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--against")
    a = ap.parse_args()
    now = on_disk()
    if not a.check:
        m = json.load(open(PATH))
        m["inputs_and_runs_sha256"] = now
        with open(PATH, "w") as fh:
            json.dump(m, fh, indent=1)
        print(f"{len(now)} files")
        return
    if a.against:
        text = subprocess.run(["git", "show", f"{a.against}:phyclone_rs/golden/MANIFEST.json"],
                              cwd=ROOT, capture_output=True, text=True, check=True).stdout
        ref = json.loads(text)["inputs_and_runs_sha256"]
    else:
        ref = json.load(open(PATH))["inputs_and_runs_sha256"]
    changed = [p for p in ref if p in now and now[p] != ref[p]]
    missing = [p for p in ref if p not in now]
    new = [] if a.against else [p for p in now if p not in ref]
    print(f"{len(ref)} listed, {len(ref) - len(changed) - len(missing)} identical, "
          f"{len(changed)} changed, {len(missing)} missing, {len(new)} not listed")
    for p in changed + missing + new:
        print(f"  {p}")
    sys.exit(1 if changed or missing or new else 0)


if __name__ == "__main__":
    main()
