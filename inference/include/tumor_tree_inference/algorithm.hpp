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
    std::uint64_t iterations = 1500;
    std::uint64_t burnin = 1000;
    unsigned thin = 1;
    double purity = 0.99;
    std::uint64_t checkpoint_every = 100;
    unsigned threads = 1;
    unsigned chains = 1;
    bool resume = false;

    void validate() const;
};

struct RunOptions {
    std::filesystem::path outdir;
    std::vector<std::string> exclude_ids;
};

struct ChainResult {
    std::filesystem::path outdir;
    std::uint64_t posterior_samples = 0;
};

// Replaceable algorithm seam.  Implementations own their RNG/state and must
// not mutate CanonicalTable.  One Algorithm object is run independently per
// chain, so the chain runner can safely parallelize calls.
class Algorithm {
public:
    virtual ~Algorithm() = default;
    virtual const std::string& name() const = 0;
    virtual ChainResult run(const CanonicalTable& table,
                            const InferenceConfig& config,
                            const RunOptions& options,
                            unsigned chain_index) const = 0;
};

using AlgorithmPtr = std::unique_ptr<Algorithm>;

}  // namespace tumor_tree_inference
