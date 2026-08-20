#include "tumor_tree_inference/model.hpp"

#include "hash.hpp"

#include <algorithm>
#include <climits>
#include <cstdint>
#include <cmath>
#include <fstream>
#include <limits>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <thread>
#include <unordered_set>
#include <utility>

#include <zlib.h>

namespace tumor_tree_inference {
namespace {

constexpr double kErrorRate = 0.005;
const std::vector<std::string> kRequiredColumns = {
    "mutation_id", "chrom", "pos", "ref", "alt", "bulk_ref", "bulk_alt", "bulk_depth",
    "hp1_1_ref", "hp1_1_alt", "hp2_1_ref", "hp2_1_alt", "major_cn", "minor_cn", "total_cn",
    "rho_ASCAT", "multiplicity_candidates", "multiplicity_prior", "model_include", "model_status"};
const std::vector<std::string> kForbiddenColumns = {"tumor_dna_fraction", "multiplicity_posteriors"};

class GzipInput final {
public:
    explicit GzipInput(const std::filesystem::path& path) : handle_(gzopen(path.string().c_str(), "rb")) {
        if (handle_ == nullptr) throw std::runtime_error("cannot open gzip canonical input: " + path.string());
    }

    GzipInput(const GzipInput&) = delete;
    GzipInput& operator=(const GzipInput&) = delete;

    ~GzipInput() {
        if (handle_ != nullptr) gzclose(handle_);
    }

    int read(void* buffer, unsigned length) { return gzread(handle_, buffer, length); }

