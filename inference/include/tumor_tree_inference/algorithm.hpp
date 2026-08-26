#pragma once

#include "tumor_tree_inference/model.hpp"

#include <cstdint>
#include <filesystem>
#include <memory>
#include <string>
#include <vector>

namespace tumor_tree_inference {

struct InferenceConfig {
    std::uint64_t seed = 1;
    unsigned num_nodes = 6;
    unsigned annealing_stages = 64;
    double purity = 0.99;
    std::uint64_t checkpoint_every = 100;
    unsigned threads = 1;
    unsigned repeats = 1;
    unsigned particles = 32;
    double conditional_ess_target = 0.8;
    double resample_ess_threshold = 0.5;
    unsigned rejuvenation_sweeps = 3;
    unsigned global_topology_moves = 1;
    bool resume = false;

    void validate() const;
};

struct RunOptions {
    std::filesystem::path outdir;
    std::vector<std::string> exclude_ids;
};

struct RepeatResult {
    std::filesystem::path outdir;
    std::uint64_t posterior_samples = 0;
};

// Replaceable algorithm seam.  Implementations own their RNG/state and must
// not mutate CanonicalTable. One Algorithm object is run independently per
// repeat, so the repeat runner can safely parallelize calls.
class Algorithm {
public:
    virtual ~Algorithm() = default;
    virtual const std::string& name() const = 0;
    virtual RepeatResult run(const CanonicalTable& table,
                             const InferenceConfig& config,
                             const RunOptions& options,
                             unsigned repeat_index) const = 0;
};

using AlgorithmPtr = std::unique_ptr<Algorithm>;

}  // namespace tumor_tree_inference
