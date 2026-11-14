"""HG008 (2026-11-13): score haploclone MAP runs against the reference-tree layers (pre-set comparison in README).

For each run: clone tree with CCF and SNV count, where each reference layer (truncal, L111, L48, L16) went,
check 1 (L111 split from truncal as a descendant) and check 2 (layer clone CCF within 0.1 of the cell share).
Between runs: share of SNV pairs whose relation (same clone, ancestor, descendant, other branch) agrees.
Run from repo root: python3 -I lab_report/2026-11-13_hg008_bulk_rebuild/eval_hg008.py LABELS RUN_PREFIX...
(RUN_PREFIX + '_map.tsv' and '_map.nwk' are the `haploclone map` outputs)."""
import csv, sys, collections as co
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from eval_diplosim_haploclone import newick_parents, ancestors  # noqa: E402

CELL = {'truncal': 1.0, 'L111': 111 / 119, 'L48': 48 / 119, 'L16': 16 / 119}
tsv = lambda p: list(csv.DictReader(open(p), delimiter='\t'))


def load(prefix):
    rows = tsv(f'{prefix}_map.tsv')
    clone = {r['mutation_id']: r['clone_id'] for r in rows}
    ccf = {r['clone_id']: float(r['ccf']) for r in rows}
    parent = newick_parents(open(f'{prefix}_map.nwk').read())
    return clone, ccf, parent


def relation(a, b, parent):
    if a == b:
        return 'same'
    if a in ancestors(b, parent):
        return 'anc'
    if b in ancestors(a, parent):
        return 'desc'
    return 'branch'


def report(name, labels, clone, ccf, parent):
    print(f'\n== {name}: {len(set(clone.values()))} clones')
    by = co.defaultdict(co.Counter)
    for m, c in clone.items():
        by[c][labels[m]] += 1
    print('clone\tparent\tCCF\tSNVs\ttruncal\tL111\tL48\tL16\tother_clade\tnone')
    order = sorted(by, key=lambda c: -ccf[c])
    for c in order:
        n = by[c]
        print(f'{c}\t{parent.get(c, "-")}\t{ccf[c]:.3f}\t{sum(n.values())}\t' +
              '\t'.join(str(n[k]) for k in ('truncal', 'L111', 'L48', 'L16', 'other_clade', 'none')))
    major = {}
    for lay in CELL:
        n = co.Counter(clone[m] for m in clone if labels[m] == lay)
        if not n:
            print(f'{lay}: no SNV in input')
            continue
        c, k = n.most_common(1)[0]
        major[lay] = c
        ok = abs(ccf[c] - CELL[lay]) <= 0.1
        print(f'{lay}: {sum(n.values())} SNVs, majority clone {c} ({k}/{sum(n.values())}), CCF {ccf[c]:.3f} vs cells {CELL[lay]:.3f} '
              f'-> check 2 {"match" if ok else "no match"}; spread {dict(n)}')
    if 'truncal' in major and 'L111' in major:
        t, l = major['truncal'], major['L111']
        ok = t != l and t in ancestors(l, parent)
        print(f'check 1 (L111 split from truncal, as its descendant): {"YES" if ok else "NO"} (truncal clone {t}, L111 clone {l})')


def agree(a, b):
    """Share of SNV pairs with the same relation in runs a and b, counted per (clone_a, clone_b) group."""
    (ca, _, pa), (cb, _, pb) = a, b
    g = co.Counter((ca[m], cb[m]) for m in ca if m in cb)
    keys = list(g)
    same = tot = 0
    for i, x in enumerate(keys):
        nx = g[x]
        pairs = nx * (nx - 1) // 2  # both in group x: same/same
        same += pairs
        tot += pairs
        for y in keys[i + 1:]:
            p = nx * g[y]
            tot += p
            same += p * (relation(x[0], y[0], pa) == relation(x[1], y[1], pb))
    return same / tot


def main():
    labels = {r['mutation_id']: r['layer'] for r in tsv(sys.argv[1])}
    runs = {Path(p).name: load(p) for p in sys.argv[2:]}
    for name, r in runs.items():
        report(name, labels, *r)
    print('\npair-relation agreement between runs')
    for x, y in combinations(runs, 2):
        print(f'{x}\t{y}\t{agree(runs[x], runs[y]):.3f}')


if __name__ == '__main__':
    main()
