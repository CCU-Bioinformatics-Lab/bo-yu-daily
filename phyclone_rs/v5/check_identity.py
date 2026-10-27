"""Run a haploclone binary at seed 1 on golden configs and compare each trace directory with the
frozen M7 Rust trace (v3/rust_m7/traces/<config>/seed1), byte for byte; meta.json is compared as
JSON without settings.prior.

Usage: python3 phyclone_rs/v5/check_identity.py BIN OUT [config ...]
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "phyclone_rs", "v3"))
from run_rust import jobs  # noqa: E402

REF = os.path.join(ROOT, "phyclone_rs", "v3", "rust_m7", "traces")
DEFAULT = ["e0_base_bin", "b03_base_err003_hpu", "e0_out001", "fscrp_assign_loss", "upstream_grid1000",
           "real_a2_err004", "e0_out001_fully"]


def meta(path):
    with open(path) as fh:
        m = json.load(fh)
    m.get("settings", {}).pop("prior", None)
    m.pop("command", None)
    return m


def same(a, b):
    with open(a, "rb") as fa, open(b, "rb") as fb:
        return fa.read() == fb.read()


def main():
    binary, out, *configs = sys.argv[1:]
    configs = configs or DEFAULT
    bad = 0
    for d, cmd in jobs(out, [1], binary):
        config = os.path.basename(os.path.dirname(d))
        if config not in configs:
            continue
        os.makedirs(os.path.dirname(d), exist_ok=True)
        t = time.time()
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        secs = time.time() - t
        ref = os.path.join(REF, config, "seed1")
        diffs = []
        for f in sorted(os.listdir(ref)):
            got = os.path.join(d, f)
            if not os.path.exists(got):
                diffs.append(f + " missing")
            elif f == "meta.json":
                if meta(got) != meta(os.path.join(ref, f)):
                    diffs.append(f)
            elif not same(got, os.path.join(ref, f)):
                diffs.append(f)
        bad += bool(diffs)
        print(f"{config}\t{secs:.2f}s\t{'IDENTICAL' if not diffs else 'DIFF ' + ','.join(diffs)}")
    print("ALL IDENTICAL" if not bad else f"{bad} configs differ")
    sys.exit(bool(bad))


if __name__ == "__main__":
    main()
