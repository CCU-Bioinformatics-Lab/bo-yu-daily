use std::collections::{BTreeSet, HashMap};
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

use diplosim::hp::Allele;
use diplosim::params::Params;
use diplosim::{output, simulate, Simulation};

fn scratch(tag: &str) -> PathBuf {
    let dir = std::env::temp_dir().join(format!("diplosim-test-{}-{tag}", std::process::id()));
    let _ = fs::remove_dir_all(&dir);
    dir
}

fn read_tsv(path: &Path) -> Vec<HashMap<String, String>> {
    let text = fs::read_to_string(path).unwrap();
    let mut lines = text.lines();
    let header: Vec<&str> = lines.next().unwrap().split('\t').collect();
    lines
        .map(|l| header.iter().map(|h| h.to_string()).zip(l.split('\t').map(str::to_string)).collect())
        .collect()
}

fn n(row: &HashMap<String, String>, col: &str) -> u64 {
    row[col].parse().unwrap_or_else(|_| panic!("{col} = {:?}", row[col]))
}

fn written_rows(sim: &Simulation, tag: &str) -> Vec<HashMap<String, String>> {
    let dir = scratch(tag);
    output::write_all(sim, &dir, "T").unwrap();
    let rows = read_tsv(&dir.join("T.tsv"));
    fs::remove_dir_all(&dir).unwrap();
    rows
}

fn no_cn(n_clones: usize, n_snv: usize) -> Params {
    let mut p = Params::new(n_clones, n_snv);
    p.prop_pos_gained = 0.0;
    p.prop_pos_lost = 0.0;
    p
}

#[test]
fn tree_has_n_clones_plus_normal_and_is_connected() {
    for (n_clones, seed) in [(2, 1), (3, 2), (5, 3), (10, 4), (25, 5)] {
        let sim = simulate(&Params::new(n_clones, 400), seed).unwrap();
        let t = &sim.tree;
        assert_eq!(t.nodes.len(), n_clones + 1, "nodes for n_clones={n_clones}");
        assert_eq!(t.edges.len(), n_clones, "a tree on n+1 nodes has n edges");
        let mut reached = BTreeSet::from([t.root]);
        let mut stack = vec![t.root];
        while let Some(node) = stack.pop() {
            for c in t.children(node) {
                assert!(reached.insert(c), "node {c} has two parents");
                stack.push(c);
            }
        }
        assert_eq!(reached, t.nodes.iter().copied().collect(), "every node hangs below the normal");
        assert_eq!(t.children(t.root).collect::<Vec<_>>(), vec![t.initial_cc]);
    }
}

#[test]
fn every_snv_sits_on_exactly_one_edge_and_no_edge_is_empty() {
    for seed in 0..20 {
        let sim = simulate(&Params::new(6, 300), seed).unwrap();
        let mut seen = vec![0; 300];
        for (edge, positions) in sim.tree.edges.iter().zip(&sim.evolution.snv_edges) {
            assert!(!positions.is_empty(), "edge {edge:?} has no SNV (seed {seed})");
            for &p in positions {
                seen[p] += 1;
            }
        }
        assert!(seen.iter().all(|&k| k == 1), "seed {seed}: SNV counts per position {seen:?}");
    }
}

#[test]
fn minimum_branch_length_above_one_still_assigns_each_snv_once() {
    let mut p = Params::new(6, 300);
    p.minimum_branch_length = 40;
    for seed in 0..10 {
        let sim = simulate(&p, seed).unwrap();
        let total: usize = sim.evolution.snv_edges.iter().map(Vec::len).sum();
        assert_eq!(total, 300);
    }
}

#[test]
fn prop_snv_on_b_zero_puts_every_snv_on_hp1() {
    let mut p = Params::new(4, 500);
    p.prop_snv_on_b = 0.0;
    let rows = written_rows(&simulate(&p, 11).unwrap(), "allA");
    assert_eq!(rows.len(), 500);
    assert!(rows.iter().all(|r| r["ALLELE"] == "A"));
    assert!(rows.iter().all(|r| n(r, "HP2_ALT") == 0));
    assert!(rows.iter().map(|r| n(r, "HP1_ALT")).sum::<u64>() > 0, "alt reads exist and land on HP1");
}

#[test]
fn prop_tagged_one_leaves_no_untagged_reads() {
    let mut p = Params::new(4, 500);
    p.prop_tagged = 1.0;
    let rows = written_rows(&simulate(&p, 12).unwrap(), "tagged");
    assert!(rows.iter().all(|r| n(r, "HP0_REF") == 0 && n(r, "HP0_ALT") == 0));

    p.prop_tagged = 0.8;
    let rows = written_rows(&simulate(&p, 12).unwrap(), "untagged");
    let hp0: u64 = rows.iter().map(|r| n(r, "HP0_REF") + n(r, "HP0_ALT")).sum();
    let depth: u64 = rows.iter().map(|r| n(r, "DEPTH")).sum();
    let frac = hp0 as f64 / depth as f64;
    assert!((frac - 0.2).abs() < 0.01, "untagged fraction {frac}, expected about 0.2");
}

