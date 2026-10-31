//! evolution.py: SNV, CNA and WGD events on the tree, and the per-clone genotype they produce.
use std::collections::{BTreeMap, BTreeSet};

use clap::ValueEnum;
use rand::seq::SliceRandom;
use rand::Rng as _;

use crate::params::Params;
use crate::topology::{NodeId, Tree};
use crate::{np_round2, py_float, py_round, Rng};

/// SNV position index (CONIPHER Variant_Position).
pub type Pos = usize;

/// The event names of generate_events (evolution.py:164-181). `dcf_loss_A` and `dcf_cnloh_A`
/// are `LossA`/`CnlohA` applied in `Mode::Dcf`.
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, ValueEnum)]
pub enum Event {
    #[value(skip)]
    Wgd,
    #[value(name = "gain_A")]
    GainA,
    #[value(name = "gain_B")]
    GainB,
    #[value(name = "gain_both")]
    GainBoth,
    #[value(skip)]
    Snv,
    #[value(name = "loss_A")]
    LossA,
    #[value(name = "loss_B")]
    LossB,
    #[value(name = "cnloh_A")]
    CnlohA,
    #[value(name = "cnloh_B")]
    CnlohB,
}

/// Which profile an event updates: `Total` (mutation_node_assignment) or `Dcf`
/// (dcf_mutation_node_assignment, where loss_A and cnloh_A keep the mutated copy count).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Mode {
    Total,
    Dcf,
}

/// `[cnA, cnB, mutated copies]` (evolution.py:115).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Genotype {
    pub a: i32,
    pub b: i32,
    pub mutated: i32,
}

pub const NORMAL: Genotype = Genotype { a: 1, b: 1, mutated: 0 };

impl Genotype {
    fn plus(self, a: i32, b: i32, mutated: i32) -> Genotype {
        Genotype { a: self.a + a, b: self.b + b, mutated: self.mutated + mutated }
    }

    /// The same copies with alleles A and B renamed.
    pub fn swapped(self) -> Genotype {
        Genotype { a: self.b, b: self.a, mutated: self.mutated }
    }
}

impl Event {
    pub fn name(self) -> &'static str {
        match self {
            Event::Wgd => "wgd",
            Event::GainA => "gain_A",
            Event::GainB => "gain_B",
            Event::GainBoth => "gain_both",
            Event::Snv => "snv",
            Event::LossA => "loss_A",
            Event::LossB => "loss_B",
            Event::CnlohA => "cnloh_A",
            Event::CnlohB => "cnloh_B",
        }
    }

    pub fn is_gain(self) -> bool {
        matches!(self, Event::GainA | Event::GainB | Event::GainBoth)
    }

    pub fn is_loss(self) -> bool {
        matches!(self, Event::LossA | Event::LossB | Event::CnlohA | Event::CnlohB)
    }

    /// The event with alleles A and B renamed (gain_A <-> gain_B, loss_A <-> loss_B, ...).
    pub fn mirrored(self) -> Event {
        match self {
            Event::GainA => Event::GainB,
            Event::GainB => Event::GainA,
            Event::LossA => Event::LossB,
            Event::LossB => Event::LossA,
            Event::CnlohA => Event::CnlohB,
            Event::CnlohB => Event::CnlohA,
            e => e,
        }
    }

    /// diplosim: whether a second CNA can follow on a position with these allele copies. A lost
    /// allele cannot be gained or copied back, and the last copy is never lost.
    fn possible_on(self, g: Genotype) -> bool {
        match self {
            Event::GainA => g.a > 0,
            Event::GainB => g.b > 0,
            Event::GainBoth | Event::CnlohA | Event::CnlohB => g.a > 0 && g.b > 0,
            Event::LossA => g.a > 0 && g.a + g.b > 1,
            Event::LossB => g.b > 0 && g.a + g.b > 1,
            Event::Wgd | Event::Snv => false,
        }
    }

    /// evolution.py:164-181 generate_events, one arm per lambda.
    pub fn apply(self, g: Genotype, mode: Mode) -> Genotype {
        let cn_mut = i32::from(g.mutated > 0);
        match (self, mode) {
            (Event::Wgd, _) => Genotype { a: g.a * 2, b: g.b * 2, mutated: g.mutated * 2 },
            (Event::GainA, _) => g.plus(1, 0, cn_mut),
            (Event::GainB, _) => g.plus(0, 1, 0),
            (Event::GainBoth, _) => g.plus(1, 1, cn_mut),
            (Event::Snv, _) => {
                let snv_cn = if g.a != 0 { 1 } else if g.mutated == 0 { 0 } else { -1 };
                g.plus(0, 0, snv_cn)
            }
            (Event::LossB, _) => g.plus(0, -1, 0),
            (Event::CnlohB, _) => g.plus(1, -1, cn_mut),
            (Event::CnlohA, Mode::Total) => g.plus(-1, 1, -cn_mut),
            (Event::CnlohA, Mode::Dcf) => g.plus(-1, 1, 0),
            (Event::LossA, Mode::Total) => g.plus(-1, 0, -cn_mut),
            (Event::LossA, Mode::Dcf) => g.plus(-1, 0, 0),
        }
    }
}

