#include "tumor_tree_inference/registry.hpp"

#include <algorithm>
#include <atomic>
#include <cctype>
#include <cmath>
#include <cstdint>
#include <exception>
#include <fstream>
#include <iostream>
#include <limits>
#include <mutex>
#include <sstream>
#include <stdexcept>
#include <thread>

namespace tti = tumor_tree_inference;

namespace {

struct Cli {
    std::string algorithm = "phylowgs_inspired_tssb_mcmc";
    std::filesystem::path input;
    std::filesystem::path outdir;
    tti::InferenceConfig config;
    std::filesystem::path exclude_file;
    bool help = false;
};

std::string trim(const std::string& value) {
    const auto first = value.find_first_not_of(" \t\r\n");
    if (first == std::string::npos) return {};
    const auto last = value.find_last_not_of(" \t\r\n");
    return value.substr(first, last - first + 1);
}

[[noreturn]] void usage_error(const std::string& message) {
    throw std::runtime_error(message + "\nUse --help for usage.");
}

template <typename T>
T parse_unsigned(const std::string& value, const std::string& flag) {
    if (value.empty() || !std::all_of(value.begin(), value.end(), [](unsigned char character) { return std::isdigit(character) != 0; })) {
        usage_error("invalid non-negative integer for " + flag + ": " + value);
    }
    std::size_t consumed = 0;
    unsigned long long parsed = 0;
    try { parsed = std::stoull(value, &consumed); }
    catch (...) { usage_error("invalid value for " + flag + ": " + value); }
    if (consumed != value.size()) usage_error("invalid value for " + flag + ": " + value);
    if (parsed > static_cast<unsigned long long>(std::numeric_limits<T>::max())) usage_error("value out of range for " + flag);
    return static_cast<T>(parsed);
}

double parse_double(const std::string& value, const std::string& flag) {
    std::size_t consumed = 0;
    double parsed = 0.0;
    try { parsed = std::stod(value, &consumed); }
    catch (...) { usage_error("invalid value for " + flag + ": " + value); }
    if (consumed != value.size() || !std::isfinite(parsed)) usage_error("invalid value for " + flag + ": " + value);
    return parsed;
}

std::string require_value(int& index, int argc, char** argv, const std::string& flag) {
    if (index + 1 >= argc) usage_error("missing value for " + flag);
    return argv[++index];
}

void print_help() {
    std::cout << "tumor_tree_inference (C++17 finite-K TSSB-inspired MCMC backend)\n\n"
              << "Required:\n"
              << "  --algorithm phylowgs_inspired_tssb_mcmc\n"
              << "  --input canonical.tsv[.gz]\n"
              << "  --outdir OUTPUT_DIR\n\n"
              << "Options:\n"
              << "  --seed N --num-nodes N --iterations N --burnin N --thin N\n"
              << "  --purity RHO --checkpoint-every N --threads N --chains N\n"
              << "  --exclude-file IDS.txt --resume\n\n"
              << "Each completed chain writes samples.jsonl.gz, multiplicity_posterior.tsv.gz,\n"
              << "diagnostics.json, representative_tree.json, checkpoint.json.gz, chain_complete.json.\n";
}

Cli parse_cli(int argc, char** argv) {
    Cli cli;
    for (int index = 1; index < argc; ++index) {
        const std::string flag = argv[index];
        if (index == 1 && flag == "run") continue;
        if (flag == "--help" || flag == "-h") { cli.help = true; return cli; }
        if (flag == "--algorithm") cli.algorithm = require_value(index, argc, argv, flag);
        else if (flag == "--input") cli.input = require_value(index, argc, argv, flag);
        else if (flag == "--outdir" || flag == "--output") cli.outdir = require_value(index, argc, argv, flag);
        else if (flag == "--seed") cli.config.seed = parse_unsigned<std::uint64_t>(require_value(index, argc, argv, flag), flag);
        else if (flag == "--num-nodes") cli.config.num_nodes = parse_unsigned<unsigned>(require_value(index, argc, argv, flag), flag);
        else if (flag == "--iterations") cli.config.iterations = parse_unsigned<std::uint64_t>(require_value(index, argc, argv, flag), flag);
        else if (flag == "--burnin") cli.config.burnin = parse_unsigned<std::uint64_t>(require_value(index, argc, argv, flag), flag);
        else if (flag == "--thin") cli.config.thin = parse_unsigned<unsigned>(require_value(index, argc, argv, flag), flag);
        else if (flag == "--purity" || flag == "--rho-ascat") cli.config.purity = parse_double(require_value(index, argc, argv, flag), flag);
        else if (flag == "--checkpoint-every") cli.config.checkpoint_every = parse_unsigned<std::uint64_t>(require_value(index, argc, argv, flag), flag);
        else if (flag == "--threads") cli.config.threads = parse_unsigned<unsigned>(require_value(index, argc, argv, flag), flag);
        else if (flag == "--chains") cli.config.chains = parse_unsigned<unsigned>(require_value(index, argc, argv, flag), flag);
        else if (flag == "--exclude-file") cli.exclude_file = require_value(index, argc, argv, flag);
        else if (flag == "--resume") cli.config.resume = true;
        else usage_error("unknown option: " + flag);
    }
    if (cli.input.empty()) usage_error("--input is required");
    if (cli.outdir.empty()) usage_error("--outdir is required");
    if (cli.algorithm != "phylowgs_inspired_tssb_mcmc") usage_error("only phylowgs_inspired_tssb_mcmc is currently implemented");
    return cli;
}

std::vector<std::string> read_exclude_file(const std::filesystem::path& path) {
    if (path.empty()) return {};
    std::ifstream input(path);
    if (!input) throw std::runtime_error("cannot open exclude file: " + path.string());
    std::vector<std::string> ids;
    std::string line;
    while (std::getline(input, line)) {
        line = trim(line);
        if (!line.empty() && line.front() != '#') ids.push_back(line);
    }
    std::sort(ids.begin(), ids.end());
    ids.erase(std::unique(ids.begin(), ids.end()), ids.end());
    return ids;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const Cli cli = parse_cli(argc, argv);
        if (cli.help) { print_help(); return 0; }
        cli.config.validate();
        const auto excludes = read_exclude_file(cli.exclude_file);
        const auto table = tti::load_canonical_table(cli.input, cli.config.purity, excludes);

        std::cerr << "algorithm=" << cli.algorithm << " sites=" << table.sites.size()
                  << " chains=" << cli.config.chains << " seed=" << cli.config.seed << "\n";
        // Initialize the registry before worker creation.  The registry is
        // immutable during a run; this makes its first-use synchronization
        // explicit to race-detection tools as well as to readers.
        auto& registry = tti::AlgorithmRegistry::instance();
        std::atomic<unsigned> next_chain{0};
        std::mutex error_mutex;
        std::exception_ptr first_error;
        std::vector<tti::ChainResult> results(cli.config.chains);
        const unsigned worker_count = std::min(cli.config.chains, std::max(1U, cli.config.threads));
        auto worker = [&]() {
            while (true) {
                const unsigned chain_index = next_chain.fetch_add(1);
                if (chain_index >= cli.config.chains) return;
                try {
                    // With multiple chains, --threads controls chain parallelism and
                    // each chain uses one scorer thread to avoid oversubscription.
                    tti::InferenceConfig chain_config = cli.config;
                    if (cli.config.chains > 1) chain_config.threads = 1;
                    tti::RunOptions options;
                    options.outdir = cli.config.chains == 1
                        ? cli.outdir
                        : cli.outdir / (std::string("chain_") + (chain_index + 1 < 10 ? "0" : "") + std::to_string(chain_index + 1));
                    options.exclude_ids = excludes;
                    auto algorithm = registry.create(cli.algorithm);
                    results[chain_index] = algorithm->run(table, chain_config, options, chain_index);
                } catch (...) {
                    std::lock_guard<std::mutex> lock(error_mutex);
                    if (!first_error) first_error = std::current_exception();
                    return;
                }
            }
        };
        std::vector<std::thread> workers;
        workers.reserve(worker_count);
        for (unsigned i = 0; i < worker_count; ++i) workers.emplace_back(worker);
        for (auto& thread : workers) thread.join();
        if (first_error) {
            // A multi-chain invocation is transactional at the completion
            // marker level: a partial run must never look fully complete.
            for (const auto& result : results) {
                if (!result.outdir.empty()) {
                    std::error_code ignored;
                    std::filesystem::remove(result.outdir / "chain_complete.json", ignored);
                }
            }
            std::rethrow_exception(first_error);
        }
        for (const auto& result : results) std::cout << result.outdir << "\t" << result.posterior_samples << "\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "ERROR: " << error.what() << "\n";
        return 2;
    }
}
