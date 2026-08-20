#pragma once

#include "tumor_tree_inference/algorithm.hpp"

#include <string>
#include <vector>

namespace tumor_tree_inference {

class AlgorithmRegistry {
public:
    static AlgorithmRegistry& instance();

    AlgorithmPtr create(const std::string& algorithm) const;
    std::vector<std::string> names() const;

private:
    AlgorithmRegistry();
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace tumor_tree_inference
