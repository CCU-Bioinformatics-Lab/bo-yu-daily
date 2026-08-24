#include "tumor_tree_inference/registry.hpp"

#include <map>
#include <stdexcept>

namespace tumor_tree_inference {

AlgorithmPtr make_rao_blackwellized_annealed_smc();

struct AlgorithmRegistry::Impl {
    std::map<std::string, AlgorithmPtr (*)()> factories;
};

AlgorithmRegistry::AlgorithmRegistry() : impl_(std::make_unique<Impl>()) {
    impl_->factories.emplace("rao_blackwellized_annealed_smc", &make_rao_blackwellized_annealed_smc);
}

AlgorithmRegistry& AlgorithmRegistry::instance() {
    static AlgorithmRegistry registry;
    return registry;
}

AlgorithmPtr AlgorithmRegistry::create(const std::string& algorithm) const {
    const auto found = impl_->factories.find(algorithm);
    if (found == impl_->factories.end()) throw std::runtime_error("unknown algorithm " + algorithm + "; available: rao_blackwellized_annealed_smc");
    return found->second();
}

std::vector<std::string> AlgorithmRegistry::names() const {
    std::vector<std::string> result;
    for (const auto& [name, factory] : impl_->factories) {
        static_cast<void>(factory);
        result.push_back(name);
    }
    return result;
}

}  // namespace tumor_tree_inference
