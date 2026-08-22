#include "tumor_tree_inference/algorithm.hpp"

#include "json.hpp"

#include <algorithm>
#include <cerrno>
#include <cmath>
#include <cstring>
#include <fstream>
#include <fcntl.h>
#include <iomanip>
#include <map>
#include <numeric>
#include <random>
#include <sstream>
#include <stdexcept>
#include <unistd.h>

namespace tumor_tree_inference {
namespace {

constexpr std::uint64_t kCheckpointVersion = 2;
constexpr double kTssbAlphaDecay = 0.65;
constexpr double kTssbMinimumMassShape = 0.25;
const std::vector<std::string> kMoveTypes = {"assignment", "eta", "topology"};

struct State {
    std::vector<int> parents;
    std::vector<double> eta;
    std::vector<int> z;
};

struct ScoreResult {
    double score = 0.0;
    std::vector<double> phi;
};

using Counters = std::map<std::string, std::uint64_t>;

bool valid_tree(const std::vector<int>& parents) {
    for (std::size_t child = 0; child < parents.size(); ++child) {
        const int parent = parents[child];
        if (parent < -1 || parent >= static_cast<int>(parents.size()) || parent == static_cast<int>(child)) return false;
        std::vector<bool> seen(parents.size(), false);
        seen[child] = true;
        int cursor = parent;
        while (cursor != -1) {
            if (seen[static_cast<std::size_t>(cursor)]) return false;
            seen[static_cast<std::size_t>(cursor)] = true;
            cursor = parents[static_cast<std::size_t>(cursor)];
        }
    }
    return true;
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

ScoreResult score_state(const CanonicalTable& table, const InferenceConfig& config, const State& state) {
    if (state.z.size() != table.sites.size() || state.parents.size() != config.num_nodes) throw std::runtime_error("state dimensions do not match model/config");
    const auto phi = cumulative_phi(state.parents, state.eta);
    const auto prior_alpha = tssb_mass_prior_alpha(state.parents);
    double score = tssb_tree_log_prior(state.parents) + dirichlet_logpdf(state.eta, prior_alpha);
    // Fixed site-index reduction: the result is independent of worker scheduling.
    for (std::size_t site = 0; site < state.z.size(); ++site) {
        const int node = state.z[site];
        if (node < 0 || node >= static_cast<int>(config.num_nodes)) throw std::runtime_error("assignment outside clone range");
        score += site_log_likelihood(table.sites[site], phi[static_cast<std::size_t>(node)]) + std::log(state.eta[static_cast<std::size_t>(node)]);
    }
    return {score, phi};
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

std::string counters_json(const Counters& counters) {
    std::string result = "{";
    bool first = true;
    for (const auto& [key, value] : counters) {
        if (!first) result += ",";
        first = false;
        result += json_string(key) + ":" + json_u64(value);
    }
    return result + "}";
}

std::string config_json(const InferenceConfig& config) {
    return "{\"seed\":" + json_u64(config.seed) + ",\"num_nodes\":" + std::to_string(config.num_nodes) +
           ",\"iterations\":" + json_u64(config.iterations) + ",\"burnin\":" + json_u64(config.burnin) +
           ",\"thin\":" + std::to_string(config.thin) + ",\"ascat_purity\":" + json_number(config.purity) +
           ",\"checkpoint_every\":" + json_u64(config.checkpoint_every) + "}";
}

std::string rng_json(const std::mt19937_64& rng) {
    std::ostringstream stream;
    stream << rng;
    return json_string(stream.str());
}

std::string assignment_counts_json(const std::vector<std::vector<std::uint64_t>>& counts) {
    std::string result = "[";
    for (std::size_t i = 0; i < counts.size(); ++i) {
        if (i != 0) result += ",";
        result += json_u64_array(counts[i]);
    }
    return result + "]";
}

std::uint64_t chain_seed(std::uint64_t seed, unsigned chain_index) {
    // The chain index is part of the seed derivation; no RNG or mutable state is shared.
    return seed + static_cast<std::uint64_t>(chain_index);
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

std::string checkpoint_json(const CanonicalTable& table, const InferenceConfig& reported_config,
                            std::uint64_t requested_seed,
                            const std::vector<std::string>& exclude_ids, std::uint64_t next_iteration,
                            const State& state, double score, const Counters& counters,
                            const std::vector<SampleRecord>& retained, const std::vector<std::vector<std::uint64_t>>& counts,
                            const SampleRecord* best_sample, const std::vector<int>* best_assignments,
                            const std::mt19937_64& rng, unsigned chain_index) {
    std::string result = "{\"checkpoint_version\":" + json_u64(kCheckpointVersion) +
        ",\"input_sha256\":" + json_string(table.input_sha256) + ",\"config\":" + config_json(reported_config) +
        ",\"requested_seed\":" + json_u64(requested_seed) + ",\"chain_index\":" + std::to_string(chain_index) + ",\"derived_seed\":" + json_u64(reported_config.seed) +
        ",\"exclude_ids\":" + json_string_array(exclude_ids) + ",\"next_iteration\":" + json_u64(next_iteration) +
        ",\"parents\":" + json_parent_array(state.parents) + ",\"eta\":" + json_double_array(state.eta) +
        ",\"z\":" + json_int_array(state.z) + ",\"score\":" + json_number(score) + ",\"counters\":" + counters_json(counters) +
        ",\"retained_samples\":" + sample_array_json(retained) + ",\"assignment_counts\":" + assignment_counts_json(counts);
    if (best_sample == nullptr) result += ",\"best_sample\":null,\"best_assignments\":null";
    else result += ",\"best_sample\":" + sample_json(*best_sample) + ",\"best_assignments\":" + json_int_array(*best_assignments);
    return result + ",\"rng_state\":" + rng_json(rng) + "}\n";
}

std::string samples_jsonl(const std::vector<SampleRecord>& samples) {
    std::string result;
    for (const auto& sample : samples) result += sample_json(sample) + "\n";
    return result;
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
    for (const auto& move : kMoveTypes) {
        counters[move + "_proposals"] = 0;
        counters[move + "_accepted"] = 0;
    }
}

class PhyloWgsInspiredTssbMcmc final : public Algorithm {
public:
    const std::string& name() const override {
        static const std::string algorithm_name = "phylowgs_inspired_tssb_mcmc";
        return algorithm_name;
    }

    ChainResult run(const CanonicalTable& table, const InferenceConfig& config,
                    const RunOptions& options, unsigned chain_index) const override {
        config.validate();
        if (config.resume) throw std::runtime_error("--resume is fail-closed: C++ checkpoint restore is not implemented; use a new outdir");
        if (std::filesystem::exists(options.outdir)) {
            if (!std::filesystem::is_directory(options.outdir) || !std::filesystem::is_empty(options.outdir)) throw std::runtime_error("refusing to overwrite non-empty output directory: " + options.outdir.string());
        } else {
            std::filesystem::create_directories(options.outdir);
        }
        // The empty-directory check above is intentionally followed by an
        // O_EXCL lock.  This closes the TOCTOU window when two processes are
        // accidentally pointed at the same chain directory.
        OutputLock output_lock(options.outdir);

        const std::uint64_t derived_seed = chain_seed(config.seed, chain_index);
        InferenceConfig reported_config = config;
        reported_config.seed = derived_seed;
        std::mt19937_64 rng(derived_seed);
        State state;
        state.parents.resize(config.num_nodes);
        // Start from a shallow TSSB truncation.  This avoids giving every
        // chain the same artificial linear topology before the Gibbs kernel
        // has had a chance to explore the tree.
        std::fill(state.parents.begin(), state.parents.end(), -1);
        state.eta.assign(config.num_nodes, 1.0 / static_cast<double>(config.num_nodes));
        const auto initial_phi = cumulative_phi(state.parents, state.eta);
        const auto initial_matrix = likelihood_matrix(table, initial_phi, config.threads);
        state.z.resize(table.sites.size());
        std::vector<double> log_weights(config.num_nodes, 0.0);
        for (std::size_t site = 0; site < state.z.size(); ++site) {
            for (unsigned node = 0; node < config.num_nodes; ++node) log_weights[node] = initial_matrix[site][node] + std::log(state.eta[node]);
            state.z[site] = static_cast<int>(sample_log_categorical(log_weights, rng));
        }
        auto current = score_state(table, config, state);
        double current_score = current.score;
        std::vector<double> current_phi = std::move(current.phi);

        Counters counters;
        initialize_counters(counters);
        std::vector<SampleRecord> retained;
        std::vector<std::vector<std::uint64_t>> assignment_counts(table.sites.size(), std::vector<std::uint64_t>(config.num_nodes, 0));
        std::vector<std::vector<double>> multiplicity_posterior_sums;
        multiplicity_posterior_sums.reserve(table.sites.size());
        for (const Site& site : table.sites) {
            multiplicity_posterior_sums.emplace_back(site.multiplicity_candidates.size(), 0.0);
        }
        SampleRecord best_sample;
        std::vector<int> best_assignments;
        bool has_best = false;
        auto write_checkpoint = [&](std::uint64_t next_iteration) {
            atomic_write_gzip(options.outdir / "checkpoint.json.gz", checkpoint_json(table, reported_config, config.seed, options.exclude_ids, next_iteration, state, current_score, counters, retained, assignment_counts, has_best ? &best_sample : nullptr, has_best ? &best_assignments : nullptr, rng, chain_index));
        };

        for (std::uint64_t iteration = 0; iteration < config.iterations; ++iteration) {
            // 1) Assignment Gibbs sweep.  The current phi is held fixed for
            // this sweep, so the likelihood matrix is evaluated once and
            // every SNV can move directly to any clone.
            const auto assignment_matrix = likelihood_matrix(table, current_phi, config.threads);
            for (std::size_t site = 0; site < state.z.size(); ++site) {
                const int old_node = state.z[site];
                for (unsigned node = 0; node < config.num_nodes; ++node) log_weights[node] = assignment_matrix[site][node] + std::log(state.eta[node]);
                state.z[site] = static_cast<int>(sample_log_categorical(log_weights, rng));
                ++counters["assignment_proposals"];
                if (state.z[site] != old_node) ++counters["assignment_accepted"];
                current_score += assignment_matrix[site][static_cast<std::size_t>(state.z[site])] + std::log(state.eta[static_cast<std::size_t>(state.z[site])]);
                current_score -= assignment_matrix[site][static_cast<std::size_t>(old_node)] + std::log(state.eta[static_cast<std::size_t>(old_node)]);
            }

            // 2) Resample local masses from a TSSB-shaped Dirichlet proposal.
            // The proposal depends on the fixed assignment/tree but not on
            // the current eta, so its forward/reverse density cancels.  The
            // emission term still makes this an MH correction, not a naive
            // conjugate Gibbs update.
            std::vector<std::uint64_t> occupancy(config.num_nodes, 0);
            for (int node : state.z) ++occupancy[static_cast<std::size_t>(node)];
            auto eta_alpha = tssb_mass_prior_alpha(state.parents);
            for (unsigned node = 0; node < config.num_nodes; ++node) eta_alpha[node] += static_cast<double>(occupancy[node]);
            const auto proposal_eta = dirichlet_sample(eta_alpha, rng);
            auto eta_proposal = state;
            eta_proposal.eta = proposal_eta;
            const auto eta_result = score_state(table, config, eta_proposal);
            ++counters["eta_proposals"];
            if (std::log(std::max(1e-300, std::generate_canonical<double, 53>(rng))) < eta_result.score - current_score) {
                state = std::move(eta_proposal);
                current_score = eta_result.score;
                current_phi = eta_result.phi;
                ++counters["eta_accepted"];
            }

            // 3) Conditional subtree prune-and-regraft.  A selected node is
            // detached together with its descendants and reattached to every
            // legal parent in its finite support.  Sampling the support by
            // posterior mass is a Gibbs update; it does not suffer from the
            // old uniform-proposal topology acceptance collapse.
            std::uniform_int_distribution<std::size_t> node_distribution(0, config.num_nodes - 1U);
            const std::size_t node = node_distribution(rng);
            const auto support = topology_support_for_node(state.parents, node);
            if (!support.empty()) {
                std::vector<double> support_scores;
                support_scores.reserve(support.size());
                std::vector<ScoreResult> support_results;
                support_results.reserve(support.size());
                for (const auto& parents : support) {
                    auto proposal = state;
                    proposal.parents = parents;
                    auto result = score_state(table, config, proposal);
                    support_scores.push_back(result.score);
                    support_results.push_back(std::move(result));
                }
                const std::size_t selected = sample_log_categorical(support_scores, rng);
                ++counters["topology_proposals"];
                if (support[selected][node] != state.parents[node]) ++counters["topology_accepted"];
                state.parents = support[selected];
                current_score = support_results[selected].score;
                current_phi = support_results[selected].phi;
            }

            const std::uint64_t completed_iteration = iteration + 1U;
            if (completed_iteration > config.burnin && ((completed_iteration - config.burnin - 1U) % config.thin == 0U)) {
                const auto phi = cumulative_phi(state.parents, state.eta);
                SampleRecord sample;
                sample.iteration = completed_iteration;
                sample.log_posterior = current_score;
                sample.parents = state.parents;
                sample.eta = state.eta;
                sample.phi = phi;
                sample.occupancy.assign(config.num_nodes, 0);
                for (int node : state.z) ++sample.occupancy[static_cast<std::size_t>(node)];
                retained.push_back(sample);
                for (std::size_t site = 0; site < state.z.size(); ++site) {
                    ++assignment_counts[site][static_cast<std::size_t>(state.z[site])];
                    const auto multiplicity_posterior = site_multiplicity_posterior(
                        table.sites[site], phi[static_cast<std::size_t>(state.z[site])]);
                    for (std::size_t candidate = 0; candidate < multiplicity_posterior.size(); ++candidate) {
                        multiplicity_posterior_sums[site][candidate] += multiplicity_posterior[candidate];
                    }
                }
                if (!has_best || current_score > best_sample.log_posterior) { best_sample = sample; best_assignments = state.z; has_best = true; }
            }
            if (completed_iteration % config.checkpoint_every == 0U) write_checkpoint(completed_iteration);
        }
        if (!has_best) throw std::runtime_error("chain retained no posterior samples");
        write_checkpoint(config.iterations);

        const auto samples_path = options.outdir / "samples.jsonl.gz";
        atomic_write_gzip(samples_path, samples_jsonl(retained));
        atomic_write_gzip(
            options.outdir / "multiplicity_posterior.tsv.gz",
            multiplicity_posterior_tsv(table, multiplicity_posterior_sums, retained.size()));
        double minimum = retained.front().log_posterior, maximum = minimum, mean = 0.0;
        for (const auto& sample : retained) { minimum = std::min(minimum, sample.log_posterior); maximum = std::max(maximum, sample.log_posterior); mean += sample.log_posterior; }
        mean /= static_cast<double>(retained.size());
        std::vector<double> phi_mean(config.num_nodes, 0.0);
        for (const auto& sample : retained) {
            for (std::size_t node = 0; node < sample.phi.size(); ++node) phi_mean[node] += sample.phi[node];
        }
        for (double& value : phi_mean) value /= static_cast<double>(retained.size());
        std::vector<std::size_t> map_assignment(table.sites.size(), 0);
        std::vector<double> map_probability(table.sites.size(), 0.0);
        for (std::size_t site = 0; site < table.sites.size(); ++site) {
            const auto found = std::max_element(assignment_counts[site].begin(), assignment_counts[site].end());
            map_assignment[site] = static_cast<std::size_t>(std::distance(assignment_counts[site].begin(), found));
            map_probability[site] = static_cast<double>(*found) / static_cast<double>(retained.size());
        }
        const std::string model_name = "finite_K_tssb_inspired";
        const auto assignment_rate = static_cast<double>(counters["assignment_accepted"]) / static_cast<double>(std::max<std::uint64_t>(1, counters["assignment_proposals"]));
        const auto eta_rate = static_cast<double>(counters["eta_accepted"]) / static_cast<double>(std::max<std::uint64_t>(1, counters["eta_proposals"]));
        const auto topology_rate = static_cast<double>(counters["topology_accepted"]) / static_cast<double>(std::max<std::uint64_t>(1, counters["topology_proposals"]));
        std::string diagnostics = "{\"model\":" + json_string(model_name) + ",\"algorithm\":\"single_chain_phylowgs_inspired_tssb_mcmc\",\"input_schema\":\"hcc1395_tumor_tree_input/v4\",\"input_sha256\":" + json_string(table.input_sha256) + ",\"observed_sites\":" + json_u64(table.sites.size()) + ",\"excluded_sites\":" + json_u64(options.exclude_ids.size()) + ",\"posterior_samples\":" + json_u64(retained.size()) + ",\"config\":" + config_json(reported_config) + ",\"requested_seed\":" + json_u64(config.seed) + ",\"chain_index\":" + std::to_string(chain_index) + ",\"derived_seed\":" + json_u64(derived_seed) + ",\"resumed\":false,\"state_variables\":[\"parents\",\"eta\",\"z\"],\"target\":{\"tree_prior\":\"finite_truncated_TSSB_depth_and_branching_prior\",\"eta_prior\":\"TSSB_shaped_depth_width_Dirichlet\",\"assignment_prior\":\"categorical_local_node_mass\",\"site_terms\":\"CN_constrained_multiplicity_candidates_marginalized_with_emission_posterior\"},\"eta_semantics\":\"simplex_of_local_clone_masses; phi_is_descendant_sum\",\"purity_role\":\"ASCAT_purity_in_observation_emission\",\"multiplicity_role\":\"CN_constrained_latent_state_with_per_site_posterior; not_a_table_column\",\"multiplicity_posterior_artifact\":\"multiplicity_posterior.tsv.gz\",\"ps_role\":\"upstream_phase_block_used_to_derive_HP_counts; not_an_explicit_downstream_state_or_tree_constraint\",\"proposal_kernel\":{\"compound_sweep_per_iteration\":true,\"assignment\":\"all_SNV_categorical_Gibbs_sweep\",\"eta\":\"TSSB_shaped_Dirichlet_independence_MH_with_emission_correction\",\"topology\":\"conditional_subtree_prune_and_regraft_Gibbs_over_valid_parents\"},\"hastings_correction\":{\"assignment_gibbs\":true,\"eta_independence_MH\":true,\"topology_gibbs\":true},\"assignment_acceptance\":" + json_number(assignment_rate) + ",\"eta_acceptance\":" + json_number(eta_rate) + ",\"topology_acceptance\":" + json_number(topology_rate) + ",\"acceptance_semantics\":{\"assignment\":\"fraction_of_SNV_Gibbs_updates_that_changed_label\",\"eta\":\"MH_acceptance\",\"topology\":\"fraction_of_conditional_parent_updates_that_changed_parent\"},\"counters\":" + counters_json(counters) + ",\"log_posterior\":{\"minimum\":" + json_number(minimum) + ",\"maximum\":" + json_number(maximum) + ",\"mean\":" + json_number(mean) + "},\"checkpoint\":\"checkpoint.json.gz\"}\n";
        const std::string checkpoint_marker = ",\"checkpoint\":\"checkpoint.json.gz\"";
        const auto marker_position = diagnostics.rfind(checkpoint_marker);
        if (marker_position == std::string::npos) throw std::runtime_error("internal diagnostics checkpoint marker is missing");
        diagnostics.insert(marker_position, ",\"phi_mean\":" + json_double_array(phi_mean));
        atomic_write_text(options.outdir / "diagnostics.json", diagnostics);

        std::string representative = "{\"model\":" + json_string(model_name) + ",\"posterior_status\":\"candidate_tree\",\"root\":\"tumor_root\",\"root_semantics\":\"structural_root_with_frequency_one; eta_contains_clone_masses_only\",\"selected_edges\":[";
        for (std::size_t child = 0; child < best_sample.parents.size(); ++child) {
            if (child != 0) representative += ",";
            const int parent = best_sample.parents[child];
            representative += "{\"parent\":" + json_string(parent == -1 ? "tumor_root" : "clone_" + std::to_string(parent + 1)) + ",\"child\":" + json_string("clone_" + std::to_string(child + 1)) + "}";
        }
        representative += "],\"best_sample\":" + sample_json(best_sample) + ",\"best_sample_assignments\":{";
        for (std::size_t site = 0; site < table.sites.size(); ++site) {
            if (site != 0) representative += ",";
            representative += json_string(table.sites[site].mutation_id) + ":" + json_string("clone_" + std::to_string(best_assignments[site] + 1));
        }
        representative += "},\"posterior_map_assignments\":{";
        for (std::size_t site = 0; site < table.sites.size(); ++site) {
            if (site != 0) representative += ",";
            representative += json_string(table.sites[site].mutation_id) + ":{\"node\":" + json_string("clone_" + std::to_string(map_assignment[site] + 1)) + ",\"probability\":" + json_number(map_probability[site]) + "}";
        }
        representative += "}}\n";
        atomic_write_text(options.outdir / "representative_tree.json", representative);
        atomic_write_text(options.outdir / "chain_complete.json", "{\"status\":\"complete\",\"input_sha256\":" + json_string(table.input_sha256) + ",\"posterior_samples\":" + json_u64(retained.size()) + ",\"artifacts\":[\"samples.jsonl.gz\",\"multiplicity_posterior.tsv.gz\",\"diagnostics.json\",\"representative_tree.json\",\"checkpoint.json.gz\"]}\n");
        return {options.outdir, retained.size()};
    }
};

}  // namespace

void InferenceConfig::validate() const {
    if (num_nodes < 2 || num_nodes > 8) throw std::runtime_error("num-nodes must be between 2 and 8");
    if (iterations <= burnin) throw std::runtime_error("iterations must exceed burnin");
    if (thin == 0) throw std::runtime_error("thin must be positive");
    if (!(purity > 0.0 && purity <= 1.0)) throw std::runtime_error("purity must be in (0,1]");
    if (checkpoint_every == 0) throw std::runtime_error("checkpoint-every must be positive");
    if (threads == 0) throw std::runtime_error("threads must be positive");
    if (chains == 0) throw std::runtime_error("chains must be positive");
}

AlgorithmPtr make_phylowgs_inspired_tssb_mcmc() { return std::make_unique<PhyloWgsInspiredTssbMcmc>(); }

}  // namespace tumor_tree_inference
