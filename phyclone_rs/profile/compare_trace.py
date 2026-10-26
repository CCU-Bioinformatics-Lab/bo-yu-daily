"""Check that a profiled run sampled the same chain as the golden run: every dataset and
attribute in the two trace.h5 files must be equal, except timing fields.

Usage: python phyclone_rs/profile/compare_trace.py A.trace.h5 B.trace.h5
"""
import sys

import h5py
import numpy as np


def walk(f):
    items = {}
    f.visititems(lambda n, o: items.__setitem__(n, o))
    items[""] = f
    return items


def same(x, y):
    x, y = np.asarray(x), np.asarray(y)
    if x.dtype != y.dtype or x.shape != y.shape:
        return False
    if x.dtype.kind == "O" and x.ndim == 0:
        return repr(x.item()) == repr(y.item())
    if x.dtype.kind == "O":
        return all(same(u, v) for u, v in zip(x.ravel(), y.ravel()))
    return x.tobytes() == y.tobytes()


def main(a, b):
    fa, fb = h5py.File(a, "r"), h5py.File(b, "r")
    ia, ib = walk(fa), walk(fb)
    diffs = sorted(set(ia) ^ set(ib))
    n_data = 0
    for name in sorted(set(ia) & set(ib)):
        oa, ob = ia[name], ib[name]
        for k in set(oa.attrs) | set(ob.attrs):
            va, vb = oa.attrs.get(k), ob.attrs.get(k)
            if "time" in k.lower():
                continue
            if not same(va, vb):
                diffs.append(f"{name}@{k}")
        if isinstance(oa, h5py.Dataset):
            if "time" in name.lower():
                continue
            n_data += 1
            if not same(oa[()], ob[()]):
                diffs.append(name)
    print(f"{n_data} datasets compared; {len(diffs)} differ")
    for d in diffs[:20]:
        print("  differs:", d)
    return 1 if diffs else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
