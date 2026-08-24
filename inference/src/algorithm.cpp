#include "tumor_tree_inference/algorithm.hpp"

#include "json.hpp"

#include <algorithm>
#include <cerrno>
#include <cmath>
#include <cstring>
#include <fstream>
#include <fcntl.h>
#include <functional>
#include <iomanip>
#include <limits>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <sstream>
#include <stdexcept>
#include <unistd.h>

namespace tumor_tree_inference {
namespace {

constexpr double kTssbAlphaDecay = 0.65;
constexpr double kTssbMinimumMassShape = 0.25;

struct Particle {
    std::vector<int> parents;
    std::vector<double> eta;
    double log_likelihood = -std::numeric_limits<double>::infinity();
};

using Counters = std::map<std::string, std::uint64_t>;

bool valid_tree(const std::vector<int>& parents) {
    std::size_t structural_roots = 0;
    for (std::size_t child = 0; child < parents.size(); ++child) {
        const int parent = parents[child];
        if (parent < -1 || parent >= static_cast<int>(parents.size()) || parent == static_cast<int>(child)) return false;
        if (parent == -1) ++structural_roots;
        std::vector<bool> seen(parents.size(), false);
        seen[child] = true;
        int cursor = parent;
        while (cursor != -1) {
            if (seen[static_cast<std::size_t>(cursor)]) return false;
            seen[static_cast<std::size_t>(cursor)] = true;
            cursor = parents[static_cast<std::size_t>(cursor)];
        }
    }
    // -1 denotes the single direct child of the structural tumor root.  A
    // valid state is therefore one connected tumor tree, not a forest of
    // independent founders.  The caller guarantees a non-empty state.
    return !parents.empty() && structural_roots == 1;
}

std::vector<std::vector<int>> children(const std::vector<int>& parents) {
    std::vector<std::vector<int>> result(parents.size());
    for (std::size_t child = 0; child < parents.size(); ++child) {
        if (parents[child] != -1) result[static_cast<std::size_t>(parents[child])].push_back(static_cast<int>(child));
    }
    return result;
}

double visit_phi(int node, const std::vector<std::vector<int>>& child_list,
                 const std::vector<double>& eta, std::vector<double>& phi) {
    double value = eta[static_cast<std::size_t>(node)];
    for (int child : child_list[static_cast<std::size_t>(node)]) value += visit_phi(child, child_list, eta, phi);
    phi[static_cast<std::size_t>(node)] = value;
    return value;
}

std::vector<double> cumulative_phi(const std::vector<int>& parents, const std::vector<double>& eta) {
    if (!valid_tree(parents) || eta.size() != parents.size()) throw std::runtime_error("invalid tree/eta dimensions");
    const double sum = std::accumulate(eta.begin(), eta.end(), 0.0);
    if (!(sum > 0.0) || std::abs(sum - 1.0) > 1e-9 || std::any_of(eta.begin(), eta.end(), [](double value) { return !(value > 0.0); })) throw std::runtime_error("eta must be a positive simplex");
    auto child_list = children(parents);
    std::vector<double> phi(parents.size(), 0.0);
    for (std::size_t node = 0; node < parents.size(); ++node) if (parents[node] == -1) visit_phi(static_cast<int>(node), child_list, eta, phi);
    // Descendant sums are mathematically bounded by one because eta is a
    // simplex.  Clamp only floating-point roundoff at the boundary so the
    // serialized C++ artifact satisfies the Python predictive scorer's
    // closed [0, 1] contract without hiding a real invalid state.
    for (double& value : phi) {
        if (value < -1e-12 || value > 1.0 + 1e-12) throw std::runtime_error("derived phi is outside [0,1]");
        value = std::clamp(value, 0.0, 1.0);
    }
    return phi;
}

std::vector<double> tssb_mass_prior_alpha(const std::vector<int>& parents) {
    const auto child_list = children(parents);
    std::vector<double> result(parents.size(), kTssbMinimumMassShape);
    for (std::size_t node = 0; node < parents.size(); ++node) {
        unsigned depth = 1;
        int cursor = parents[node];
        while (cursor != -1) {
            ++depth;
            cursor = parents[static_cast<std::size_t>(cursor)];
        }
        const double depth_shape = std::exp(-kTssbAlphaDecay * static_cast<double>(depth - 1U));
        const double width_shape = 1.0 / (1.0 + static_cast<double>(child_list[node].size()));
        result[node] += 0.75 * depth_shape * width_shape;
    }
    return result;
}

double tssb_tree_log_prior(const std::vector<int>& parents) {
    const auto child_list = children(parents);
    double result = 0.0;
    for (std::size_t node = 0; node < parents.size(); ++node) {
        int depth = 1;
        int cursor = parents[node];
        while (cursor != -1) { ++depth; cursor = parents[static_cast<std::size_t>(cursor)]; }
        result += -0.35 * static_cast<double>(depth) - 0.12 * std::pow(static_cast<double>(child_list[node].size()), 2.0);
    }
    return result;
}

bool is_descendant(const std::vector<int>& parents, int node, int candidate) {
    int cursor = candidate;
    while (cursor != -1) {
        if (cursor == node) return true;
        cursor = parents[static_cast<std::size_t>(cursor)];
    }
    return false;
}

std::vector<std::vector<int>> topology_support_for_node(const std::vector<int>& parents, std::size_t node) {
    std::vector<std::vector<int>> support;
    for (int proposed_parent = -1; proposed_parent < static_cast<int>(parents.size()); ++proposed_parent) {
        if (proposed_parent == static_cast<int>(node) || is_descendant(parents, static_cast<int>(node), proposed_parent)) continue;
        auto proposal = parents;
        proposal[node] = proposed_parent;
        if (valid_tree(proposal)) support.push_back(std::move(proposal));
    }
    return support;
}

double dirichlet_logpdf(const std::vector<double>& values, const std::vector<double>& alpha) {
    if (values.size() != alpha.size()) return -std::numeric_limits<double>::infinity();
    const double value_sum = std::accumulate(values.begin(), values.end(), 0.0);
    if (std::abs(value_sum - 1.0) > 1e-9 || std::any_of(values.begin(), values.end(), [](double value) { return !(value > 0.0); })) return -std::numeric_limits<double>::infinity();
    const double alpha_sum = std::accumulate(alpha.begin(), alpha.end(), 0.0);
    double result = std::lgamma(alpha_sum);
    for (double value : alpha) result -= std::lgamma(value);
    for (std::size_t i = 0; i < values.size(); ++i) result += (alpha[i] - 1.0) * std::log(values[i]);
    return result;
}

std::vector<double> dirichlet_sample(const std::vector<double>& alpha, std::mt19937_64& rng) {
    std::vector<double> result;
    result.reserve(alpha.size());
    double total = 0.0;
    for (double value : alpha) {
        std::gamma_distribution<double> gamma(value, 1.0);
        const double draw = gamma(rng);
        result.push_back(draw);
        total += draw;
    }
    if (!(total > 0.0) || !std::isfinite(total)) throw std::runtime_error("Dirichlet proposal produced an invalid simplex");
    for (double& value : result) value /= total;
    return result;
}

double log_sum_exp(const std::vector<double>& values) {
    if (values.empty()) return -std::numeric_limits<double>::infinity();
    const double maximum = *std::max_element(values.begin(), values.end());
    if (!std::isfinite(maximum)) return maximum;
    double total = 0.0;
    for (const double value : values) total += std::exp(value - maximum);
    if (!(total > 0.0) || !std::isfinite(total)) return -std::numeric_limits<double>::infinity();
    return maximum + std::log(total);
}

double rb_log_likelihood(const CanonicalTable& table, const std::vector<double>& phi,
                         const std::vector<double>& eta) {
    if (phi.size() != eta.size() || phi.empty()) throw std::runtime_error("Rao-Blackwellized state dimensions do not match");
    std::vector<double> node_terms(phi.size());
    double result = 0.0;
    for (const Site& site : table.sites) {
        for (std::size_t node = 0; node < phi.size(); ++node) {
            node_terms[node] = site_log_likelihood(site, phi[node]) + std::log(eta[node]);
        }
        const double site_score = log_sum_exp(node_terms);
        if (!std::isfinite(site_score)) return site_score;
        result += site_score;
    }
    return result;
}

double particle_log_target(const CanonicalTable& table, const Particle& particle, double beta) {
    static_cast<void>(table);
    return tssb_tree_log_prior(particle.parents) +
           dirichlet_logpdf(particle.eta, tssb_mass_prior_alpha(particle.parents)) +
           beta * particle.log_likelihood;
}

std::vector<int> rb_map_assignments(const CanonicalTable& table, const Particle& particle) {
    const auto phi = cumulative_phi(particle.parents, particle.eta);
    std::vector<int> assignments;
    assignments.reserve(table.sites.size());
    std::vector<double> node_terms(phi.size());
    for (const Site& site : table.sites) {
        for (std::size_t node = 0; node < phi.size(); ++node) {
            node_terms[node] = site_log_likelihood(site, phi[node]) + std::log(particle.eta[node]);
        }
        assignments.push_back(static_cast<int>(std::distance(node_terms.begin(), std::max_element(node_terms.begin(), node_terms.end()))));
    }
    return assignments;
}

std::size_t sample_log_categorical(const std::vector<double>& log_weights, std::mt19937_64& rng) {
    if (log_weights.empty()) throw std::runtime_error("cannot sample an empty categorical distribution");
    const double maximum = *std::max_element(log_weights.begin(), log_weights.end());
    if (!std::isfinite(maximum)) throw std::runtime_error("categorical weights are all non-finite");
    double total = 0.0;
    for (double value : log_weights) total += std::exp(value - maximum);
    if (!(total > 0.0) || !std::isfinite(total)) throw std::runtime_error("categorical weights have invalid total");
    const double draw = std::generate_canonical<double, 53>(rng) * total;
    double cumulative = 0.0;
    for (std::size_t index = 0; index < log_weights.size(); ++index) {
        cumulative += std::exp(log_weights[index] - maximum);
        if (draw < cumulative || index + 1U == log_weights.size()) return index;
    }
    return log_weights.size() - 1U;
}

std::vector<int> sample_tree(unsigned num_nodes, std::mt19937_64& rng) {
    if (num_nodes < 2) throw std::runtime_error("SMC requires at least two clone nodes");
    std::vector<int> parents(num_nodes, -1);
    // Keeping clone 0 as the initial founder preserves the fixed-K output
    // convention.  Topology rejuvenation can subsequently move the founder.
    for (unsigned child = 1; child < num_nodes; ++child) {
        std::uniform_int_distribution<int> parent_distribution(0, static_cast<int>(child - 1U));
        parents[child] = parent_distribution(rng);
    }
    return parents;
}

double weighted_ess(const std::vector<double>& log_weights) {
    if (log_weights.empty()) return 0.0;
    const double maximum = *std::max_element(log_weights.begin(), log_weights.end());
    if (!std::isfinite(maximum)) return 0.0;
    double sum = 0.0;
    double squared_sum = 0.0;
    for (const double log_weight : log_weights) {
        const double weight = std::exp(log_weight - maximum);
        sum += weight;
        squared_sum += weight * weight;
    }
    if (!(sum > 0.0) || !(squared_sum > 0.0) || !std::isfinite(sum) || !std::isfinite(squared_sum)) return 0.0;
    return (sum * sum) / squared_sum;
}

double normalize_log_weights(std::vector<double>& log_weights) {
    const double normalizer = log_sum_exp(log_weights);
    if (!std::isfinite(normalizer)) throw std::runtime_error("SMC particle weights have invalid normalization");
    for (double& value : log_weights) value -= normalizer;
    return normalizer;
}

std::vector<std::size_t> systematic_resample(const std::vector<double>& log_weights,
                                             std::mt19937_64& rng) {
    if (log_weights.empty()) throw std::runtime_error("cannot resample an empty particle set");
    const double maximum = *std::max_element(log_weights.begin(), log_weights.end());
    if (!std::isfinite(maximum)) throw std::runtime_error("cannot resample non-finite particle weights");
    std::vector<double> weights(log_weights.size(), 0.0);
    double total = 0.0;
    for (std::size_t index = 0; index < log_weights.size(); ++index) {
        weights[index] = std::exp(log_weights[index] - maximum);
        total += weights[index];
    }
    if (!(total > 0.0) || !std::isfinite(total)) throw std::runtime_error("cannot resample invalid particle weights");
    for (double& weight : weights) weight /= total;

    std::vector<double> cumulative(weights.size(), 0.0);
    std::partial_sum(weights.begin(), weights.end(), cumulative.begin());
    cumulative.back() = 1.0;
    const double offset = std::generate_canonical<double, 53>(rng) / static_cast<double>(weights.size());
    std::vector<std::size_t> ancestors;
    ancestors.reserve(weights.size());
    std::size_t cursor = 0;
    for (std::size_t draw = 0; draw < weights.size(); ++draw) {
        const double position = offset + static_cast<double>(draw) / static_cast<double>(weights.size());
        while (cursor + 1U < cumulative.size() && position > cumulative[cursor]) ++cursor;
        ancestors.push_back(cursor);
    }
    return ancestors;
}

double ess_for_beta(double beta, double current_beta,
                    const std::vector<double>& log_weights,
                    const std::vector<Particle>& particles) {
    std::vector<double> trial_weights(log_weights.size());
    const double delta = beta - current_beta;
    for (std::size_t index = 0; index < particles.size(); ++index) {
        trial_weights[index] = log_weights[index] + delta * particles[index].log_likelihood;
    }
    return weighted_ess(trial_weights);
}

double next_annealing_beta(double current_beta, unsigned annealing_steps,
                           double target_ess, const std::vector<double>& log_weights,
                           const std::vector<Particle>& particles) {
    if (current_beta >= 1.0) return 1.0;
    const double nominal = std::min(1.0, current_beta + 1.0 / static_cast<double>(std::max(1U, annealing_steps)));
    const double particle_count = static_cast<double>(particles.size());
    if (ess_for_beta(nominal, current_beta, log_weights, particles) >= target_ess * particle_count) return nominal;

    double low = current_beta;
    double high = nominal;
    for (unsigned iteration = 0; iteration < 32; ++iteration) {
        const double middle = (low + high) * 0.5;
        if (ess_for_beta(middle, current_beta, log_weights, particles) >= target_ess * particle_count) low = middle;
        else high = middle;
    }
    // A single very informative site may make even the smallest proposed
    // increment fall below the target.  Progress is mandatory; the next
    // stage therefore uses the nominal beta in that degenerate case.
    return low > current_beta + 1e-12 ? low : nominal;
}

std::string config_json(const InferenceConfig& config) {
    return "{\"seed\":" + json_u64(config.seed) + ",\"num_nodes\":" + std::to_string(config.num_nodes) +
           ",\"annealing_stages\":" + std::to_string(config.annealing_stages) + ",\"ascat_purity\":" + json_number(config.purity) +
           ",\"checkpoint_every\":" + json_u64(config.checkpoint_every) +
           ",\"particles\":" + std::to_string(config.particles) +
           ",\"conditional_ess_target\":" + json_number(config.conditional_ess_target) +
           ",\"resample_ess_threshold\":" + json_number(config.resample_ess_threshold) +
           ",\"rejuvenation_sweeps\":" + std::to_string(config.rejuvenation_sweeps) + "}";
}

std::string rng_json(const std::mt19937_64& rng) {
    std::ostringstream stream;
    stream << rng;
    return json_string(stream.str());
}

std::uint64_t repeat_seed(std::uint64_t seed, unsigned repeat_index) {
    // Each independent repeat receives a deterministic, disjoint seed.
    return seed + static_cast<std::uint64_t>(repeat_index);
}

class OutputLock final {
public:
    explicit OutputLock(const std::filesystem::path& directory) : path_(directory / ".run.lock") {
        fd_ = ::open(path_.c_str(), O_WRONLY | O_CREAT | O_EXCL, 0664);
        if (fd_ < 0) {
            throw std::runtime_error("output directory is already locked or cannot create lock " + path_.string() + ": " + std::strerror(errno));
        }
    }