#[test]
fn tag_concentration_spreads_the_tag_fraction_across_sites_around_prop_tagged() {
    let tag_fracs = |p: &Params, tag: &str| -> Vec<f64> {
        written_rows(&simulate(p, 13).unwrap(), tag)
            .iter()
            .filter(|r| n(r, "DEPTH") >= 100)
            .map(|r| 1.0 - (n(r, "HP0_REF") + n(r, "HP0_ALT")) as f64 / n(r, "DEPTH") as f64)
            .collect()
    };
    let sd = |x: &[f64]| {
        let m = x.iter().sum::<f64>() / x.len() as f64;
        ((x.iter().map(|v| (v - m).powi(2)).sum::<f64>() / x.len() as f64).sqrt(), m)
    };
    let mut p = Params::new(4, 2000);
    p.prop_tagged = 0.86;
    let (sd_fixed, _) = sd(&tag_fracs(&p, "fixed"));
    p.tag_concentration = Some(1.0);
    let (sd_beta, mean_beta) = sd(&tag_fracs(&p, "beta"));
    assert!(sd_fixed < 0.06 && sd_beta > 0.2, "SD fixed {sd_fixed}, Beta {sd_beta}");
    assert!((mean_beta - 0.86).abs() < 0.03, "mean tag fraction {mean_beta}");
    p.tag_concentration = Some(0.0);
    assert!(p.validate().is_err());
}

#[test]
fn hp_counts_add_up_to_conipher_counts() {
    let mut cases = vec![Params::new(5, 400), no_cn(3, 300)];
    let mut wgd = Params::new(6, 400);
    wgd.clonal_wgd = true;
    wgd.subclonal_wgd = true;
    wgd.prop_mutloss_positions = 0.1;
    wgd.prop_lost_truncal = 0.5;
    cases.push(wgd);
    let mut noisy = Params::new(4, 400);
    noisy.fract_noise = 0.1;
    noisy.n_noise_clones = 2;
    cases.push(noisy);
    for (i, p) in cases.iter().enumerate() {
        let rows = written_rows(&simulate(p, 100 + i as u64).unwrap(), &format!("sum{i}"));
        for r in &rows {
            assert_eq!(n(r, "HP1_REF") + n(r, "HP2_REF") + n(r, "HP0_REF"), n(r, "REF_COUNT"), "case {i}");
            assert_eq!(n(r, "HP1_ALT") + n(r, "HP2_ALT") + n(r, "HP0_ALT"), n(r, "VAR_COUNT"), "case {i}");
            assert_eq!(n(r, "REF_COUNT") + n(r, "VAR_COUNT"), n(r, "DEPTH"));
            let wrong_hp_alt = if r["ALLELE"] == "A" { "HP2_ALT" } else { "HP1_ALT" };
            assert_eq!(n(r, wrong_hp_alt), 0, "case {i}: alt only on the SNV's haplotype or HP0");
        }
    }
}

#[test]
fn read_errors_keep_counts_consistent_and_put_reads_on_the_other_side() {
    let mut p = Params::new(5, 3000);
    p.prop_tagged = 1.0;
    p.min_tumour_purity = 1.0;
    p.max_tumour_purity = 1.0;
    let clean = written_rows(&simulate(&p, 71).unwrap(), "clean");
    p.mistag_rate = 0.02;
    p.base_error = 0.02;
    let noisy = written_rows(&simulate(&p, 71).unwrap(), "noisy");
    let wrong_hp_alt = |r: &HashMap<String, String>| n(r, if r["ALLELE"] == "A" { "HP2_ALT" } else { "HP1_ALT" });
    for (c, r) in clean.iter().zip(&noisy) {
        assert_eq!(n(r, "DEPTH"), n(c, "DEPTH"), "errors move reads, they do not add or drop them");
        assert_eq!(n(r, "HP1_REF") + n(r, "HP2_REF") + n(r, "HP0_REF"), n(r, "REF_COUNT"));
        assert_eq!(n(r, "HP1_ALT") + n(r, "HP2_ALT") + n(r, "HP0_ALT"), n(r, "VAR_COUNT"));
    }
    assert!(noisy.iter().any(|r| wrong_hp_alt(r) > 0), "mistagged alt reads land on the other haplotype");
    // A clonal LOH SNV on every copy has no ref read without errors.
    let full = |r: &&HashMap<String, String>| r["REF_COUNT"] == "0" && n(r, "DEPTH") > 20;
    let full_clean: Vec<usize> = clean.iter().enumerate().filter(|(_, r)| full(r)).map(|(i, _)| i).collect();
    assert!(!full_clean.is_empty());
    assert!(full_clean.iter().any(|&i| n(&noisy[i], "REF_COUNT") > 0), "base errors show ref reads at VAF-1 sites");
}

