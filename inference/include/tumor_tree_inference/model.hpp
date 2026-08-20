#pragma once

#include <cstddef>
#include <filesystem>
#include <string>
#include <vector>

namespace tumor_tree_inference {

struct Site {
    std::string mutation_id;
    std::string chrom;
    long long pos = 0;
    std::string ref;
    std::string alt;
    int bulk_ref = 0;
    int bulk_alt = 0;
    int bulk_depth = 0;
    int hp1_1_ref = 0;
    int hp1_1_alt = 0;
    int hp2_1_ref = 0;
    int hp2_1_alt = 0;
    double major_cn = 0.0;
    double minor_cn = 0.0;
    double total_cn = 0.0;
    double purity = 0.0;
    std::vector<int> multiplicity_candidates;
    std::vector<double> multiplicity_prior;
};

struct CanonicalTable {
    std::vector<Site> sites;
    double requested_purity = 0.0;
    std::string input_sha256;
};

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