    int close() {
        gzFile handle = handle_;
        handle_ = nullptr;
        return gzclose(handle);
    }

private:
    gzFile handle_ = nullptr;
};

std::string read_text(const std::filesystem::path& path) {
    if (path.extension() != ".gz") {
        std::ifstream input(path, std::ios::binary);
        if (!input) throw std::runtime_error("cannot open canonical input: " + path.string());
        std::ostringstream contents;
        contents << input.rdbuf();
        return contents.str();
    }
    GzipInput input(path);
    std::string contents;
    char buffer[1 << 16];
    int count = 0;
    while ((count = input.read(buffer, sizeof(buffer))) > 0) contents.append(buffer, static_cast<std::size_t>(count));
    const int close_status = input.close();
    if (count < 0 || close_status != Z_OK) throw std::runtime_error("cannot read gzip canonical input: " + path.string());
    return contents;
}

std::string trim(const std::string& value) {
    const auto first = value.find_first_not_of(" \t\r\n");
    if (first == std::string::npos) return {};
    const auto last = value.find_last_not_of(" \t\r\n");
    return value.substr(first, last - first + 1);
}

std::vector<std::string> split_tab(const std::string& line) {
    std::vector<std::string> fields;
    std::size_t start = 0;
    while (true) {
        const std::size_t separator = line.find('\t', start);
        if (separator == std::string::npos) {
            fields.push_back(line.substr(start));
            return fields;
        }
        fields.push_back(line.substr(start, separator - start));
        start = separator + 1;
    }
}

long long parse_integer(const std::string& raw, const std::string& label, const std::string& id) {
    const std::string value = trim(raw);
    if (value.empty()) throw std::runtime_error("row " + id + " is missing " + label);
    std::size_t consumed = 0;
    long long parsed = 0;
    try { parsed = std::stoll(value, &consumed); }
    catch (...) { throw std::runtime_error("row " + id + " has invalid integer " + label + "=" + value); }
    if (consumed != value.size() || parsed < 0) throw std::runtime_error("row " + id + " has invalid non-negative integer " + label);
    return parsed;
}

int parse_count(const std::string& raw, const std::string& label, const std::string& id) {
    const long long value = parse_integer(raw, label, id);
    if (value > INT_MAX) throw std::runtime_error("row " + id + " has an out-of-range count in " + label);
    return static_cast<int>(value);
}

double parse_number(const std::string& raw, const std::string& label, const std::string& id) {
    const std::string value = trim(raw);
    if (value.empty()) throw std::runtime_error("row " + id + " is missing " + label);
    std::size_t consumed = 0;
    double parsed = 0.0;
    try { parsed = std::stod(value, &consumed); }
    catch (...) { throw std::runtime_error("row " + id + " has invalid number " + label + "=" + value); }
    if (consumed != value.size() || !std::isfinite(parsed)) throw std::runtime_error("row " + id + " has non-finite " + label);
    return parsed;
}

std::vector<int> parse_candidates(const std::string& raw, const std::string& id) {
    std::vector<int> values;
    std::stringstream stream(raw);
    std::string token;
    while (std::getline(stream, token, ';')) {
        token = trim(token);
        if (token.empty()) continue;
        const long long value = parse_integer(token, "multiplicity_candidates", id);
        if (value <= 0 || value > std::numeric_limits<int>::max()) throw std::runtime_error("row " + id + " has invalid multiplicity candidate");
        values.push_back(static_cast<int>(value));
    }
    if (values.empty() || !std::is_sorted(values.begin(), values.end()) || std::adjacent_find(values.begin(), values.end()) != values.end()) {
        throw std::runtime_error("row " + id + " multiplicity_candidates must be sorted, unique and non-empty");
    }
    return values;
}

std::vector<double> parse_prior(const std::string& raw, const std::vector<int>& candidates, const std::string& id) {
    std::vector<std::pair<int, double>> entries;
    std::stringstream stream(raw);
    std::string token;
    while (std::getline(stream, token, ';')) {
        token = trim(token);
        if (token.empty()) continue;
        const auto equals = token.find('=');
        if (equals == std::string::npos || token.find('=', equals + 1) != std::string::npos) throw std::runtime_error("row " + id + " has invalid multiplicity_prior token");
        const long long key = parse_integer(token.substr(0, equals), "multiplicity_prior key", id);
        const double probability = parse_number(token.substr(equals + 1), "multiplicity_prior probability", id);
        if (key <= 0 || probability <= 0.0) throw std::runtime_error("row " + id + " has invalid multiplicity_prior value");
        entries.emplace_back(static_cast<int>(key), probability);
    }
    std::sort(entries.begin(), entries.end(), [](const auto& left, const auto& right) { return left.first < right.first; });
    if (entries.empty() || std::adjacent_find(entries.begin(), entries.end(), [](const auto& left, const auto& right) { return left.first == right.first; }) != entries.end()) {
        throw std::runtime_error("row " + id + " multiplicity_prior keys are duplicated");
    }
    std::vector<int> keys;
    std::vector<double> probabilities;
    keys.reserve(entries.size());
    probabilities.reserve(entries.size());
    for (const auto& [key, probability] : entries) { keys.push_back(key); probabilities.push_back(probability); }
    if (keys != candidates) throw std::runtime_error("row " + id + " multiplicity_prior keys disagree with candidates");
    const double total = std::accumulate(probabilities.begin(), probabilities.end(), 0.0);
    if (!std::isfinite(total) || std::abs(total - 1.0) > 1e-6) throw std::runtime_error("row " + id + " multiplicity_prior must sum to 1");
    return probabilities;
}

std::size_t column_index(const std::vector<std::string>& header, const std::string& name) {
    const auto found = std::find(header.begin(), header.end(), name);
    if (found == header.end()) throw std::runtime_error("internal missing column: " + name);
    return static_cast<std::size_t>(found - header.begin());
}

double log_binomial(int ref, int alt, double probability) {
    probability = std::clamp(probability, 1e-12, 1.0 - 1e-12);
    const std::int64_t total = static_cast<std::int64_t>(ref) + static_cast<std::int64_t>(alt);
    return std::lgamma(static_cast<double>(total) + 1.0) - std::lgamma(static_cast<double>(ref) + 1.0) -
           std::lgamma(static_cast<double>(alt) + 1.0) + static_cast<double>(alt) * std::log(probability) +
           static_cast<double>(ref) * std::log1p(-probability);
}

double log_multinomial3(const int alt0, const int alt1, const int alt2,
                        const double weight0, const double weight1, const double weight2) {
    const double total_weight = weight0 + weight1 + weight2;
    if (!(total_weight > 0.0)) return -std::numeric_limits<double>::infinity();
    double probability0 = std::max(1e-12, weight0 / total_weight);
    double probability1 = std::max(1e-12, weight1 / total_weight);
    double probability2 = std::max(1e-12, weight2 / total_weight);
    const double normalizer = probability0 + probability1 + probability2;
    probability0 /= normalizer;
    probability1 /= normalizer;
    probability2 /= normalizer;
    const std::int64_t total = static_cast<std::int64_t>(alt0) + static_cast<std::int64_t>(alt1) + static_cast<std::int64_t>(alt2);
    double result = std::lgamma(static_cast<double>(total) + 1.0);
    result -= std::lgamma(static_cast<double>(alt0) + 1.0);
    result -= std::lgamma(static_cast<double>(alt1) + 1.0);
    result -= std::lgamma(static_cast<double>(alt2) + 1.0);
    result += static_cast<double>(alt0) * std::log(probability0);
    result += static_cast<double>(alt1) * std::log(probability1);
    result += static_cast<double>(alt2) * std::log(probability2);
    return result;
}

double expected_alt_probability(const Site& site, double phi, int multiplicity) {
    const double denominator = (1.0 - site.purity) * 2.0 + site.purity * site.total_cn;
    const double cellular_fraction = site.purity * phi * static_cast<double>(multiplicity) / denominator;
    return std::clamp(kErrorRate + (1.0 - 2.0 * kErrorRate) * cellular_fraction, 1e-12, 1.0 - 1e-12);
}

double conditional_hp(const Site& site, double q_bulk, int side) {
    const std::int64_t tagged = static_cast<std::int64_t>(site.hp1_1_ref) + site.hp1_1_alt + site.hp2_1_ref + site.hp2_1_alt;
    if (tagged == 0) return 0.0;
    const double tag_fraction = std::clamp(static_cast<double>(tagged) / site.bulk_depth, 1e-9, 1.0 - 1e-9);
    const double half_tag = tag_fraction * 0.5;
    const double untagged = 1.0 - tag_fraction;
    const int untag_alt = site.bulk_alt - site.hp1_1_alt - site.hp2_1_alt;
    const int untag_ref = site.bulk_ref - site.hp1_1_ref - site.hp2_1_ref;
    const double hp1_q = side == 0 ? q_bulk : kErrorRate;
    const double hp2_q = side == 0 ? kErrorRate : q_bulk;
    return log_multinomial3(
               site.hp1_1_alt, site.hp2_1_alt, untag_alt,
               half_tag * hp1_q, half_tag * hp2_q, untagged * q_bulk) +
           log_multinomial3(
               site.hp1_1_ref, site.hp2_1_ref, untag_ref,
               half_tag * (1.0 - hp1_q), half_tag * (1.0 - hp2_q),
               untagged * (1.0 - q_bulk));
}

double site_log_likelihood_impl(const Site& site, double phi) {
    double top = -std::numeric_limits<double>::infinity();
    double scaled_sum = 0.0;
    for (std::size_t i = 0; i < site.multiplicity_candidates.size(); ++i) {
        const int multiplicity = site.multiplicity_candidates[i];
        const double q_bulk = expected_alt_probability(site, phi, multiplicity);
        const double bulk = log_binomial(site.bulk_ref, site.bulk_alt, q_bulk);
        const double hp0 = conditional_hp(site, q_bulk, 0);
        const double hp1 = conditional_hp(site, q_bulk, 1);
        const double hp = std::log(0.5) + std::max(hp0, hp1) + std::log(std::exp(hp0 - std::max(hp0, hp1)) + std::exp(hp1 - std::max(hp0, hp1)));
        const double component = std::log(site.multiplicity_prior[i]) + bulk + hp;
        if (!std::isfinite(top)) {
            top = component;
            scaled_sum = 1.0;
        } else if (component <= top) {
            scaled_sum += std::exp(component - top);
        } else {
            scaled_sum = 1.0 + scaled_sum * std::exp(top - component);
            top = component;
        }
    }
    return top + std::log(scaled_sum);
}

}  // namespace

double site_log_likelihood(const Site& site, double phi) {
    return site_log_likelihood_impl(site, phi);
}

CanonicalTable load_canonical_table(const std::filesystem::path& path,
                                    double requested_purity,
                                    const std::vector<std::string>& exclude_ids) {
    if (!std::filesystem::is_regular_file(path)) throw std::runtime_error("canonical input does not exist: " + path.string());
    if (!(requested_purity > 0.0 && requested_purity <= 1.0)) throw std::runtime_error("purity must be in (0,1]");
    const std::string text = read_text(path);
    std::istringstream lines(text);
    std::string line;
    if (!std::getline(lines, line)) throw std::runtime_error("canonical input has no header");
    line = trim(line);
    const auto header = split_tab(line);
    std::unordered_set<std::string> header_set;
    for (const auto& name : header) if (!header_set.insert(name).second) throw std::runtime_error("canonical input has duplicate header: " + name);
    for (const auto& name : kRequiredColumns) if (!header_set.count(name)) throw std::runtime_error("canonical input is missing required column: " + name);
    for (const auto& name : kForbiddenColumns) if (header_set.count(name)) throw std::runtime_error("canonical input contains forbidden legacy column: " + name);
    std::vector<std::size_t> indexes;
    indexes.reserve(kRequiredColumns.size());
    for (const auto& name : kRequiredColumns) indexes.push_back(column_index(header, name));
    std::unordered_set<std::string> excluded(exclude_ids.begin(), exclude_ids.end());
    std::unordered_set<std::string> seen_ids;
    CanonicalTable table;
    table.requested_purity = requested_purity;
    unsigned line_number = 1;
    while (std::getline(lines, line)) {
        ++line_number;
        if (!line.empty() && line.back() == '\r') line.pop_back();
        if (trim(line).empty()) continue;
        const auto fields = split_tab(line);
        if (fields.size() != header.size()) throw std::runtime_error("canonical row " + std::to_string(line_number) + " has wrong field count");
        auto field = [&](const std::string& name) -> const std::string& { return fields[column_index(header, name)]; };
        const std::string id = trim(field("mutation_id"));
        if (id.empty() || !seen_ids.insert(id).second) throw std::runtime_error("empty or duplicate mutation_id at row " + std::to_string(line_number));
        const std::string include = trim(field("model_include"));
        const std::string status = trim(field("model_status"));
        if (include != "yes" && include != "no") throw std::runtime_error("row " + id + " model_include must be yes or no");
        if (include != "yes" || status != "eligible") continue;

        Site site;
        site.mutation_id = id;
        site.chrom = trim(field("chrom"));
        site.pos = parse_integer(field("pos"), "pos", id);
        site.ref = trim(field("ref")); site.alt = trim(field("alt"));
        if (site.chrom.empty() || site.ref.empty() || site.alt.empty() || site.pos < 1) throw std::runtime_error("row " + id + " has invalid genomic key");
        site.bulk_ref = parse_count(field("bulk_ref"), "bulk_ref", id);
        site.bulk_alt = parse_count(field("bulk_alt"), "bulk_alt", id);
        site.bulk_depth = parse_count(field("bulk_depth"), "bulk_depth", id);
        const std::int64_t bulk_total = static_cast<std::int64_t>(site.bulk_ref) + static_cast<std::int64_t>(site.bulk_alt);
        if (site.bulk_depth <= 0 || static_cast<std::int64_t>(site.bulk_depth) != bulk_total) throw std::runtime_error("row " + id + " violates bulk depth conservation");
        site.hp1_1_ref = parse_count(field("hp1_1_ref"), "hp1_1_ref", id);
        site.hp1_1_alt = parse_count(field("hp1_1_alt"), "hp1_1_alt", id);
        site.hp2_1_ref = parse_count(field("hp2_1_ref"), "hp2_1_ref", id);
        site.hp2_1_alt = parse_count(field("hp2_1_alt"), "hp2_1_alt", id);
        if (static_cast<std::int64_t>(site.hp1_1_ref) + site.hp2_1_ref > site.bulk_ref || static_cast<std::int64_t>(site.hp1_1_alt) + site.hp2_1_alt > site.bulk_alt) throw std::runtime_error("row " + id + " HP counts exceed bulk counts");
        site.major_cn = parse_number(field("major_cn"), "major_cn", id);
        site.minor_cn = parse_number(field("minor_cn"), "minor_cn", id);
        site.total_cn = parse_number(field("total_cn"), "total_cn", id);
        if (site.minor_cn < 0.0 || site.major_cn < site.minor_cn || site.total_cn <= 0.0 || std::abs(site.major_cn + site.minor_cn - site.total_cn) > 1e-6) throw std::runtime_error("row " + id + " has invalid ASCAT CN state");
        site.purity = parse_number(field("rho_ASCAT"), "rho_ASCAT", id);
        if (!(site.purity > 0.0 && site.purity <= 1.0) || std::abs(site.purity - requested_purity) > 1e-9) throw std::runtime_error("row " + id + " rho_ASCAT disagrees with requested purity");
        site.multiplicity_candidates = parse_candidates(field("multiplicity_candidates"), id);
        site.multiplicity_prior = parse_prior(field("multiplicity_prior"), site.multiplicity_candidates, id);
        if (static_cast<double>(site.multiplicity_candidates.back()) > site.total_cn + 1e-9) throw std::runtime_error("row " + id + " multiplicity exceeds total_cn");
        if (!excluded.count(id)) table.sites.push_back(std::move(site));
    }
    if (table.sites.empty()) throw std::runtime_error("canonical input has no eligible non-excluded observations");
    table.input_sha256 = sha256_file(path);
    return table;
}

std::vector<std::vector<double>> likelihood_matrix(const CanonicalTable& table,
                                                   const std::vector<double>& phi,
                                                   unsigned threads) {
    if (phi.empty()) throw std::runtime_error("likelihood matrix requires at least one clone");
    std::vector<std::vector<double>> result(table.sites.size(), std::vector<double>(phi.size()));
    const unsigned worker_count = std::max(1U, std::min<unsigned>(threads, static_cast<unsigned>(table.sites.size())));
    std::vector<std::thread> workers;
    workers.reserve(worker_count);
    auto work = [&](unsigned worker) {
        for (std::size_t site_index = worker; site_index < table.sites.size(); site_index += worker_count) {
            for (std::size_t node = 0; node < phi.size(); ++node) result[site_index][node] = site_log_likelihood(table.sites[site_index], phi[node]);
        }
    };
    for (unsigned worker = 0; worker < worker_count; ++worker) workers.emplace_back(work, worker);
    for (auto& worker : workers) worker.join();
    return result;
}

}  // namespace tumor_tree_inference