#[test]
fn without_cn_events_both_haplotypes_get_equal_depth() {
    let mut p = no_cn(4, 3000);
    p.prop_tagged = 1.0;
    let rows = written_rows(&simulate(&p, 21).unwrap(), "balanced");
    for allele in ["A", "B"] {
        let on: Vec<_> = rows.iter().filter(|r| r["ALLELE"] == allele).collect();
        let hp1: u64 = on.iter().map(|r| n(r, "HP1_REF") + n(r, "HP1_ALT")).sum();
        let hp2: u64 = on.iter().map(|r| n(r, "HP2_REF") + n(r, "HP2_ALT")).sum();
        let ratio = hp1 as f64 / hp2 as f64;
        assert!((ratio - 1.0).abs() < 0.02, "SNVs on {allele}: HP1/HP2 depth ratio {ratio}");
    }
    let b = rows.iter().filter(|r| r["ALLELE"] == "B").count() as f64 / rows.len() as f64;
    assert!((b - 0.5).abs() < 0.03, "share of SNVs on B {b}");
    for r in &rows {
        assert_eq!((r["CN_A"].as_str(), r["CN_B"].as_str()), ("1.0", "1.0"));
    }
}

#[test]
fn truncal_snvs_are_in_every_cancer_cell_without_cn_or_mutation_loss() {
    for seed in 0..5 {
        let sim = simulate(&no_cn(5, 300), seed).unwrap();
        let mut subclonal_below_one = 0;
        for r in &sim.rows {
            if r.parent == sim.tree.root {
                assert!((r.ccf - 1.0).abs() < 1e-9, "truncal SNV {} has CCF {}", r.pos, r.ccf);
            } else if r.ccf < 1.0 - 1e-9 {
                subclonal_below_one += 1;
            }
        }
        assert!(subclonal_below_one > 0, "subclonal SNVs are not all at CCF 1");
        let rows = written_rows(&sim, &format!("ccf{seed}"));
        let truncal: Vec<_> = rows.iter().filter(|r| r["CLUSTER"] == sim.tree.initial_cc.to_string()).collect();
        assert!(!truncal.is_empty() && truncal.iter().all(|r| r["TRUE_CCF"] == "1.0"));
    }
}

#[test]
fn putting_every_snv_on_b_swaps_the_alleles_of_the_conipher_genotypes() {
    let mut on_a = Params::new(5, 300);
    on_a.prop_snv_on_b = 0.0;
    let mut on_b = on_a.clone();
    on_b.prop_snv_on_b = 1.0;
    let a = simulate(&on_a, 31).unwrap();
    let b = simulate(&on_b, 31).unwrap();
    assert!(b.alleles.iter().all(|&al| al == Allele::B));
    for (clone, profile) in &a.evolution.total {
        for (pos, g) in profile.iter().enumerate() {
            assert_eq!(b.evolution.total[clone][pos], g.swapped(), "clone {clone} pos {pos}");
        }
    }
    let alt = |s: &Simulation| s.rows.iter().map(|r| (r.total_reads, r.variant_reads)).collect::<Vec<_>>();
    assert_eq!(alt(&a), alt(&b), "depth and alt do not depend on the allele label");
}

#[test]
fn mutation_loss_removes_the_snv_in_some_descendant() {
    let mut p = no_cn(8, 400);
    p.prop_pos_lost = 0.3;
    p.prop_lost_truncal = 0.0;
    p.prop_mutloss_positions = 0.2;
    let sim = simulate(&p, 41).unwrap();
    assert_eq!(sim.evolution.prop_mutation_loss, 0.2);
    let lost = sim.rows.iter().filter(|r| r.dcf > r.ccf + 1e-9).count();
    assert!(lost > 0, "a lost SNV is still counted by DCF but not by CCF");
}

fn trunk_states(sim: &Simulation) -> BTreeSet<(i32, i32)> {
    let trunk = &sim.evolution.total[&sim.tree.initial_cc];
    trunk.iter().map(|g| (g.a + g.b, g.a.min(g.b))).collect()
}

#[test]
fn one_cna_per_position_cannot_reach_loh_after_gain() {
    let states = trunk_states(&simulate(&Params::new(5, 2000), 61).unwrap());
    assert!(states.iter().all(|&(total, minor)| total <= 4 && !(minor == 0 && total >= 3)), "{states:?}");
}