    OutputLock(const OutputLock&) = delete;
    OutputLock& operator=(const OutputLock&) = delete;

    ~OutputLock() {
        if (fd_ >= 0) ::close(fd_);
        std::error_code ignored;
        std::filesystem::remove(path_, ignored);
    }

private:
    std::filesystem::path path_;
    int fd_ = -1;
};

std::string samples_jsonl(const std::vector<SampleRecord>& samples) {
    std::string result;
    for (const auto& sample : samples) result += sample_json(sample) + "\n";
    return result;
}

double posterior_quantile(std::vector<double> values, double probability) {
    if (values.empty() || !(probability >= 0.0 && probability <= 1.0)) {
        throw std::runtime_error("cannot calculate posterior quantile");
    }
    std::sort(values.begin(), values.end());
    const double position = probability * static_cast<double>(values.size() - 1U);
    const auto lower = static_cast<std::size_t>(std::floor(position));
    const auto upper = static_cast<std::size_t>(std::ceil(position));
    const double fraction = position - static_cast<double>(lower);
    return values[lower] + fraction * (values[upper] - values[lower]);
}

std::vector<int> canonical_clone_labels(const SampleRecord& sample);

std::string posterior_summary_tsv(const std::vector<SampleRecord>& retained, std::size_t num_nodes) {
    if (retained.empty()) throw std::runtime_error("cannot write posterior summary without retained samples");
    std::vector<std::vector<double>> phi_by_node(num_nodes);
    for (const auto& sample : retained) {
        if (sample.phi.size() != num_nodes) throw std::runtime_error("posterior summary phi dimensions do not match fixed K");
        const auto labels = canonical_clone_labels(sample);
        for (std::size_t node = 0; node < num_nodes; ++node) {
            if (!std::isfinite(sample.phi[node]) || sample.phi[node] < 0.0 || sample.phi[node] > 1.0) {
                throw std::runtime_error("posterior summary contains an invalid phi value");
            }
            phi_by_node[static_cast<std::size_t>(labels[node] - 1)].push_back(sample.phi[node]);
        }
    }

    std::ostringstream output;
    output << "clone\tccf_median\tccf_q025\tccf_q975\tphi_median\tphi_q025\tphi_q975\n";
    output << std::setprecision(17);
    for (std::size_t node = 0; node < num_nodes; ++node) {
        const double q025 = posterior_quantile(phi_by_node[node], 0.025);
        const double median = posterior_quantile(phi_by_node[node], 0.5);
        const double q975 = posterior_quantile(phi_by_node[node], 0.975);
        // In this model CCF is the descendant-sum phi.  Both names are
        // written so downstream readers can use the familiar CCF terminology
        // without losing the model's explicit phi definition.  Rows use the
        // same per-draw canonical clone labels as topology_summary.tsv, so
        // label switching does not mix unrelated candidate nodes.
        output << "clone_" << (node + 1U) << '\t'
               << median << '\t' << q025 << '\t' << q975 << '\t'
               << median << '\t' << q025 << '\t' << q975 << '\n';
    }
    return output.str();
}

std::vector<int> canonical_clone_labels(const SampleRecord& sample) {
    if (sample.parents.empty() || sample.parents.size() != sample.phi.size()) {
        throw std::runtime_error("cannot canonicalize a posterior sample with inconsistent dimensions");
    }
    const auto child_list = children(sample.parents);
    std::vector<std::size_t> depth(sample.parents.size(), 0);
    for (std::size_t node = 0; node < sample.parents.size(); ++node) {
        int cursor = sample.parents[node];
        while (cursor != -1) {
            ++depth[node];
            cursor = sample.parents[static_cast<std::size_t>(cursor)];
        }
    }

    std::vector<std::string> subtree_signature(sample.parents.size());
    std::function<std::string(std::size_t)> make_signature = [&](std::size_t node) {
        if (!subtree_signature[node].empty()) return subtree_signature[node];
        std::vector<std::string> child_signatures;
        child_signatures.reserve(child_list[node].size());
        for (const int child : child_list[node]) {
            child_signatures.push_back(make_signature(static_cast<std::size_t>(child)));
        }
        std::sort(child_signatures.begin(), child_signatures.end());
        std::ostringstream signature;
        signature << std::setprecision(17) << sample.phi[node] << '/' << depth[node]
                  << '/' << child_list[node].size() << '[';
        for (const auto& child_signature : child_signatures) signature << child_signature << ';';
        signature << ']';
        subtree_signature[node] = signature.str();
        return subtree_signature[node];
    };
    for (std::size_t node = 0; node < sample.parents.size(); ++node) make_signature(node);

    const auto node_less = [&](std::size_t left, std::size_t right) {
        if (sample.phi[left] != sample.phi[right]) return sample.phi[left] > sample.phi[right];
        if (depth[left] != depth[right]) return depth[left] < depth[right];
        if (child_list[left].size() != child_list[right].size()) {
            return child_list[left].size() > child_list[right].size();
        }
        return subtree_signature[left] < subtree_signature[right];
    };

    std::size_t root = sample.parents.size();
    for (std::size_t node = 0; node < sample.parents.size(); ++node) {
        if (sample.parents[node] == -1) {
            if (root != sample.parents.size()) throw std::runtime_error("topology summary found multiple roots");
            root = node;
        }
    }
    if (root == sample.parents.size()) throw std::runtime_error("topology summary found no root");

    // Label the rooted tree by a canonical traversal.  Child ordering uses
    // the promised posterior observables (phi, depth, child count), with the
    // full sorted subtree signature resolving non-symmetric ties.  Exact
    // equal subtree ties are automorphisms, so either traversal has the same
    // canonical edge multiset and does not depend on the input node labels.
    std::vector<int> labels(sample.parents.size(), 0);
    int next_label = 1;
    std::function<void(std::size_t)> assign_labels = [&](std::size_t node) {
        labels[node] = next_label++;
        std::vector<int> ordered_children = child_list[node];
        std::sort(ordered_children.begin(), ordered_children.end(), [&](int left, int right) {
            return node_less(static_cast<std::size_t>(left), static_cast<std::size_t>(right));
        });
        for (const int child : ordered_children) assign_labels(static_cast<std::size_t>(child));
    };
    assign_labels(root);
    if (next_label != static_cast<int>(sample.parents.size()) + 1) {
        throw std::runtime_error("topology summary could not label every clone");
    }
    return labels;
}

std::string topology_summary_tsv(const std::vector<SampleRecord>& retained) {
    if (retained.empty()) throw std::runtime_error("cannot write topology summary without retained samples");
    std::map<std::pair<int, int>, std::uint64_t> edge_counts;
    for (const auto& sample : retained) {
        if (!valid_tree(sample.parents)) throw std::runtime_error("topology summary received an invalid posterior tree");
        const auto labels = canonical_clone_labels(sample);
        for (std::size_t child = 0; child < sample.parents.size(); ++child) {
            const int parent = sample.parents[child] == -1
                ? 0
                : labels[static_cast<std::size_t>(sample.parents[child])];
            ++edge_counts[{parent, labels[child]}];
        }
    }

    std::ostringstream output;
    output << "parent\tchild\tsupport_count\tretained_samples\tsupport_fraction\n";
    output << std::setprecision(17);
    for (const auto& [edge, count] : edge_counts) {
        output << (edge.first == 0 ? "tumor_root" : "clone_" + std::to_string(edge.first)) << '\t'
               << "clone_" << edge.second << '\t'
               << count << '\t' << retained.size() << '\t'
               << static_cast<double>(count) / static_cast<double>(retained.size()) << '\n';
    }
    return output.str();
}

std::string multiplicity_posterior_tsv(
    const CanonicalTable& table,
    const std::vector<std::vector<double>>& posterior_sums,
    std::uint64_t posterior_draws) {
    if (posterior_draws == 0 || posterior_sums.size() != table.sites.size()) {
        throw std::runtime_error("cannot write multiplicity posterior without matching posterior draws");
    }
    std::ostringstream output;
    output << "mutation_id\tmultiplicity\tprior\tposterior_mean\n";
    output << std::setprecision(17);
    for (std::size_t site_index = 0; site_index < table.sites.size(); ++site_index) {
        const Site& site = table.sites[site_index];
        if (posterior_sums[site_index].size() != site.multiplicity_candidates.size()) {
            throw std::runtime_error("multiplicity posterior candidate dimensions do not match site");
        }
        for (std::size_t candidate = 0; candidate < site.multiplicity_candidates.size(); ++candidate) {
            const double posterior = posterior_sums[site_index][candidate] /
                static_cast<double>(posterior_draws);
            if (!std::isfinite(posterior) || posterior < 0.0) {
                throw std::runtime_error("multiplicity posterior contains an invalid value");
            }
            output << site.mutation_id << '\t'
                   << site.multiplicity_candidates[candidate] << '\t'
                   << site.multiplicity_prior[candidate] << '\t'
                   << posterior << '\n';
        }
    }
    return output.str();
}

void initialize_counters(Counters& counters) {
    for (const auto& move : {std::string("eta"), std::string("topology")}) {
        counters[move + "_proposals"] = 0;
        counters[move + "_accepted"] = 0;
    }
}


class RaoBlackwellizedAnnealedSmcContract final : public Algorithm {
public:
    const std::string& name() const override {
        static const std::string algorithm_name = "rao_blackwellized_annealed_smc";
        return algorithm_name;
    }

