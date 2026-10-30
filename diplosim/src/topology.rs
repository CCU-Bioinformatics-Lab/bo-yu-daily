//! topology.py: random binary tree over the clone labels, pruned back to n_clones + normal.
use rand::seq::SliceRandom;
use rand::Rng as _;

use crate::Rng;

/// CONIPHER node label (leaves 1..=n, internal nodes and the normal root above).
pub type NodeId = u32;
/// (parent, child).
pub type Edge = (NodeId, NodeId);

#[derive(Clone, Debug)]
pub struct Tree {
    /// Order as CONIPHER keeps it (leaves, internal nodes, root), minus pruned leaves.
    pub nodes: Vec<NodeId>,
    /// Order as CONIPHER keeps it; the last edge is (root, initial_cc).
    pub edges: Vec<Edge>,
    /// The diploid normal.
    pub root: NodeId,
    /// The truncal cancer clone.
    pub initial_cc: NodeId,
    /// Children that are never parents, in edge order (simulate.py:163-164).
    pub leaves: Vec<NodeId>,
}

impl Tree {
    fn new(nodes: Vec<NodeId>, edges: Vec<Edge>, root: NodeId, initial_cc: NodeId) -> Tree {
        let leaves = edges
            .iter()
            .map(|&(_, c)| c)
            .filter(|c| !edges.iter().any(|&(p, _)| p == *c))
            .collect();
        Tree { nodes, edges, root, initial_cc, leaves }
    }

    pub fn children(&self, node: NodeId) -> impl Iterator<Item = NodeId> + '_ {
        self.edges.iter().filter(move |&&(p, _)| p == node).map(|&(_, c)| c)
    }

    /// evolution.py:357 get_descendants(edge)[1:]: the subtree below the edge's child, the child
    /// itself excluded, in pre-order.
    pub fn descendants_below(&self, edge: Edge) -> Vec<NodeId> {
        let mut out = Vec::new();
        let mut stack: Vec<NodeId> = self.children(edge.1).collect();
        stack.reverse();
        while let Some(n) = stack.pop() {
            out.push(n);
            let mut kids: Vec<NodeId> = self.children(n).collect();
            kids.reverse();
            stack.extend(kids);
        }
        out
    }
}

/// topology.py:9 split.
fn split(leaves: &[NodeId], rng: &mut Rng) -> (Vec<NodeId>, Vec<NodeId>) {
    let n = leaves.len();
    let n_ones = rng.gen_range(1..n);
    let mut mask: Vec<bool> = (0..n).map(|i| i < n_ones).collect();
    mask.shuffle(rng);
    let left = leaves.iter().zip(&mask).filter(|(_, &m)| m).map(|(&l, _)| l).collect();
    let right = leaves.iter().zip(&mask).filter(|(_, &m)| !m).map(|(&l, _)| l).collect();
    (left, right)
}

/// topology.py:21 make_tree.
fn make_tree(leaves: &[NodeId], rng: &mut Rng) -> Tree {
    let mut parents = vec![*leaves.iter().max().expect("at least one leaf")];
    let (mut edges, _) = make_tree_internal(leaves, &mut parents, rng);
    let root = parents.last().unwrap() + 1;
    let initial_cc = parents[1];
    edges.push((root, initial_cc));
    let mut nodes = leaves.to_vec();
    nodes.extend_from_slice(&parents[1..]);
    nodes.push(root);
    Tree::new(nodes, edges, root, initial_cc)
}

/// topology.py:32 make_tree_internal. Returns the subtree's edges and its top node.
fn make_tree_internal(leaves: &[NodeId], parents: &mut Vec<NodeId>, rng: &mut Rng) -> (Vec<Edge>, NodeId) {
    if leaves.len() == 1 {
        return (Vec::new(), leaves[0]);
    }
    let current = parents.iter().max().unwrap() + 1;
    parents.push(current);
    let (left, right) = split(leaves, rng);
    let (mut tree, parent_left) = make_tree_internal(&left, parents, rng);
    let (tree_right, parent_right) = make_tree_internal(&right, parents, rng);
    tree.extend(tree_right);
    tree.push((current, parent_left));
    tree.push((current, parent_right));
    (tree, current)
}

/// topology.py:46 prune_tree: drop random leaves until n_nodes + 1 nodes remain.
fn prune_tree(mut tree: Tree, n_nodes: usize, rng: &mut Rng) -> Tree {
    while tree.nodes.len() != n_nodes + 1 {
        let remove = *tree.leaves.choose(rng).expect("tree has leaves");
        tree.nodes.retain(|&n| n != remove);
        let idx = tree.edges.iter().position(|&(_, c)| c == remove).unwrap();
        tree.edges.remove(idx);
        tree = Tree::new(tree.nodes, tree.edges, tree.root, tree.initial_cc);
    }
    tree
}

/// topology.py:64 simulate_topology.
pub fn simulate_topology(n_nodes: usize, rng: &mut Rng) -> Tree {
    let leaves: Vec<NodeId> = (1..=n_nodes as NodeId).collect();
    prune_tree(make_tree(&leaves, rng), n_nodes, rng)
}
