//! Simulation parameters (CONIPHER `tx_simulation`, simulate.py:13-46, plus seven diplosim ones).
//! Defaults are CONIPHER's; `validate` is the one boundary check every entry point passes.
use clap::{ArgAction, Args};

use crate::evolution::Event;

#[derive(Args, Clone, Debug)]
pub struct Params {
    /// Tumour clones, normal excluded (CONIPHER n_nodes).
    #[arg(long)]
    pub n_clones: usize,
    /// SNV positions (CONIPHER n_positions).
    #[arg(long)]
    pub n_snv: usize,
    #[arg(long, default_value_t = 0.5)]
    pub prop_truncal_snvs: f64,
    #[arg(long, default_value_t = 0.5)]
    pub prop_pos_gained: f64,
    #[arg(long, default_value_t = 0.3)]
    pub prop_pos_lost: f64,
    #[arg(long, default_value_t = 1.0)]
    pub prop_gained_truncal: f64,
    #[arg(long, default_value_t = 1.0)]
    pub prop_lost_truncal: f64,
    /// diplosim: probability that a truncal CNA position gets one more truncal CNA after it,
    /// asked again after each added event (at most MAX_EXTRA_CNAS). 0 = CONIPHER.
    #[arg(long, default_value_t = 0.0)]
    pub prop_pos_second_cna: f64,
    #[arg(long, value_enum, value_delimiter = ',', default_values_t = [Event::GainA, Event::GainB, Event::GainBoth])]
    pub gain_events: Vec<Event>,
    #[arg(long, value_enum, value_delimiter = ',', default_values_t = [Event::LossB, Event::CnlohB])]
    pub loss_events: Vec<Event>,
    #[arg(long, default_value_t = 0.0)]
    pub prop_mutloss_positions: f64,
    #[arg(long, default_value_t = false, action = ArgAction::Set)]
    pub mutloss_truncal: bool,
    #[arg(long, default_value_t = true, action = ArgAction::Set)]
    pub constant_multiplicity: bool,
    #[arg(long, default_value_t = false, action = ArgAction::Set)]
    pub clonal_wgd: bool,
    #[arg(long, default_value_t = false, action = ArgAction::Set)]
    pub subclonal_wgd: bool,
    #[arg(long, default_value_t = 1)]
    pub n_subclonal_wgd: usize,
    #[arg(long, default_value_t = 1)]
    pub minimum_branch_length: usize,
    #[arg(long, default_value_t = 400.0)]
    pub coverage: f64,
    /// diplosim: depth overdispersion phi. Each site's expected depth is scaled by a
    /// Gamma(1/phi, phi) factor, so depth variance = mean + phi * mean^2. Unset = Poisson.
    #[arg(long)]
    pub depth_dispersion: Option<f64>,
    #[arg(long, default_value_t = 0.7)]
    pub min_tumour_purity: f64,
    #[arg(long, default_value_t = 0.9)]
    pub max_tumour_purity: f64,
    #[arg(long, default_value_t = 0.0)]
    pub fract_noise: f64,
    #[arg(long, default_value_t = 0)]
    pub n_noise_clones: usize,
    /// diplosim: probability that a position's SNV sits on allele B (HP2).
    #[arg(long, default_value_t = 0.5)]
    pub prop_snv_on_b: f64,
    /// diplosim: probability that a read keeps its HP tag; the rest become HP0.
    #[arg(long, default_value_t = 0.8)]
    pub prop_tagged: f64,
    /// diplosim: each site draws its own tag probability from Beta(k * prop_tagged,
    /// k * (1 - prop_tagged)) with k = this value; smaller k spreads sites more. Unset = every
    /// site uses prop_tagged.
    #[arg(long)]
    pub tag_concentration: Option<f64>,
    /// diplosim: probability that a read carries the other haplotype's tag (phasing error).
    #[arg(long, default_value_t = 0.0)]
    pub mistag_rate: f64,
    /// diplosim: probability that a read shows the other allele at the SNV (ref <-> alt).
    #[arg(long, default_value_t = 0.0)]
    pub base_error: f64,
}