/// Per-edge counts for the `_treeedges.tsv` table (simulate.py:171-177).
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct EdgeLabel {
    pub cna_gains: usize,
    pub cna_losses: usize,
    pub snvs: usize,
    pub wgd: usize,
}

/// One CN event per (node, position): the shape of CONIPHER's overall_cnas.
type CnaMap = BTreeMap<NodeId, BTreeMap<Pos, Event>>;

/// Positions picked for a CN event, with the event each got.
type Picks = Vec<(Pos, Event)>;

/// Everything tree_profiles returns (evolution.py:4-19).
#[derive(Clone, Debug)]
pub struct Evolution {
    /// SNV positions per edge, aligned with `Tree::edges`.
    pub snv_edges: Vec<Vec<Pos>>,
    /// Events per node and position, in the shuffled order they are applied.
    pub events: BTreeMap<NodeId, BTreeMap<Pos, Vec<Event>>>,
    /// Aligned with `Tree::edges`.
    pub edge_labels: Vec<EdgeLabel>,
    pub total: BTreeMap<NodeId, Vec<Genotype>>,
    pub dcf: BTreeMap<NodeId, Vec<Genotype>>,
    pub prop_mutation_loss: f64,
    pub warnings: Vec<String>,
}

/// numpy `choice(xs, k, replace=False)`: k distinct elements in random order.
fn choose_without(xs: &[Pos], k: usize, rng: &mut Rng) -> Vec<Pos> {
    let mut v = xs.to_vec();
    v.partial_shuffle(rng, k).0.to_vec()
}

fn without(xs: &[Pos], drop: &[Pos]) -> Vec<Pos> {
    let drop: BTreeSet<Pos> = drop.iter().copied().collect();
    xs.iter().copied().filter(|p| !drop.contains(p)).collect()
}

/// evolution.py:4 tree_profiles.
pub fn tree_profiles(tree: &Tree, n_positions: usize, p: &Params, rng: &mut Rng) -> Result<Evolution, String> {
    let mut warnings = Vec::new();
    let snv_edges = snv_assignment(tree, n_positions, p.prop_truncal_snvs, p.minimum_branch_length, rng);
    let mut cna = cna_assignment(tree, n_positions, p, &snv_edges, rng, &mut warnings)?;
    let extra = if p.prop_pos_second_cna > 0.0 {
        extra_truncal_cnas(&cna.overall[&tree.initial_cc], p, rng)
    } else {
        BTreeMap::new()
    };
    let (gains, losses) = cna.labels.entry(tree.initial_cc).or_default();
    for ev in extra.values().flatten() {
        if p.gain_events.contains(ev) {
            *gains += 1;
        } else {
            *losses += 1;
        }
    }
    let wgd_nodes = wgd_assignment(tree, &cna.subclone_nodes, p.clonal_wgd, p.subclonal_wgd, p.n_subclonal_wgd, rng);

    let edge_labels = tree
        .edges
        .iter()
        .zip(&snv_edges)
        .map(|(&(_, child), snvs)| {
            let (cna_gains, cna_losses) = cna.labels.get(&child).copied().unwrap_or((0, 0));
            EdgeLabel { cna_gains, cna_losses, snvs: snvs.len(), wgd: usize::from(wgd_nodes.contains(&child)) }
        })
        .collect();

    let events = concat_all_events(tree, n_positions, &cna.overall, &extra, &snv_edges, &wgd_nodes, rng);
    let total = mutation_node_assignment(tree, n_positions, &events, Mode::Total);
    let dcf = mutation_node_assignment(tree, n_positions, &events, Mode::Dcf);
    Ok(Evolution {
        snv_edges,
        events,
        edge_labels,
        total,
        dcf,
        prop_mutation_loss: cna.prop_mutation_loss,
        warnings,
    })
}

