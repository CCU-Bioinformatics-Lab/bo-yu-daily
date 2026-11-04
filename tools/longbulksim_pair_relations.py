"""Tree relation of every longbulksim pairs.tsv row, and how often its co-occurrence rule holds.

Relation of the two SNVs' origin clones: same clone, ancestor -> descendant, or different branches.
Rule (only rows whose HP carries both SNVs), with A the ancestor-side SNV and D the other:
  same clone       reads never show one allele without the other (n10 = n01 = 0)
  ancestor -> desc no read shows D alt with A ref
  different branch no read shows both alt (n11 = 0)
A broken rule is checked against truth/genome.json: the forbidden pattern is "possible" when some
copy of that HP in some lineage carries it (e.g. an HP gain before A puts D on a copy without A).

Usage: python3 tools/longbulksim_pair_relations.py SIM_ROOT OUT_DIR
SIM_ROOT holds sim_* directories from python3 -m longbulksim.generate.
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def tsv(path):
    with open(path) as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def ancestors(parent, c):
    out = []
    while parent.get(c) not in (None, "N"):
        c = parent[c]
        out.append(c)
    return out


def patterns(genome, seg, hp, ri, rj):
    """(alt_i, alt_j) patterns present on any copy of this HP in any lineage."""
    return {(ri in cp, rj in cp) for g in genome.values() for cp in map(set, g[seg][hp])}


def one_sim(d):
    truth = {r["mutation_id"]: r for r in tsv(d / "truth/truth.tsv")}
    parent = {r["clone"]: r["parent"] for r in tsv(d / "truth/truth_tree.tsv")}
    genome = json.loads((d / "truth/genome.json").read_text())["genome"]
    rows = []
    for r in tsv(d / "input/pairs.tsv"):
        ti, tj = truth[r["mutation_i"]], truth[r["mutation_j"]]
        ci, cj = ti["origin_clone"], tj["origin_clone"]
        n = {k: int(r[k]) for k in ("n11", "n10", "n01", "n00")}
        on_hp = (ti["hp"] == r["hap"]) + (tj["hp"] == r["hap"])
        if ci == cj:
            rel = "same clone"
        elif ci in ancestors(parent, cj) or cj in ancestors(parent, ci):
            rel = "ancestor-descendant"
        else:
            rel = "different branch"
        trunk = [c for c, p in parent.items() if p == "N"][0]
        kind = ("trunk-trunk" if ci == cj == trunk else
                "trunk-sub" if trunk in (ci, cj) else "sub-sub")
        out = {"sim": d.name, "rel": rel, "kind": kind, "on_hp": on_hp,
               "reads": sum(n.values()), "distance": int(r["distance"]), **n}
        if on_hp == 2:
            pats = patterns(genome, ti["segment"], r["hap"], ti["role"], tj["role"])
            if rel == "same clone":
                forbid = [("n10", (True, False)), ("n01", (False, True))]
            elif rel == "ancestor-descendant":
                # D alt, A ref: n01 when i is the ancestor side, n10 when j is
                forbid = [("n01", (False, True))] if ci in ancestors(parent, cj) else [("n10", (True, False))]
            else:
                forbid = [("n11", (True, True))]
            out["holds"] = all(n[k] == 0 for k, _ in forbid)
            out["possible"] = any(p in pats for _, p in forbid)
            out["forbidden_reads"] = sum(n[k] for k, _ in forbid)
        rows.append(out)
    return rows, len(parent), sum(1 for p in parent.values() if p != "N")


def main():
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    rows, sims = [], []
    for d in sorted(root.glob("sim_*")):
        r, n_clones, _ = one_sim(d)
        man = json.loads((d / "manifest.json").read_text())
        sims.append({"sim": d.name, "clones": n_clones, "wgd": man.get("wgd"),
                     "snvs": man["n_mutations"], "pair_rows": len(r)})
        rows += r
    keys = ["sim", "rel", "kind", "on_hp", "reads", "distance", "n11", "n10", "n01", "n00",
            "holds", "possible", "forbidden_reads"]
    with open(out / "pair_rows.tsv", "w") as fh:
        w = csv.DictWriter(fh, keys, delimiter="\t", restval="")
        w.writeheader()
        w.writerows(rows)

    lines = [f"sims {len(sims)}, pair rows {len(rows)}",
             "per sim: " + ", ".join(f"{s['sim'][-2:]}:{s['clones']}c/{s['pair_rows']}" for s in sims)]
    both = [r for r in rows if r["on_hp"] == 2]
    lines.append(f"rows with both SNVs on the row's HP: {len(both)} ({len(both) / len(rows):.1%}); "
                 f"one: {sum(r['on_hp'] == 1 for r in rows)}; none: {sum(r['on_hp'] == 0 for r in rows)}")
    lines.append("\nrelation x kind (rows with both SNVs on the HP)")
    c = Counter((r["rel"], r["kind"]) for r in both)
    for (rel, kind), k in sorted(c.items()):
        sub = [r for r in both if r["rel"] == rel and r["kind"] == kind]
        reads = sorted(r["reads"] for r in sub)
        lines.append(f"  {rel:20s} {kind:12s} {k:6d} ({k / len(both):6.1%})  median reads {reads[len(reads) // 2]}")
    lines.append("\nrule holds (rows with both SNVs on the HP)")
    by = defaultdict(list)
    for r in both:
        by[r["rel"]].append(r)
    for rel, sub in sorted(by.items()):
        held = sum(r["holds"] for r in sub)
        broken = [r for r in sub if not r["holds"]]
        expl = sum(r["possible"] for r in broken)
        lines.append(f"  {rel:20s} {held}/{len(sub)} ({held / len(sub):.1%}) hold; "
                     f"{len(broken)} broken, {expl} explained by copy structure")
    text = "\n".join(lines)
    (out / "summary.txt").write_text(text + "\n")
    (out / "sims.json").write_text(json.dumps(sims, indent=1))
    print(text)


if __name__ == "__main__":
    main()