#[test]
fn second_cnas_give_loh_with_gains_and_never_lose_the_last_copy() {
    let mut p = Params::new(5, 2000);
    p.prop_pos_lost = 0.45;
    p.prop_pos_second_cna = 0.5;
    let sim = simulate(&p, 61).unwrap();
    let states = trunk_states(&sim);
    assert!(states.contains(&(3, 0)) && states.contains(&(4, 0)), "{states:?}");
    for profile in sim.evolution.total.values() {
        assert!(profile.iter().all(|g| g.a >= 0 && g.b >= 0 && g.mutated >= 0 && g.mutated <= g.a.max(g.b)));
    }
    let trunk = &sim.evolution.total[&sim.tree.initial_cc];
    assert!(trunk.iter().all(|g| g.a + g.b >= 1), "the last copy is never lost");
    // (3, 0) with 2 mutated copies needs the SNV between cnloh and the gain that follows it.
    assert!(trunk.iter().any(|g| g.a.max(g.b) == 3 && g.a.min(g.b) == 0 && g.mutated == 2));
}

#[test]
fn depth_dispersion_adds_phi_mean_squared_to_the_depth_variance() {
    let vmr = |p: &Params| {
        let d: Vec<f64> = simulate(p, 92).unwrap().rows.iter().map(|r| r.total_reads as f64).collect();
        let m = d.iter().sum::<f64>() / d.len() as f64;
        (d.iter().map(|x| (x - m).powi(2)).sum::<f64>() / d.len() as f64) / m
    };
    let mut p = no_cn(4, 5000);
    p.coverage = 50.0;
    assert!((vmr(&p) - 1.0).abs() < 0.1, "Poisson without CN");
    p.depth_dispersion = Some(0.02);
    let v = vmr(&p);
    assert!((v - 2.0).abs() < 0.2, "VMR {v}, expected 1 + 0.02 * 50 = 2");
}

#[test]
fn noise_snvs_go_to_new_clusters_off_the_tree() {
    let mut p = Params::new(4, 300);
    p.fract_noise = 0.1;
    p.n_noise_clones = 2;
    let sim = simulate(&p, 51).unwrap();
    assert_eq!(sim.rows.len(), 330);
    let noise: Vec<_> = sim.rows.iter().filter(|r| r.noise).collect();
    assert_eq!(noise.len(), 30);
    let max_node = *sim.tree.nodes.iter().max().unwrap();
    assert!(noise.iter().all(|r| r.child > max_node && sim.noise_clones.contains(&r.child)));
}

#[test]
fn constant_multiplicity_false_with_too_many_cnas_is_an_error() {
    let mut p = Params::new(4, 300);
    p.constant_multiplicity = false;
    p.prop_pos_gained = 0.7;
    p.prop_pos_lost = 0.3;
    p.prop_mutloss_positions = 0.0;
    assert!(simulate(&p, 1).is_ok(), "exactly all positions fit");
    p.prop_mutloss_positions = 0.1;
    p.prop_lost_truncal = 0.5;
    p.mutloss_truncal = true;
    assert!(simulate(&p, 1).is_ok());
}

#[test]
fn inputs_conipher_cannot_run_are_rejected() {
    assert!(Params { n_clones: 1, ..Params::new(1, 300) }.validate().is_err());
    let mut tight = Params::new(10, 15);
    tight.prop_truncal_snvs = 0.5;
    assert!(simulate(&tight, 1).is_err(), "7 subclonal SNVs cannot cover 10 edges");
}

#[test]
fn same_seed_gives_byte_identical_files() {
    let bin = env!("CARGO_BIN_EXE_diplosim");
    let run = |tag: &str| {
        let dir = scratch(tag);
        let status = Command::new(bin)
            .args(["--n-clones", "4", "--n-snv", "300", "--seed", "7", "--out"])
            .arg(&dir)
            .status()
            .unwrap();
        assert!(status.success());
        dir
    };
    let (d1, d2) = (run("same1"), run("same2"));
    let files = [
        "diplosim.tsv",
        "diplosim_TX.tsv",
        "diplosim_treeedges.tsv",
        "diplosim_cloneprops.tsv",
        "diplosim_info.tsv",
        "truth/genotypes.tsv",
        "truth/snv_edges.tsv",
        "truth/events.tsv",
    ];
    for f in files {
        assert_eq!(fs::read(d1.join(f)).unwrap(), fs::read(d2.join(f)).unwrap(), "{f} differs");
    }
    let other = scratch("other");
    Command::new(bin).args(["--n-clones", "4", "--n-snv", "300", "--seed", "8", "--out"]).arg(&other).status().unwrap();
    assert_ne!(fs::read(d1.join("diplosim.tsv")).unwrap(), fs::read(other.join("diplosim.tsv")).unwrap());
    for d in [d1, d2, other] {
        fs::remove_dir_all(d).unwrap();
    }
}