/// evolution.py:22 conditioned_choice. `elements` are SNV ids, and the chosen ids are later used
/// as split indices; DECISIONS 2026-10-30 keeps this quirk.
fn conditioned_choice(elements: &[Pos], minimum_distance: usize, n_partitions: usize, rng: &mut Rng) -> Vec<Pos> {
    let mut elements = elements.to_vec();
    let mut chosen: Vec<Pos> = Vec::new();
    for _ in 0..n_partitions {
        let available: Vec<Pos> = elements
            .iter()
            .copied()
            .filter(|&i| chosen.iter().all(|&j| i.abs_diff(j) >= minimum_distance))
            .collect();
        let Some(&choice) = available.choose(rng) else { break };
        chosen.push(choice);
        elements = available;
    }
    chosen
}

/// numpy `split(xs, sorted_indices)`, including indices past the end (empty pieces).
fn np_split(xs: &[Pos], indices: &[Pos]) -> Vec<Vec<Pos>> {
    let mut bounds = vec![0];
    bounds.extend_from_slice(indices);
    bounds.push(xs.len());
    bounds
        .windows(2)
        .map(|w| xs[w[0].min(xs.len())..w[1].min(xs.len())].to_vec())
        .collect()
}

/// evolution.py:35 partition: cut the subclonal SNVs into consecutive pieces, one per
/// non-truncal edge.
fn partition(n_edges: usize, subclonal: &[Pos], minimum_distance: usize, rng: &mut Rng) -> Vec<Vec<Pos>> {
    let n_cuts = n_edges - 2;
    let mut cuts = if minimum_distance == 1 {
        let candidates: Vec<Pos> = (1..subclonal.len().saturating_sub(1)).collect();
        choose_without(&candidates, n_cuts, rng)
    } else {
        conditioned_choice(subclonal, minimum_distance, n_cuts, rng)
    };
    cuts.sort_unstable();
    let parts = np_split(subclonal, &cuts);
    if minimum_distance == 1 {
        assert!(parts.iter().all(|p| !p.is_empty()), "Empty partitions");
    }
    parts
}

/// evolution.py:48 snv_assignment. Returns the SNV positions of each edge, in edge order; the
/// last edge (root -> initial_cc) gets the truncal SNVs.
fn snv_assignment(tree: &Tree, n_positions: usize, prop_truncal: f64, minimum_distance: usize, rng: &mut Rng) -> Vec<Vec<Pos>> {
    let positions: Vec<Pos> = (0..n_positions).collect();
    let n_subclonal = (n_positions as f64 * (1.0 - prop_truncal)) as usize;
    let subclonal = choose_without(&positions, n_subclonal, rng);
    let truncal = without(&positions, &subclonal);
    let n_edges = tree.edges.len();
    let mut parts = partition(n_edges, &subclonal, minimum_distance, rng);
    parts.resize(n_edges - 1, Vec::new());
    parts.push(truncal);
    parts
}

