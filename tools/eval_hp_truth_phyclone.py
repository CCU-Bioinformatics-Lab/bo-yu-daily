"""Compare a PhyClone MAP result with the designed HP-aware truth tree.

Reads INPUT_DIR/truth.tsv (from tools/hp_truth_tree_to_phyclone.py) and RUN_DIR/map_table.tsv,
RUN_DIR/map_tree.nwk. Prints, per SNV role, where PhyClone put the 10 replicates and at what
CCF; then the inferred clones with their parent and the roles they hold. Also writes
RUN_DIR/eval_by_role.tsv and RUN_DIR/eval_clones.tsv.

Usage: python3 tools/eval_hp_truth_phyclone.py INPUT_DIR RUN_DIR
"""
import csv
import os
import re
import sys
from collections import Counter, defaultdict


def read_tsv(path):
    with open(path) as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def newick_parents(text):
    """Return {node: parent} for a Newick string with labelled internal nodes."""
    text = re.sub(r":[0-9.eE+-]+", "", text.strip().rstrip(";"))
    parent, stack, i, pending = {}, [], 0, []
    tok = re.compile(r"[^(),]+")
    while i < len(text):
        ch = text[i]
        if ch == "(":
            stack.append([])
            i += 1
        elif ch == ",":
            i += 1
        elif ch == ")":
            i += 1
            m = tok.match(text, i)
            name = m.group(0) if m else f"_anon{i}"
            i = m.end() if m else i
            kids = stack.pop()
            for k in kids:
                parent[k] = name
            (stack[-1] if stack else pending).append(name)
        else:
            m = tok.match(text, i)
            (stack[-1] if stack else pending).append(m.group(0))
            i = m.end()
    return parent


def main(inp, run):
    # SNVs a simulated caller missed (detected = 0) are not in the method input
    truth = {r["mutation_id"]: r for r in read_tsv(os.path.join(inp, "truth.tsv"))
             if r.get("detected", "1") == "1"}
    table = read_tsv(os.path.join(run, "map_table.tsv"))
    with open(os.path.join(run, "map_tree.nwk")) as fh:
        parents = newick_parents(fh.read())

    clone_of = {r["mutation_id"]: r["clone_id"] for r in table}
    # per clone, CCF in each sample (sample order as in the table); shown as "S1/S2/..."
    ccfs_of = defaultdict(dict)
    for r in table:
        ccfs_of[r["clone_id"]][r["sample_id"]] = float(r["ccf"])
    samples = sorted({r["sample_id"] for r in table})
    ccf_of = {c: v[samples[0]] for c, v in ccfs_of.items()}
    ccf_str = {c: "/".join(f"{v[sm]:.2f}" for sm in samples) for c, v in ccfs_of.items()}

    def per_sample(t, col):
        """Truth value in every sample: plain column for the first, _<sample> for the rest."""
        return "/".join(t[col] if i == 0 else t[f"{col}_{sm}"] for i, sm in enumerate(samples))

    by_role = defaultdict(list)
    for mid, t in truth.items():
        by_role[t["role"]].append(clone_of[mid])

    roles_in_clone = defaultdict(Counter)
    for mid, c in clone_of.items():
        roles_in_clone[c][truth[mid]["role"]] += 1

    out = []
    print("role\torigin\torigin_ccf\tcarrier\texpected_f\tinferred_clones (n)\tinferred_ccf")
    for role in sorted(by_role, key=lambda r: int(r[1:])):
        t = next(v for v in truth.values() if v["role"] == role)
        cnt = Counter(by_role[role])
        clones = ", ".join(f"{c}({n})" for c, n in cnt.most_common())
        ccfs = ", ".join(ccf_str[c] for c, _ in cnt.most_common())
        row = [role, t["origin_clone"], per_sample(t, "origin_ccf"),
               per_sample(t, "carrier_fraction"), per_sample(t, "phyclone_ccf_expected"), clones,
               ccfs]
        out.append(row)
        print("\t".join(row))

    with open(os.path.join(run, "eval_by_role.tsv"), "w") as fh:
        fh.write("role\torigin_clone\torigin_ccf\tcarrier_fraction\tphyclone_ccf_expected\t"
                 "inferred_clones\tinferred_ccf\n")
        fh.write("\n".join("\t".join(r) for r in out) + "\n")

    print("\nclone\tparent\tccf\troles")
    rows = []
    for c in sorted(roles_in_clone, key=lambda c: -ccf_of[c]):
        roles = ", ".join(f"{r}×{n}" for r, n in sorted(roles_in_clone[c].items(),
                                                       key=lambda x: int(x[0][1:])))
        row = [c, parents.get(c, "outlier" if c == "-1" else "?"), ccf_str[c], roles]
        rows.append(row)
        print("\t".join(row))
    with open(os.path.join(run, "eval_clones.tsv"), "w") as fh:
        fh.write("clone_id\tparent\tccf\troles\n" + "\n".join("\t".join(r) for r in rows) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