    RepeatResult run(const CanonicalTable& table, const InferenceConfig& config,
                     const RunOptions& options, unsigned repeat_index) const override {
        config.validate();
        if (config.resume) throw std::runtime_error("--resume is fail-closed: C++ checkpoint restore is not implemented; use a new outdir");
        if (std::filesystem::exists(options.outdir)) {
            if (!std::filesystem::is_directory(options.outdir) || !std::filesystem::is_empty(options.outdir)) throw std::runtime_error("refusing to overwrite non-empty output directory: " + options.outdir.string());
        } else {
            std::filesystem::create_directories(options.outdir);
        }
        OutputLock output_lock(options.outdir);

        struct Stage {
            std::uint64_t index = 0;
            double beta = 0.0;
            double conditional_ess = 0.0;
            double weighted_ess = 0.0;
            bool resampled = false;
            double ancestor_diversity = 1.0;
            std::uint64_t sweeps = 3;
            double eta_acceptance = 0.0;
            double topology_acceptance = 0.0;
        };

        const std::uint64_t derived_seed = repeat_seed(config.seed, repeat_index);
        InferenceConfig reported_config = config;
        reported_config.seed = derived_seed;
        std::mt19937_64 rng(derived_seed);
        const double uniform_log_weight = -std::log(static_cast<double>(config.particles));
        const double uniform_particle_weight = 1.0 / static_cast<double>(config.particles);

        std::vector<Particle> particles;
        particles.reserve(config.particles);
        for (unsigned index = 0; index < config.particles; ++index) {
            Particle particle;
            particle.parents = sample_tree(config.num_nodes, rng);
            particle.eta = dirichlet_sample(tssb_mass_prior_alpha(particle.parents), rng);
            particle.log_likelihood = rb_log_likelihood(table, cumulative_phi(particle.parents, particle.eta), particle.eta);
            particles.push_back(std::move(particle));
        }
        std::vector<double> log_weights(config.particles, uniform_log_weight);
        std::vector<Stage> stages;
        stages.reserve(static_cast<std::size_t>(config.annealing_stages));
        std::string history;
        double beta = 0.0;
        double log_normalizer_estimate = 0.0;
        std::vector<std::size_t> final_ancestors(config.particles, 0);
        std::iota(final_ancestors.begin(), final_ancestors.end(), 0);
        Counters counters;
        initialize_counters(counters);

        auto rejuvenate = [&](Particle& particle, std::uint64_t& eta_proposals,
                              std::uint64_t& eta_accepts, std::uint64_t& topology_proposals,
                              std::uint64_t& topology_accepts) {
            std::uniform_int_distribution<std::size_t> node_distribution(0, config.num_nodes - 1U);
            const std::size_t node = node_distribution(rng);
            const auto support = topology_support_for_node(particle.parents, node);
            if (!support.empty()) {
                std::vector<double> support_scores;
                std::vector<Particle> support_particles;
                support_scores.reserve(support.size());
                support_particles.reserve(support.size());
                for (const auto& parents : support) {
                    Particle proposal = particle;
                    proposal.parents = parents;
                    proposal.log_likelihood = rb_log_likelihood(table, cumulative_phi(proposal.parents, proposal.eta), proposal.eta);
                    support_scores.push_back(particle_log_target(table, proposal, beta));
                    support_particles.push_back(std::move(proposal));
                }
                const std::size_t selected = sample_log_categorical(support_scores, rng);
                ++topology_proposals;
                ++counters["topology_proposals"];
                if (support_particles[selected].parents != particle.parents) {
                    ++topology_accepts;
                    ++counters["topology_accepted"];
                }
                particle = std::move(support_particles[selected]);
            }

            const auto eta_alpha = tssb_mass_prior_alpha(particle.parents);
            Particle proposal = particle;
            proposal.eta = dirichlet_sample(eta_alpha, rng);
            proposal.log_likelihood = rb_log_likelihood(table, cumulative_phi(proposal.parents, proposal.eta), proposal.eta);
            const double log_acceptance = particle_log_target(table, proposal, beta) -
                particle_log_target(table, particle, beta) +
                dirichlet_logpdf(particle.eta, eta_alpha) - dirichlet_logpdf(proposal.eta, eta_alpha);
            ++eta_proposals;
            ++counters["eta_proposals"];
            if (std::log(std::max(1e-300, std::generate_canonical<double, 53>(rng))) < log_acceptance) {
                ++eta_accepts;
                ++counters["eta_accepted"];
                particle = std::move(proposal);
            }
        };

        const unsigned annealing_steps = std::max(1U, config.annealing_stages);
        for (unsigned stage_number = 0; stage_number < annealing_steps; ++stage_number) {
            const std::uint64_t stage_index = static_cast<std::uint64_t>(stage_number) + 1U;
            const double next_beta = stage_index >= annealing_steps
                ? 1.0
                : next_annealing_beta(beta, annealing_steps, config.conditional_ess_target, log_weights, particles);
            const double conditional_ess = ess_for_beta(next_beta, beta, log_weights, particles);
            const double delta_beta = next_beta - beta;
            for (std::size_t index = 0; index < particles.size(); ++index) log_weights[index] += delta_beta * particles[index].log_likelihood;
            log_normalizer_estimate += normalize_log_weights(log_weights);
            beta = next_beta;
            const double weighted_ess_value = weighted_ess(log_weights);
            Stage stage;
            stage.index = stage_index;
            stage.beta = beta;
            stage.conditional_ess = conditional_ess;
            stage.weighted_ess = weighted_ess_value;
            std::vector<std::size_t> ancestors(config.particles, 0);
            std::iota(ancestors.begin(), ancestors.end(), 0);
            if (weighted_ess_value < config.resample_ess_threshold * static_cast<double>(config.particles)) {
                ancestors = systematic_resample(log_weights, rng);
                std::vector<Particle> resampled;
                resampled.reserve(particles.size());
                for (const std::size_t ancestor : ancestors) resampled.push_back(particles[ancestor]);
                particles = std::move(resampled);
                log_weights.assign(config.particles, uniform_log_weight);
                stage.resampled = true;
            }
            std::vector<bool> ancestor_seen(config.particles, false);
            for (const std::size_t ancestor : ancestors) ancestor_seen[ancestor] = true;
            stage.ancestor_diversity = static_cast<double>(std::count(ancestor_seen.begin(), ancestor_seen.end(), true)) /
                static_cast<double>(config.particles);

            std::uint64_t eta_proposals = 0;
            std::uint64_t eta_accepts = 0;
            std::uint64_t topology_proposals = 0;
            std::uint64_t topology_accepts = 0;
            for (unsigned sweep = 0; sweep < config.rejuvenation_sweeps; ++sweep) {
                for (Particle& particle : particles) rejuvenate(particle, eta_proposals, eta_accepts, topology_proposals, topology_accepts);
            }
            stage.eta_acceptance = static_cast<double>(eta_accepts) / static_cast<double>(std::max<std::uint64_t>(1, eta_proposals));
            stage.topology_acceptance = static_cast<double>(topology_accepts) / static_cast<double>(std::max<std::uint64_t>(1, topology_proposals));
            stages.push_back(stage);

            for (std::size_t index = 0; index < particles.size(); ++index) {
                history += "{\"stage\":" + json_u64(stage.index) + ",\"particle_index\":" + json_u64(index) +
                    ",\"sample_kind\":\"smc_particle\",\"weight\":" + json_number(std::exp(log_weights[index])) +
                    ",\"log_weight\":" + json_number(log_weights[index]) +
                    ",\"ancestor_index\":" + json_u64(ancestors[index]) + ",\"topology\":{\"parents\":" + json_parent_array(particles[index].parents) +
                    "},\"rejuvenation_sweeps\":" + std::to_string(config.rejuvenation_sweeps) + "}\n";
            }
            final_ancestors = std::move(ancestors);
        }

        // Publish an equal-weight final posterior particle population.  This
        // final systematic draw is also what makes samples/checkpoint stable
        // to consume without exposing an unnormalised terminal weight vector.
        const auto terminal_ancestors = systematic_resample(log_weights, rng);
        std::vector<Particle> terminal_particles;
        terminal_particles.reserve(particles.size());
        for (const std::size_t ancestor : terminal_ancestors) terminal_particles.push_back(particles[ancestor]);
        particles = std::move(terminal_particles);
        log_weights.assign(config.particles, uniform_log_weight);

        std::vector<SampleRecord> retained;
        retained.reserve(particles.size());
        std::vector<std::vector<std::uint64_t>> assignment_counts(table.sites.size(), std::vector<std::uint64_t>(config.num_nodes, 0));
        std::vector<std::vector<double>> multiplicity_posterior_sums;
        multiplicity_posterior_sums.reserve(table.sites.size());
        for (const Site& site : table.sites) multiplicity_posterior_sums.emplace_back(site.multiplicity_candidates.size(), 0.0);
        SampleRecord best_sample;
        std::vector<int> best_assignments;
        bool has_best = false;

        for (std::size_t particle_index = 0; particle_index < particles.size(); ++particle_index) {
            const Particle& particle = particles[particle_index];
            const auto phi = cumulative_phi(particle.parents, particle.eta);
            const auto assignments = rb_map_assignments(table, particle);
            SampleRecord sample;
            sample.iteration = stages.size();
            sample.log_posterior = particle_log_target(table, particle, 1.0);
            sample.log_weight = uniform_log_weight;
            sample.particle_weight = uniform_particle_weight;
            sample.particle_index = particle_index;
            sample.sample_kind = "smc_particle";
            sample.parents = particle.parents;
            sample.eta = particle.eta;
            sample.phi = phi;
            sample.occupancy.assign(config.num_nodes, 0);
            for (const int node : assignments) ++sample.occupancy[static_cast<std::size_t>(node)];
            retained.push_back(sample);
            for (std::size_t site_index = 0; site_index < table.sites.size(); ++site_index) {
                ++assignment_counts[site_index][static_cast<std::size_t>(assignments[site_index])];
                std::vector<double> node_terms(config.num_nodes, 0.0);
                for (unsigned node = 0; node < config.num_nodes; ++node) node_terms[node] = site_log_likelihood(table.sites[site_index], phi[node]) + std::log(particle.eta[node]);
                const double site_normalizer = log_sum_exp(node_terms);
                for (unsigned node = 0; node < config.num_nodes; ++node) {
                    const double clone_responsibility = std::exp(node_terms[node] - site_normalizer);
                    const auto multiplicity_posterior = site_multiplicity_posterior(table.sites[site_index], phi[node]);
                    for (std::size_t candidate = 0; candidate < multiplicity_posterior.size(); ++candidate) {
                        multiplicity_posterior_sums[site_index][candidate] += clone_responsibility * multiplicity_posterior[candidate];
                    }
                }
            }
            if (!has_best || sample.log_posterior > best_sample.log_posterior) {
                best_sample = sample;
                best_assignments = assignments;
                has_best = true;
            }
        }
        if (!has_best) throw std::runtime_error("SMC retained no posterior particles");

        atomic_write_gzip(options.outdir / "samples.jsonl.gz", samples_jsonl(retained));
        atomic_write_gzip(options.outdir / "particle_history.jsonl.gz", history);
        atomic_write_gzip(options.outdir / "multiplicity_posterior.tsv.gz",
                          multiplicity_posterior_tsv(table, multiplicity_posterior_sums, retained.size()));
        atomic_write_gzip(options.outdir / "posterior_summary.tsv.gz", posterior_summary_tsv(retained, config.num_nodes));
        atomic_write_text(options.outdir / "topology_summary.tsv", topology_summary_tsv(retained));

        std::vector<double> phi_mean(config.num_nodes, 0.0);
        double minimum = retained.front().log_posterior;
        double maximum = minimum;
        double mean = 0.0;
        for (const auto& sample : retained) {
            minimum = std::min(minimum, sample.log_posterior);
            maximum = std::max(maximum, sample.log_posterior);
            mean += sample.log_posterior;
            for (std::size_t node = 0; node < sample.phi.size(); ++node) phi_mean[node] += sample.phi[node];
        }
        mean /= static_cast<double>(retained.size());
        for (double& value : phi_mean) value /= static_cast<double>(retained.size());
        std::vector<std::size_t> map_assignment(table.sites.size(), 0);
        std::vector<double> map_probability(table.sites.size(), 0.0);
        for (std::size_t site = 0; site < table.sites.size(); ++site) {
            const auto found = std::max_element(assignment_counts[site].begin(), assignment_counts[site].end());
            map_assignment[site] = static_cast<std::size_t>(std::distance(assignment_counts[site].begin(), found));
            map_probability[site] = static_cast<double>(*found) / static_cast<double>(retained.size());
        }
        std::set<std::vector<int>> unique_topologies;
        for (const auto& sample : retained) unique_topologies.insert(sample.parents);
        const double particle_diversity = static_cast<double>(unique_topologies.size()) /
            static_cast<double>(retained.size());

        std::string beta_schedule = "[0.0";
        std::string annealing_stage_json = "[";
        std::string rejuvenation_stage_json = "[";
        for (std::size_t index = 0; index < stages.size(); ++index) {
            const auto& stage = stages[index];
            beta_schedule += "," + json_number(stage.beta);
            if (index != 0) {
                annealing_stage_json += ",";
                rejuvenation_stage_json += ",";
            }
            annealing_stage_json += "{\"stage\":" + json_u64(stage.index) + ",\"beta\":" + json_number(stage.beta) +
                ",\"conditional_ess\":" + json_number(stage.conditional_ess) + ",\"weighted_ess\":" + json_number(stage.weighted_ess) +
                ",\"resampled\":" + json_bool(stage.resampled) + ",\"ancestor_diversity\":" + json_number(stage.ancestor_diversity) + "}";
            rejuvenation_stage_json += "{\"stage\":" + json_u64(stage.index) + ",\"sweeps\":" + std::to_string(config.rejuvenation_sweeps) + ",\"stop_reason\":\"fixed_sweeps\",\"eta_acceptance\":" +
                json_number(stage.eta_acceptance) + ",\"topology_acceptance\":" + json_number(stage.topology_acceptance) + "}";
        }
        beta_schedule += "]";
        annealing_stage_json += "]";
        rejuvenation_stage_json += "]";

        const double eta_rate = static_cast<double>(counters["eta_accepted"]) / static_cast<double>(std::max<std::uint64_t>(1, counters["eta_proposals"]));
        const double topology_rate = static_cast<double>(counters["topology_accepted"]) / static_cast<double>(std::max<std::uint64_t>(1, counters["topology_proposals"]));
        const std::string algorithm_name = "rao_blackwellized_annealed_smc";
        std::string diagnostics = "{\"model\":" + json_string(algorithm_name) + ",\"algorithm\":" + json_string(algorithm_name) +
            ",\"sample_semantics\":\"smc_particle\",\"checkpoint_semantics\":\"smc_stage_particle_state\",\"input_schema\":\"hcc1395_tumor_tree_input/v4\",\"input_sha256\":" + json_string(table.input_sha256) +
            ",\"observed_sites\":" + json_u64(table.sites.size()) + ",\"excluded_sites\":" + json_u64(options.exclude_ids.size()) + ",\"posterior_samples\":" + json_u64(retained.size()) +
            ",\"particle_count\":" + std::to_string(config.particles) + ",\"independent_repeat\":" + std::to_string(repeat_index + 1U) + ",\"requested_seed\":" + json_u64(config.seed) +
            ",\"derived_seed\":" + json_u64(derived_seed) + ",\"resumed\":false,\"state_variables\":[\"topology\",\"eta\"],\"rao_blackwellized_variables\":[\"assignment\",\"multiplicity\"],\"config\":" + config_json(reported_config) +
            ",\"target\":{\"tree_prior\":\"finite_K_TSSB_shaped_working_tree_prior\",\"eta_prior\":\"finite_K_TSSB_shaped_depth_width_Dirichlet_working_prior\",\"likelihood_tempering\":\"product_site_likelihood_to_beta\",\"site_terms\":\"CN_constrained_joint_multiplicity_responsibility_Rao_Blackwellized\"},\"tree_constraint\":\"exactly_one_tumor_founder_under_structural_root\",\"eta_semantics\":\"simplex_of_local_clone_masses; phi_is_descendant_sum\",\"purity_role\":\"ASCAT_purity_in_observation_emission\",\"error_rate\":0.005,\"hp_role\":\"loaded_and_conservation_checked_only; reserved_for_Model_B\",\"multiplicity_role\":\"Rao_Blackwellized_joint_responsibility; not_a_table_column\",\"multiplicity_semantics\":\"weighted_joint_responsibility_marginalized_over_clone\",\"annealing\":{\"beta_schedule\":" + beta_schedule + ",\"final_beta\":" + json_number(beta) + ",\"stages\":" + annealing_stage_json + ",\"conditional_ess_target_fraction\":" + json_number(config.conditional_ess_target) + ",\"weighted_ess_resampling_threshold_fraction\":" + json_number(config.resample_ess_threshold) + "},\"rejuvenation\":{\"min_sweeps\":" + std::to_string(config.rejuvenation_sweeps) + ",\"max_sweeps\":" + std::to_string(config.rejuvenation_sweeps) + ",\"eta_kernel\":\"prior_shaped_Dirichlet_rejuvenation\",\"topology_kernel\":\"conditional_single_founder_topology_Gibbs\",\"stages\":" + rejuvenation_stage_json + "},\"weighted_particle_ess_fraction\":" + json_number(stages.empty() ? 1.0 : stages.back().weighted_ess / static_cast<double>(config.particles)) +
            ",\"conditional_ess_fraction\":" + json_number(stages.empty() ? 1.0 : stages.back().conditional_ess / static_cast<double>(config.particles)) + ",\"particle_diversity\":" + json_number(particle_diversity) + ",\"ancestor_diversity\":" + json_number(stages.empty() ? 1.0 : stages.back().ancestor_diversity) +
            ",\"resampling_count\":" + json_u64(static_cast<std::uint64_t>(std::count_if(stages.begin(), stages.end(), [](const Stage& stage) { return stage.resampled; }))) +
            ",\"eta_acceptance\":" + json_number(eta_rate) + ",\"topology_acceptance\":" + json_number(topology_rate) + ",\"topology_change_rate\":" + json_number(topology_rate) + ",\"ccf_summary_semantics\":\"particle_weighted_quantiles\",\"topology_summary_semantics\":\"particle_weighted_canonical_edge_support\",\"particle_history_artifact\":\"particle_history.jsonl.gz\",\"posterior_summary_artifact\":\"posterior_summary.tsv.gz\",\"topology_summary_artifact\":\"topology_summary.tsv\",\"multiplicity_posterior_artifact\":\"multiplicity_posterior.tsv.gz\",\"diagnostics_contract\":\"smc_particle_diagnostics_v1\",\"phi_mean\":" + json_double_array(phi_mean) +
            ",\"log_posterior\":{\"minimum\":" + json_number(minimum) + ",\"maximum\":" + json_number(maximum) + ",\"mean\":" + json_number(mean) + "},\"checkpoint\":\"checkpoint.json.gz\"}\n";
        atomic_write_text(options.outdir / "diagnostics.json", diagnostics);

        std::string representative = "{\"model\":" + json_string(algorithm_name) + ",\"selection_semantics\":\"highest_posterior_weight_particle\",\"selected_edges\":[";
        for (std::size_t child = 0; child < best_sample.parents.size(); ++child) {
            if (child != 0) representative += ",";
            const int parent = best_sample.parents[child];
            representative += "{\"parent\":" + json_string(parent == -1 ? "tumor_root" : "clone_" + std::to_string(parent + 1)) + ",\"child\":" + json_string("clone_" + std::to_string(child + 1)) + "}";
        }
        representative += "],\"posterior_map_assignments\":{";
        for (std::size_t site = 0; site < table.sites.size(); ++site) {
            if (site != 0) representative += ",";
            representative += json_string(table.sites[site].mutation_id) + ":{\"node\":" + json_string("clone_" + std::to_string(map_assignment[site] + 1)) + ",\"probability\":" + json_number(map_probability[site]) + "}";
        }
        representative += "}}\n";
        atomic_write_text(options.outdir / "representative_tree.json", representative);

        std::string checkpoint = "{\"checkpoint_version\":3,\"checkpoint_semantics\":\"smc_stage_particle_state\",\"sample_semantics\":\"smc_particle\",\"stage\":" + json_u64(stages.size()) +
            ",\"beta\":" + json_number(beta) + ",\"input_sha256\":" + json_string(table.input_sha256) + ",\"config\":" + config_json(reported_config) + ",\"particles\":[";
        for (std::size_t index = 0; index < particles.size(); ++index) {
            if (index != 0) checkpoint += ",";
            checkpoint += "{\"particle_index\":" + json_u64(index) + ",\"topology\":{\"parents\":" + json_parent_array(particles[index].parents) + "},\"eta\":" + json_double_array(particles[index].eta) + ",\"weight\":" + json_number(uniform_particle_weight) + "}";
        }
        checkpoint += "],\"weights\":[";
        for (std::size_t index = 0; index < particles.size(); ++index) {
            if (index != 0) checkpoint += ",";
            checkpoint += json_number(uniform_particle_weight);
        }
        checkpoint += "],\"ancestor_indices\":[";
        for (std::size_t index = 0; index < particles.size(); ++index) {
            if (index != 0) checkpoint += ",";
            checkpoint += json_u64(index);
        }
        checkpoint += "],\"normalizing_constant_log_estimate\":" + json_number(log_normalizer_estimate) + ",\"rng_state\":" + rng_json(rng) + "}\n";
        atomic_write_gzip(options.outdir / "checkpoint.json.gz", checkpoint);
        atomic_write_text(options.outdir / "smc_complete.json", "{\"status\":\"complete\",\"algorithm\":" + json_string(algorithm_name) + ",\"sample_semantics\":\"smc_particle\",\"checkpoint_semantics\":\"smc_stage_particle_state\",\"particle_count\":" + std::to_string(config.particles) + ",\"artifacts\":[\"samples.jsonl.gz\",\"multiplicity_posterior.tsv.gz\",\"posterior_summary.tsv.gz\",\"topology_summary.tsv\",\"diagnostics.json\",\"representative_tree.json\",\"checkpoint.json.gz\",\"particle_history.jsonl.gz\",\"smc_complete.json\"]}\n");
        return {options.outdir, retained.size()};
    }
};

}  // namespace

void InferenceConfig::validate() const {
    if (num_nodes < 2 || num_nodes > 8) throw std::runtime_error("num-nodes must be between 2 and 8");
    if (annealing_stages == 0) throw std::runtime_error("annealing-stages must be positive");
    if (!(purity > 0.0 && purity <= 1.0)) throw std::runtime_error("purity must be in (0,1]");
    if (checkpoint_every == 0) throw std::runtime_error("checkpoint-every must be positive");
    if (threads == 0) throw std::runtime_error("threads must be positive");
    if (repeats == 0) throw std::runtime_error("repeats must be positive");
    if (particles < 2 || particles > 100000) throw std::runtime_error("particles must be between 2 and 100000");
    if (!(resample_ess_threshold > 0.0 && resample_ess_threshold < conditional_ess_target && conditional_ess_target <= 1.0)) throw std::runtime_error("SMC ESS thresholds must satisfy 0 < ess-threshold < conditional-ess-target <= 1");
    if (rejuvenation_sweeps == 0) throw std::runtime_error("rejuvenation-sweeps must be positive");
}

AlgorithmPtr make_rao_blackwellized_annealed_smc() { return std::make_unique<RaoBlackwellizedAnnealedSmcContract>(); }

}  // namespace tumor_tree_inference