/// evolution.py:64/368 create_event_dict: pick `n` positions and an event for each. CONIPHER also
/// draws events for the remaining positions but only uses their keys, so those draws are skipped.
fn create_event_dict(positions: &[Pos], n: i64, events: &[Event], rng: &mut Rng) -> (Picks, Vec<Pos>) {
    assert!(n >= 0 && n as usize <= positions.len(), "cannot take {n} of {} positions", positions.len());
    let chosen = choose_without(positions, n as usize, rng);
    let remaining = without(positions, &chosen);
    let picked = chosen.into_iter().map(|pos| (pos, *events.choose(rng).unwrap())).collect();
    (picked, remaining)
}

/// evolution.py:75 wgd_assignment. Subclonal WGD nodes are drawn with replacement, so a node
/// drawn twice gets one WGD (kept quirk).
fn wgd_assignment(tree: &Tree, subclone_nodes: &[NodeId], clonal: bool, subclonal: bool, n_subclonal: usize, rng: &mut Rng) -> BTreeSet<NodeId> {
    let mut wgd = BTreeSet::new();
    if clonal {
        wgd.insert(tree.initial_cc);
    }
    if subclonal {
        for _ in 0..n_subclonal {
            wgd.insert(*subclone_nodes.choose(rng).expect("a subclone exists"));
        }
    }
    wgd
}

/// Upper bound on the CNAs `prop_pos_second_cna` adds after a position's first truncal CNA.
const MAX_EXTRA_CNAS: usize = 3;

/// diplosim (not in CONIPHER, which allows one CNA per position): after each truncal CNA, add
/// another one with probability `prop_pos_second_cna`. Gain or loss follows the
/// prop_pos_gained : prop_pos_lost ratio; the event is drawn from gain_events / loss_events
/// among those `possible_on` the copies so far. This gives LOH followed by gains, e.g.
/// cnloh_B then gain_A = (3, 0), which one CNA per position cannot reach.
fn extra_truncal_cnas(truncal: &BTreeMap<Pos, Event>, p: &Params, rng: &mut Rng) -> BTreeMap<Pos, Vec<Event>> {
    let p_gain = p.prop_pos_gained / (p.prop_pos_gained + p.prop_pos_lost);
    let mut extra = BTreeMap::new();
    for (&pos, &first) in truncal {
        let mut g = first.apply(NORMAL, Mode::Total);
        let mut added = Vec::new();
        while added.len() < MAX_EXTRA_CNAS && rng.gen::<f64>() < p.prop_pos_second_cna {
            let pool = if rng.gen::<f64>() < p_gain { &p.gain_events } else { &p.loss_events };
            let possible: Vec<Event> = pool.iter().copied().filter(|e| e.possible_on(g)).collect();
            let Some(&ev) = possible.choose(rng) else { break };
            g = ev.apply(g, Mode::Total);
            added.push(ev);
        }
        if !added.is_empty() {
            extra.insert(pos, added);
        }
    }
    extra
}

/// evolution.py:91 concat_all_events: gather each (node, position)'s events and shuffle them.
/// `extra` CNAs of initial_cc go right after that position's first CNA, in order. The SNV
/// then takes a uniform slot in that CNA run (before, between or after the CNAs), so it can be
/// copied by a later gain; WGD stays where the shuffle put it.
fn concat_all_events(
    tree: &Tree,
    n_positions: usize,
    cnas: &CnaMap,
    extra: &BTreeMap<Pos, Vec<Event>>,
    snv_edges: &[Vec<Pos>],
    wgd_nodes: &BTreeSet<NodeId>,
    rng: &mut Rng,
) -> BTreeMap<NodeId, BTreeMap<Pos, Vec<Event>>> {
    let mut events: BTreeMap<NodeId, BTreeMap<Pos, Vec<Event>>> = BTreeMap::new();
    for (&node, by_pos) in cnas {
        for (&pos, &ev) in by_pos {
            events.entry(node).or_default().entry(pos).or_default().push(ev);
        }
    }
    for (&(_, child), positions) in tree.edges.iter().zip(snv_edges) {
        for &pos in positions {
            events.entry(child).or_default().entry(pos).or_default().push(Event::Snv);
        }
    }
    for &node in wgd_nodes {
        for pos in 0..n_positions {
            events.entry(node).or_default().entry(pos).or_default().push(Event::Wgd);
        }
    }
    for by_pos in events.values_mut() {
        for list in by_pos.values_mut() {
            list.shuffle(rng);
        }
    }
    if let Some(by_pos) = events.get_mut(&tree.initial_cc) {
        for (pos, evs) in extra {
            let list = by_pos.get_mut(pos).expect("extra CNAs follow a truncal CNA");
            let snv = list.iter().position(|&e| e == Event::Snv).map(|i| list.remove(i));
            let first = list.iter().position(|e| e.is_gain() || e.is_loss()).unwrap();
            list.splice(first + 1..first + 1, evs.iter().copied());
            if let Some(snv) = snv {
                list.insert(first + rng.gen_range(0..=evs.len() + 1), snv);
            }
        }
    }
    events
}