impl Params {
    /// CONIPHER defaults for everything except the two required counts.
    pub fn new(n_clones: usize, n_snv: usize) -> Params {
        Params {
            n_clones,
            n_snv,
            prop_truncal_snvs: 0.5,
            prop_pos_gained: 0.5,
            prop_pos_lost: 0.3,
            prop_gained_truncal: 1.0,
            prop_lost_truncal: 1.0,
            prop_pos_second_cna: 0.0,
            gain_events: vec![Event::GainA, Event::GainB, Event::GainBoth],
            loss_events: vec![Event::LossB, Event::CnlohB],
            prop_mutloss_positions: 0.0,
            mutloss_truncal: false,
            constant_multiplicity: true,
            clonal_wgd: false,
            subclonal_wgd: false,
            n_subclonal_wgd: 1,
            minimum_branch_length: 1,
            coverage: 400.0,
            depth_dispersion: None,
            min_tumour_purity: 0.7,
            max_tumour_purity: 0.9,
            fract_noise: 0.0,
            n_noise_clones: 0,
            prop_snv_on_b: 0.5,
            prop_tagged: 0.8,
            tag_concentration: None,
            mistag_rate: 0.0,
            base_error: 0.0,
        }
    }

    /// Rejects inputs CONIPHER would crash on or that have no meaning.
    pub fn validate(&self) -> Result<(), String> {
        // make_tree reads parents[1] (topology.py:25), which does not exist for one leaf.
        if self.n_clones < 2 {
            return Err("n_clones must be >= 2 (CONIPHER make_tree fails for 1, topology.py:25)".into());
        }
        if self.n_snv == 0 {
            return Err("n_snv must be >= 1".into());
        }
        let probs = [
            ("prop_truncal_snvs", self.prop_truncal_snvs),
            ("prop_pos_gained", self.prop_pos_gained),
            ("prop_pos_lost", self.prop_pos_lost),
            ("prop_gained_truncal", self.prop_gained_truncal),
            ("prop_lost_truncal", self.prop_lost_truncal),
            ("prop_pos_second_cna", self.prop_pos_second_cna),
            ("prop_mutloss_positions", self.prop_mutloss_positions),
            ("prop_snv_on_b", self.prop_snv_on_b),
            ("prop_tagged", self.prop_tagged),
            ("mistag_rate", self.mistag_rate),
            ("base_error", self.base_error),
        ];
        for (name, p) in probs {
            if !(0.0..=1.0).contains(&p) {
                return Err(format!("{name} must be in [0, 1], got {p}"));
            }
        }
        for (name, k) in [("tag_concentration", self.tag_concentration), ("depth_dispersion", self.depth_dispersion)] {
            if let Some(k) = k {
                if !(k > 0.0 && k.is_finite()) {
                    return Err(format!("{name} must be > 0, got {k}"));
                }
            }
        }
        // CCF and Fract_a divide by purity (sequencing.py:71, 112), so 0 is excluded.
        if !(self.min_tumour_purity > 0.0
            && self.min_tumour_purity <= self.max_tumour_purity
            && self.max_tumour_purity <= 1.0)
        {
            return Err("need 0 < min_tumour_purity <= max_tumour_purity <= 1".into());
        }
        if !(self.coverage >= 0.0 && self.coverage.is_finite()) {
            return Err("coverage must be >= 0".into());
        }
        if !(self.fract_noise >= 0.0 && self.fract_noise.is_finite()) {
            return Err("fract_noise must be >= 0".into());
        }
        if self.fract_noise > 0.0 && self.n_noise_clones == 0 {
            return Err("fract_noise > 0 needs n_noise_clones > 0 (simulate.py:68)".into());
        }
        if self.minimum_branch_length == 0 {
            return Err("minimum_branch_length must be >= 1".into());
        }
        if self.gain_events.is_empty() || !self.gain_events.iter().all(|e| e.is_gain()) {
            return Err("gain_events must be a non-empty subset of gain_A,gain_B,gain_both".into());
        }
        if self.loss_events.is_empty() || !self.loss_events.iter().all(|e| e.is_loss()) {
            return Err("loss_events must be a non-empty subset of loss_A,loss_B,cnloh_A,cnloh_B".into());
        }
        // partition asserts this when minimum_branch_length == 1 (evolution.py:37); the edge
        // count equals n_clones. n_snv grows by the noise SNVs first (simulate.py:59-60).
        let n_pos = self.n_snv + self.n_noise();
        let n_subclonal = (n_pos as f64 * (1.0 - self.prop_truncal_snvs)) as usize;
        if self.minimum_branch_length == 1 && n_subclonal < self.n_clones {
            return Err(format!(
                "{n_subclonal} subclonal SNVs for {} edges: CONIPHER needs subclonal SNVs >= edges (evolution.py:37)",
                self.n_clones
            ));
        }
        Ok(())
    }

    /// simulate.py:59 `n_noise = round(n_positions * fract_noise)`.
    pub fn n_noise(&self) -> usize {
        (self.n_snv as f64 * self.fract_noise).round_ties_even() as usize
    }
}
