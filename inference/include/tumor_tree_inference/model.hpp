#pragma once

#include <cstddef>
#include <filesystem>
#include <string>
#include <vector>

namespace tumor_tree_inference {

struct GenotypeCandidate {
    // Candidate-level copy-number context used by the PhyClone/PyClone-VI
    // expected-ALT calculation.  The normal CN is fixed at diploid (2) by
    // the current v4 input contract; reference/variant CN differ for the
    // mutation-before/after-CN candidates.
    int multiplicity = 0;
    double normal_cn = 0.0;
    double reference_cn = 0.0;
    double variant_cn = 0.0;
    double normal_alt_probability = 0.0;
    double reference_alt_probability = 0.0;
    double variant_alt_probability = 0.0;
    double prior = 0.0;
    double log_prior = 0.0;
};

struct Site {
    std::string mutation_id;
    std::string chrom;
    long long pos = 0;
    std::string ref;
    std::string alt;
    int ref_reads = 0;
    int alt_reads = 0;
    int total_reads = 0;
    int hp1_1_ref = 0;
    int hp1_1_alt = 0;
    int hp2_1_ref = 0;
    int hp2_1_alt = 0;
    double major_cn = 0.0;
    double minor_cn = 0.0;
    double total_cn = 0.0;
    double purity = 0.0;
    // Per-site constants used by the repeated emission calculation.  They
    // are derived from the canonical counts/CN at load time and are not
    // additional model inputs.
    double log_binomial_coefficient = 0.0;
    std::vector<GenotypeCandidate> genotype_candidates;
    // Candidate-aligned views retained for the existing multiplicity output
    // and public smoke seam.  They are not canonical input columns.
    std::vector<double> log_multiplicity_prior;
    std::vector<int> multiplicity_candidates;
    std::vector<double> multiplicity_prior;
};

struct CanonicalTable {
    std::vector<Site> sites;
    double requested_purity = 0.0;
    std::string input_sha256;
};

// Return the normalized posterior responsibility of each loader-derived
// multiplicity candidate at a fixed clone prevalence.  The observed VAF is
// never modified; this is a model-implied latent-state posterior.
std::vector<double> site_multiplicity_posterior(const Site& site, double phi);

// The loader is fail-closed: it validates all required active fields before
// returning.  It owns all Site memory; callers only borrow const references.
CanonicalTable load_canonical_table(const std::filesystem::path& path,
                                    double requested_purity,
                                    const std::vector<std::string>& exclude_ids);

// Each row is independent.  The result is allocated by the caller-facing
// vector and written by disjoint worker indices, so threads never share a
// mutable RNG or sampler state.  Reduction of a state score is always done in
// site index order by the algorithm layer.
std::vector<std::vector<double>> likelihood_matrix(const CanonicalTable& table,
                                                   const std::vector<double>& phi,
                                                   unsigned threads);

// Evaluate one site/clone emission without allocating a full matrix.  The
// assignment proposal uses this local score update to avoid rescoring every
// SNV when only one z_i changes.
double site_log_likelihood(const Site& site, double phi);

}  // namespace tumor_tree_inference