/// evolution.py:114 mutation_node_assignment and :143 dcf_mutation_node_assignment. CONIPHER
/// applies a node's events to the node and its whole subtree before visiting the children, so
/// each clone ends with its ancestors' events (top-down) followed by its own; copying the
/// parent's profile and applying the node's events gives the same result.
fn mutation_node_assignment(
    tree: &Tree,
    n_positions: usize,
    events: &BTreeMap<NodeId, BTreeMap<Pos, Vec<Event>>>,
    mode: Mode,
) -> BTreeMap<NodeId, Vec<Genotype>> {
    let mut profiles = BTreeMap::new();
    profiles.insert(tree.root, vec![NORMAL; n_positions]);
    let mut stack = vec![(tree.initial_cc, tree.root)];
    while let Some((node, parent)) = stack.pop() {
        let mut profile = profiles[&parent].clone();
        if let Some(by_pos) = events.get(&node) {
            for (&pos, list) in by_pos {
                profile[pos] = list.iter().fold(profile[pos], |g, ev| ev.apply(g, mode));
            }
        }
        profiles.insert(node, profile);
        stack.extend(tree.children(node).map(|c| (c, node)));
    }
    profiles
}

struct CnaAssignment {
    overall: CnaMap,
    subclone_nodes: Vec<NodeId>,
    /// (CNA gains, CNA losses) per node with an entry in `overall`.
    labels: BTreeMap<NodeId, (usize, usize)>,
    prop_mutation_loss: f64,
}

/// evolution.py:184 cna_assignment.
fn cna_assignment(
    tree: &Tree,
    n_positions: usize,
    p: &Params,
    snv_edges: &[Vec<Pos>],
    rng: &mut Rng,
    warnings: &mut Vec<String>,
) -> Result<CnaAssignment, String> {
    let mut prop_pos_gained = p.prop_pos_gained;
    if np_round2(p.prop_pos_lost + prop_pos_gained) > 1.0 {
        prop_pos_gained = 1.0 - p.prop_pos_lost;
    }
    let subclone_nodes: Vec<NodeId> =
        tree.nodes.iter().copied().filter(|&n| n != tree.root && n != tree.initial_cc).collect();
    let counts = get_npos_cnas(
        n_positions,
        prop_pos_gained,
        p.prop_pos_lost,
        p.prop_gained_truncal,
        p.prop_lost_truncal,
        p.prop_mutloss_positions,
        warnings,
    );
    let root_edge = tree.edges.iter().position(|&(parent, _)| parent == tree.root).unwrap();
    let root_mutations = snv_edges[root_edge].clone();
    let all: Vec<Pos> = (0..n_positions).collect();
    let subclonal_mutations = without(&all, &root_mutations);
    let (mutloss, root_mutations, subclonal_mutations) = get_mutloss(
        tree,
        n_positions,
        &subclone_nodes,
        root_mutations,
        subclonal_mutations,
        counts.mutloss,
        snv_edges,
        p.mutloss_truncal,
        rng,
        warnings,
    );
    let overall = assign_cnas(
        tree,
        n_positions,
        &subclone_nodes,
        snv_edges,
        &root_mutations,
        &subclonal_mutations,
        &counts,
        mutloss,
        &p.gain_events,
        &p.loss_events,
        p.constant_multiplicity,
        rng,
        warnings,
    )?;

    let is_mutloss = |e: &Event| matches!(e, Event::LossA | Event::CnlohA);
    let labels = overall
        .iter()
        .map(|(&node, by_pos)| {
            let gains = by_pos.values().filter(|e| p.gain_events.contains(e)).count();
            let losses = by_pos.values().filter(|e| p.loss_events.contains(e) || is_mutloss(e)).count();
            (node, (gains, losses))
        })
        .collect();
    let n_mutloss_events = overall.values().flat_map(|m| m.values()).filter(|e| is_mutloss(e)).count();
    Ok(CnaAssignment {
        overall,
        subclone_nodes,
        labels,
        prop_mutation_loss: np_round2(n_mutloss_events as f64 / n_positions as f64),
    })
}

