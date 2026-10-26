"""Tree spec and genome replay.

A spec is a clone tree whose edges carry ordered events (SNV roles and allele-specific CN
events). Replaying the events from the root gives each clone's genome: segment -> HP -> copies,
where each copy is the set of SNV roles it carries. Mutation loss, multiplicity and CN timing
all follow from the replay; nothing is written by hand.
"""
from dataclasses import dataclass
from pathlib import Path

import yaml

HPS = ("HP1", "HP2")
NORMAL = "N"
DATA_DIR = Path(__file__).parent / "data"

Genome = dict[str, dict[str, tuple[frozenset[str], ...]]]  # segment -> HP -> copies


@dataclass(frozen=True)
class Segment:
    id: str
    chrom: str
    start: int
    length: int

    @property
    def end(self):
        return self.start + self.length


@dataclass(frozen=True)
class SNVRole:
    """`count` SNVs that share one origin, HP, segment and copy, so they share a CN history."""
    id: str
    clone: str
    hp: str
    segment: str
    count: int
    copy: int = 0


@dataclass(frozen=True)
class CNEvent:
    kind: str  # gain | loss | cnloh
    segment: str
    hp: str    # for cnloh: the HP that is kept
    copy: int = 0


@dataclass(frozen=True)
class Spec:
    name: str
    purity: float
    depth: float
    phased_fraction: float
    read_span: Path
    parent: dict[str, str | None]  # clone -> parent, in topological order
    fraction: dict[str, float]     # clone -> share of tumour cells
    segments: dict[str, Segment]
    edges: dict[str, tuple[SNVRole | CNEvent, ...]]
    # observation errors (v0.2); all 0 reproduces v0.1 byte for byte
    mistag_rate: float = 0.0         # tagged read gets the other HP's tag (whole read)
    switch_rate_per_mb: float = 0.0  # Poisson phase switch points per Mb of segment
    base_error: float = 0.0          # per read and SNV site: allele read as the other allele

    @property
    def root(self):
        return next(c for c, p in self.parent.items() if p is None)

    @property
    def roles(self):
        return {e.id: e for ev in self.edges.values() for e in ev if isinstance(e, SNVRole)}

    def children(self, clone):
        return [c for c, p in self.parent.items() if p == clone]

    def ccf(self, clone):
        return self.fraction[clone] + sum(self.ccf(k) for k in self.children(clone))

    def cell_weight(self):
        """Bulk cell fractions, normal included."""
        return {NORMAL: 1 - self.purity, **{c: self.purity * f for c, f in self.fraction.items()}}


def _event(clone, raw):
    if "snv" in raw:
        return SNVRole(raw["snv"], clone, raw["hp"], raw["segment"], int(raw.get("count", 1)),
                       int(raw.get("copy", 0)))
    kinds = [k for k in ("gain", "loss", "cnloh") if k in raw]
    if len(kinds) != 1:
        raise ValueError(f"edge {clone}: event needs exactly one of snv/gain/loss/cnloh: {raw}")
    k = kinds[0]
    return CNEvent(k, raw[k], raw["keep"] if k == "cnloh" else raw["hp"], int(raw.get("copy", 0)))


def _topological(parent):
    order, todo = [], dict(parent)
    while todo:
        ready = [c for c, p in todo.items() if p is None or p in order]
        if not ready:
            raise ValueError(f"clone tree has a cycle or a missing parent: {todo}")
        for c in ready:
            order.append(c)
            del todo[c]
    return order


def parse_spec(raw, base_dir=Path(".")):
    clones = raw["clones"]
    order = _topological({c: v.get("parent") for c, v in clones.items()})
    parent = {c: clones[c].get("parent") for c in order}
    if sum(p is None for p in parent.values()) != 1:
        raise ValueError("clone tree needs exactly one root")
    fraction = {c: float(clones[c]["fraction"]) for c in order}
    if abs(sum(fraction.values()) - 1) > 1e-6:
        raise ValueError(f"clone fractions sum to {sum(fraction.values())}, not 1")
    segments = {s: Segment(s, v["chrom"], int(v["start"]), int(v["length"]))
                for s, v in raw["segments"].items()}
    edges = {c: tuple(_event(c, e) for e in raw.get("edges", {}).get(c, [])) for c in order}
    unknown = set(raw.get("edges", {})) - set(order)
    if unknown:
        raise ValueError(f"edges for unknown clones: {sorted(unknown)}")
    ids = [e.id for ev in edges.values() for e in ev if isinstance(e, SNVRole)]
    if len(ids) != len(set(ids)):
        raise ValueError("SNV role ids must be unique")
    for ev in edges.values():
        for e in ev:
            if e.segment not in segments:
                raise ValueError(f"unknown segment {e.segment!r} in {e}")
            if e.hp not in HPS:
                raise ValueError(f"HP must be one of {HPS}: {e}")
    span = raw.get("read_span", "hcc1395_ont_t50_n00_read_span.tsv")
    span_path = DATA_DIR / span if (DATA_DIR / span).exists() else base_dir / span
    return Spec(raw["name"], float(raw["purity"]), float(raw["depth"]),
                float(raw.get("phased_fraction", 0.859)), span_path, parent, fraction,
                segments, edges, float(raw.get("mistag_rate", 0)),
                float(raw.get("switch_rate_per_mb", 0)), float(raw.get("base_error", 0)))


def load_spec(path):
    path = Path(path)
    return parse_spec(yaml.safe_load(path.read_text()), path.parent)


def _apply(genome, e):
    seg = dict(genome[e.segment])
    copies = list(seg[e.hp])
    if isinstance(e, CNEvent) and e.kind == "cnloh":
        seg[HPS[1 - HPS.index(e.hp)]] = ()
        copies *= 2
    else:
        if not 0 <= e.copy < len(copies):
            raise ValueError(f"{e}: {e.hp} of segment {e.segment} has {len(copies)} copies")
        if isinstance(e, SNVRole):
            copies[e.copy] = copies[e.copy] | {e.id}
        elif e.kind == "gain":
            copies.append(copies[e.copy])
        else:
            del copies[e.copy]
    seg[e.hp] = tuple(copies)
    genome[e.segment] = seg


def replay(spec) -> dict[str, Genome]:
    """Genome of the normal lineage and of every clone."""
    normal = {s: {h: (frozenset(),) for h in HPS} for s in spec.segments}
    genomes = {NORMAL: normal}
    for c in spec.parent:
        g = dict(genomes[spec.parent[c] or NORMAL])
        for e in spec.edges[c]:
            _apply(g, e)
        genomes[c] = g
    return genomes


def roles_in(genome):
    return {r for seg in genome.values() for cps in seg.values() for cp in cps for r in cp}


def ancestors(spec, clone):
    """The clone and its ancestors, root first."""
    path = []
    while clone:
        path.insert(0, clone)
        clone = spec.parent[clone]
    return path


def lost(spec, genomes):
    """clone -> roles that arose in it or an ancestor but that it no longer carries."""
    out = {}
    for c in spec.parent:
        lineage = set(ancestors(spec, c))
        gone = {r for r, e in spec.roles.items() if e.clone in lineage} - roles_in(genomes[c])
        if gone:
            out[c] = sorted(gone)
    return out
