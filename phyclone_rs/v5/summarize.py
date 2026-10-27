"""Summarise bench.py timings: median and range per (config, impl), and Python / Rust ratios.

The ratio range pairs the slowest Python rep with the fastest Rust rep and the reverse.
Core-hours count wall x chains over complete Python jobs.

Usage: python3 phyclone_rs/v5/summarize.py TIMINGS.tsv [TIMINGS.tsv ...] > summary.tsv
"""
import csv
import statistics
import sys
from collections import defaultdict


def main():
    walls = defaultdict(list)
    chains = {}
    py_core_s = 0.0
    bad = 0
    for path in sys.argv[1:]:
        with open(path) as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                if r["complete"] != "1":
                    bad += 1
                    continue
                walls[r["config"], r["impl"]].append(float(r["wall_s"]))
                chains[r["config"]] = int(r["chains"])
                if r["impl"].startswith("python"):
                    py_core_s += float(r["wall_s"]) * int(r["chains"])
    impls = sorted({i for _, i in walls}, key=lambda i: (not i.startswith("python"), i))
    rust = [i for i in impls if not i.startswith("python")]
    cols = ["config", "chains"]
    for i in impls:
        cols += [f"{i}_n", f"{i}_median_s", f"{i}_min_s", f"{i}_max_s"]
    for i in rust:
        cols += [f"ratio_{i}_median", f"ratio_{i}_low", f"ratio_{i}_high"]
    print("\t".join(cols))
    for config in sorted(chains, key=lambda c: (chains[c], c)):
        row = [config, chains[config]]
        for i in impls:
            w = walls.get((config, i), [])
            row += [len(w)] + ([f"{statistics.median(w):.2f}", f"{min(w):.2f}", f"{max(w):.2f}"]
                               if w else ["", "", ""])
        py = walls.get((config, "python080"), [])
        for i in rust:
            w = walls.get((config, i), [])
            if py and w:
                row += [f"{statistics.median(py) / statistics.median(w):.2f}",
                        f"{min(py) / max(w):.2f}", f"{max(py) / min(w):.2f}"]
            else:
                row += ["", "", ""]
        print("\t".join(map(str, row)))
    print(f"# python core-hours {py_core_s / 3600:.2f}; incomplete jobs {bad}", file=sys.stderr)


if __name__ == "__main__":
    main()