struct NposCnas {
    truncal_gain: i64,
    truncal_loss: i64,
    subclonal_gain: i64,
    subclonal_loss: i64,
    mutloss: i64,
}

/// evolution.py:213 get_npos_cnas, with Python's round-half-to-even.
fn get_npos_cnas(
    n_positions: usize,
    prop_pos_gained: f64,
    prop_pos_lost: f64,
    prop_gained_truncal: f64,
    mut prop_lost_truncal: f64,
    prop_mutloss_positions: f64,
    warnings: &mut Vec<String>,
) -> NposCnas {
    let possible_subclone_losses = prop_pos_lost * (1.0 - prop_lost_truncal);
    let use_prop_mutloss_positions = if possible_subclone_losses < prop_mutloss_positions {
        prop_lost_truncal = f64::max(0.0, np_round2(1.0 - (prop_mutloss_positions / prop_pos_lost)));
        warnings.push(format!(
            "WARNING: Due to % mutation losses specified, the proportion of truncal losses is capped to {}",
            py_float(prop_lost_truncal)
        ));
        prop_pos_lost * (1.0 - prop_lost_truncal)
    } else {
        prop_mutloss_positions
    };
    if prop_mutloss_positions > use_prop_mutloss_positions {
        warnings.push(format!(
            "WARNING: Due to % losses, the proportion of mutations lost is capped to {}",
            py_float(use_prop_mutloss_positions)
        ));
    }
    let n = n_positions as f64;
    let mutloss = py_round(n * use_prop_mutloss_positions);
    let mut truncal_gain = py_round(n * prop_pos_gained * prop_gained_truncal);
    let mut subclonal_gain = py_round(n * prop_pos_gained * (1.0 - prop_gained_truncal));
    let mut truncal_loss = py_round(n * prop_pos_lost * prop_lost_truncal);
    let subclonal_loss = py_round(n * prop_pos_lost * (1.0 - prop_lost_truncal)) - mutloss;
    if truncal_gain + subclonal_gain + truncal_loss + subclonal_loss > n_positions as i64 {
        if truncal_loss > 0 {
            truncal_loss -= 1;
        } else if truncal_gain > 0 {
            truncal_gain -= 1;
        } else {
            subclonal_gain -= 1;
        }
    }
    NposCnas { truncal_gain, truncal_loss, subclonal_gain, subclonal_loss, mutloss }
}

/// evolution.py:249 get_mutloss. With mutloss_truncal = false the candidates still include
/// truncal SNVs (evolution.py:267); DECISIONS 2026-10-29 keeps this.
#[allow(clippy::too_many_arguments)]
fn get_mutloss(
    tree: &Tree,
    n_positions: usize,
    subclone_nodes: &[NodeId],
    root_mutations: Vec<Pos>,
    subclonal_mutations: Vec<Pos>,
    n_mutloss_positions: i64,
    snv_edges: &[Vec<Pos>],
    mutloss_truncal: bool,
    rng: &mut Rng,
    warnings: &mut Vec<String>,
) -> (CnaMap, Vec<Pos>, Vec<Pos>) {
    if n_mutloss_positions <= 0 {
        return (CnaMap::new(), root_mutations, subclonal_mutations);
    }
    let k = n_mutloss_positions as usize;
    let leaf_positions: Vec<Pos> = tree
        .edges
        .iter()
        .zip(snv_edges)
        .filter(|((_, child), _)| tree.leaves.contains(child))
        .flat_map(|(_, ps)| ps.iter().copied())
        .collect();
    let all: Vec<Pos> = (0..n_positions).collect();
    let possible = without(&all, &leaf_positions);
    let possible_subclonal = without(&possible, &root_mutations);
    let capped = |warnings: &mut Vec<String>, use_positions: &[Pos]| {
        warnings.push(format!(
            "WARNING: Due to % truncal/subclonal snvs, the proportion of mutations lost is capped to {}",
            py_float(np_round2(use_positions.len() as f64 / n_positions as f64))
        ));
        use_positions.to_vec()
    };
    let mutloss_positions = if mutloss_truncal {
        if k <= root_mutations.len() {
            choose_without(&root_mutations, k, rng)
        } else if possible_subclonal.len() >= k - root_mutations.len() {
            let mut v = root_mutations.clone();
            v.extend(choose_without(&possible_subclonal, k - root_mutations.len(), rng));
            v
        } else {
            capped(warnings, &possible)
        }
    } else if possible.len() >= k {
        choose_without(&possible, k, rng)
    } else {
        capped(warnings, &possible)
    };

    let lost: BTreeSet<Pos> = mutloss_positions.iter().copied().collect();
    let mut out = CnaMap::new();
    for (pos, node) in only_mutloss_cnas(tree, subclone_nodes, &lost, snv_edges, rng) {
        let ev = *[Event::LossA, Event::CnlohA].choose(rng).unwrap();
        out.entry(node).or_default().insert(pos, ev);
    }
    (out, without(&root_mutations, &mutloss_positions), without(&subclonal_mutations, &mutloss_positions))
}

/// evolution.py:286 only_mutloss_cnas: each lost SNV's loss goes to a subclone strictly below
/// the edge that carries the SNV.
fn only_mutloss_cnas(
    tree: &Tree,
    subclone_nodes: &[NodeId],
    lost: &BTreeSet<Pos>,
    snv_edges: &[Vec<Pos>],
    rng: &mut Rng,
) -> Vec<(Pos, NodeId)> {
    let mut out = Vec::new();
    for (&edge, positions) in tree.edges.iter().zip(snv_edges) {
        let below = tree.descendants_below(edge);
        let candidates: Vec<NodeId> = subclone_nodes.iter().copied().filter(|n| below.contains(n)).collect();
        for &pos in positions.iter().filter(|p| lost.contains(p)) {
            out.push((pos, *candidates.choose(rng).expect("a lost SNV sits above a subclone")));
        }
    }
    out
}

/// evolution.py:294 assign_cnas.
#[allow(clippy::too_many_arguments)]
fn assign_cnas(
    tree: &Tree,
    n_positions: usize,
    subclone_nodes: &[NodeId],
    snv_edges: &[Vec<Pos>],
    root_mutations: &[Pos],
    subclonal_mutations: &[Pos],
    counts: &NposCnas,
    mutloss: CnaMap,
    gain_events: &[Event],
    loss_events: &[Event],
    constant_multiplicity: bool,
    rng: &mut Rng,
    warnings: &mut Vec<String>,
) -> Result<CnaMap, String> {
    let (mut tg, mut tl, mut sg, mut sl) =
        (counts.truncal_gain, counts.truncal_loss, counts.subclonal_gain, counts.subclonal_loss);
    let (truncal, subclonal, nodes): (Picks, Picks, BTreeMap<Pos, NodeId>);
    if constant_multiplicity {
        let n_sub = subclonal_mutations.len() as i64;
        if sg + sl > n_sub {
            warnings.push(format!(
                "WARNING: The % subclonal CNAs > % subclonal SNVs and the constant_multiplicity is set to True. The proportion of subclonal CNAs is capped to {}",
                py_float(np_round2(n_sub as f64 / n_positions as f64))
            ));
            let diff = n_sub as f64 / (sg + sl) as f64;
            sg = py_round(sg as f64 * diff);
            sl = py_round(sl as f64 * diff).min(n_sub - sg);
        }
        let (sub_gains, sub_remaining) = create_event_dict(subclonal_mutations, sg, gain_events, rng);
        let (sub_losses, remaining) = create_event_dict(&sub_remaining, sl, loss_events, rng);

        let mut possible_truncal = root_mutations.to_vec();
        possible_truncal.extend(remaining);
        let n_possible = possible_truncal.len() as i64;
        if tg + tl > n_possible {
            warnings.push("WARNING: Capping truncal CNAs!! SEE ERROR".to_string());
            let diff = n_possible as f64 / (tg + tl) as f64;
            tl = py_round(tl as f64 * diff);
            tg = py_round(tg as f64 * diff).min(n_possible - tl);
        }
        let (tr_gains, tr_remaining) = create_event_dict(&possible_truncal, tg, gain_events, rng);
        let (tr_losses, _) = create_event_dict(&tr_remaining, tl, loss_events, rng);

        truncal = [tr_gains, tr_losses].concat();
        subclonal = [sub_gains, sub_losses].concat();
        let cna_positions: BTreeSet<Pos> = subclonal.iter().map(|&(pos, _)| pos).collect();
        nodes = prevent_subclonal_cnas(tree, subclone_nodes, &cna_positions, snv_edges, rng);
    } else {
        let mut use_positions = root_mutations.to_vec();
        use_positions.extend_from_slice(subclonal_mutations);
        if tg + tl + sg + sl > use_positions.len() as i64 {
            return Err(format!(
                "constant_multiplicity=false: {} CNAs for {} positions; CONIPHER prints 'ERROR! ABI FIX!!' and then crashes (evolution.py:333-334)",
                tg + tl + sg + sl,
                use_positions.len()
            ));
        }
        let (tr_gains, rem) = create_event_dict(&use_positions, tg, gain_events, rng);
        let (tr_losses, rem) = create_event_dict(&rem, tl, loss_events, rng);
        let (sub_gains, rem) = create_event_dict(&rem, sg, gain_events, rng);
        let (sub_losses, _) = create_event_dict(&rem, sl, loss_events, rng);
        truncal = [tr_gains, tr_losses].concat();
        subclonal = [sub_gains, sub_losses].concat();
        nodes = subclonal
            .iter()
            .map(|&(pos, _)| (pos, *subclone_nodes.choose(rng).expect("a subclone exists")))
            .collect();
    }

    let mut overall = CnaMap::new();
    for (pos, ev) in subclonal {
        overall.entry(nodes[&pos]).or_default().insert(pos, ev);
    }
    for (node, by_pos) in mutloss {
        overall.entry(node).or_default().extend(by_pos);
    }
    overall.insert(tree.initial_cc, truncal.into_iter().collect());
    Ok(overall)
}

/// evolution.py:350 prevent_subclonal_cnas: a subclonal CNA goes to a subclone outside
/// get_descendants(edge)[1:] of its SNV's edge. The `[1:]` leaves the SNV's own clone eligible
/// (DECISIONS 2026-10-29 keeps this).
fn prevent_subclonal_cnas(
    tree: &Tree,
    subclone_nodes: &[NodeId],
    cna_positions: &BTreeSet<Pos>,
    snv_edges: &[Vec<Pos>],
    rng: &mut Rng,
) -> BTreeMap<Pos, NodeId> {
    let mut out = BTreeMap::new();
    for (&edge, positions) in tree.edges.iter().zip(snv_edges) {
        if edge.0 == tree.root {
            continue;
        }
        let below = tree.descendants_below(edge);
        let candidates: Vec<NodeId> = subclone_nodes.iter().copied().filter(|n| !below.contains(n)).collect();
        for &pos in positions.iter().filter(|p| cna_positions.contains(p)) {
            out.insert(pos, *candidates.choose(rng).expect("the SNV's own clone is a candidate"));
        }
    }
    out
}
