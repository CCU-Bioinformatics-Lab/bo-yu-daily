#include "tumor_tree_inference/registry.hpp"

#include <cassert>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <stdexcept>

#include <zlib.h>

namespace {

std::string read_gzip(const std::filesystem::path& path) {
    gzFile input = gzopen(path.string().c_str(), "rb");
    if (!input) throw std::runtime_error("cannot open smoke gzip");
    std::string result;
    char buffer[4096];
    int count = 0;
    while ((count = gzread(input, buffer, sizeof(buffer))) > 0) result.append(buffer, static_cast<std::size_t>(count));
    if (gzclose(input) != Z_OK || count < 0) throw std::runtime_error("cannot read smoke gzip");
    return result;
}

std::string read_text(const std::filesystem::path& path) {
    std::ifstream input(path);
    if (!input) throw std::runtime_error("cannot open smoke text");
    std::ostringstream contents;
    contents << input.rdbuf();
    return contents.str();
}

void write_table(const std::filesystem::path& path, bool alternate_hp = false) {
    std::ofstream output(path);
    output << "mutation_id\tchrom\tpos\tref\talt\tref_reads\talt_reads\ttotal_reads\t"
              "hp1_1_ref\thp1_1_alt\thp2_1_ref\thp2_1_alt\tmajor_cn\tminor_cn\ttotal_cn\t"
              "rho_ASCAT\tmodel_include\tmodel_status\n";
    output << "chr1:10:A>G\tchr1\t10\tA\tG\t3\t2\t5\t"
            << (alternate_hp ? "0\t2\t0\t0" : "1\t2\t0\t0")
            << "\t2\t1\t3\t0.99\tyes\teligible\n";
    output << "chr1:20:C>T\tchr1\t20\tC\tT\t4\t1\t5\t"
            << (alternate_hp ? "0\t0\t0\t1" : "1\t0\t0\t1")
            << "\t2\t0\t2\t0.99\tyes\teligible\n";
    output << "chr1:30:G>A\tchr1\t30\tG\tA\t2\t3\t5\t"
            << (alternate_hp ? "0\t2\t0\t0" : "1\t1\t0\t0")
            << "\t3\t1\t4\t0.99\tyes\teligible\n";
}

void gzip_copy(const std::filesystem::path& input_path, const std::filesystem::path& output_path) {
    std::ifstream input(input_path, std::ios::binary);
    if (!input) throw std::runtime_error("cannot open smoke input for gzip");
    std::ostringstream contents;
    contents << input.rdbuf();
    gzFile output = gzopen(output_path.string().c_str(), "wb6");
    if (!output) throw std::runtime_error("cannot create smoke gzip");
    const std::string text = contents.str();
    if (gzwrite(output, text.data(), static_cast<unsigned>(text.size())) != static_cast<int>(text.size()) || gzclose(output) != Z_OK) throw std::runtime_error("cannot write smoke gzip");
}

}  // namespace

int main() {
    namespace fs = std::filesystem;
    namespace tti = tumor_tree_inference;
    const fs::path root = fs::temp_directory_path() / "tumor_tree_inference_cpp_smoke";
    std::error_code ignored;
    fs::remove_all(root, ignored);
    fs::create_directories(root);
    const fs::path input = root / "canonical.tsv";
    const fs::path hp_changed_input = root / "canonical_hp_changed.tsv";
    const fs::path compressed_input = root / "canonical.tsv.gz";
    write_table(input);
    write_table(hp_changed_input, true);
    gzip_copy(input, compressed_input);

    const auto loaded = tti::load_canonical_table(input, 0.99, {});
    const auto loaded_hp_changed = tti::load_canonical_table(hp_changed_input, 0.99, {});
    assert(loaded.sites.size() == 3);
    assert((loaded.sites[0].multiplicity_candidates == std::vector<int>{1, 2}));
    assert(std::abs(loaded.sites[0].multiplicity_prior[0] - 0.75) < 1e-12);
    assert(std::abs(loaded.sites[0].multiplicity_prior[1] - 0.25) < 1e-12);
    assert((loaded.sites[2].multiplicity_candidates == std::vector<int>{1, 2, 3}));
    assert(std::abs(loaded.sites[2].multiplicity_prior[0] - (2.0 / 3.0)) < 1e-12);
    assert(std::abs(loaded.sites[2].multiplicity_prior[1] - (1.0 / 6.0)) < 1e-12);
    assert(std::abs(loaded.sites[2].multiplicity_prior[2] - (1.0 / 6.0)) < 1e-12);
    const auto multiplicity_posterior = tti::site_multiplicity_posterior(loaded.sites[2], 0.5);
    assert(multiplicity_posterior.size() == loaded.sites[2].multiplicity_candidates.size());
    double posterior_sum = 0.0;
    for (double value : multiplicity_posterior) {
        assert(value >= 0.0 && value <= 1.0);
        posterior_sum += value;
    }
    assert(std::abs(posterior_sum - 1.0) < 1e-12);
    assert(std::abs(multiplicity_posterior[0] - loaded.sites[2].multiplicity_prior[0]) > 1e-6);

    // Model A contract: HP counts remain schema-validated supplementary data
    // and must not change the bulk/CN/purity likelihood or multiplicity
    // posterior when those active observations are held fixed.
    for (std::size_t site = 0; site < loaded.sites.size(); ++site) {
        const double baseline_score = tti::site_log_likelihood(loaded.sites[site], 0.5);
        const double changed_score = tti::site_log_likelihood(loaded_hp_changed.sites[site], 0.5);
        assert(std::abs(baseline_score - changed_score) < 1e-12);
        const auto baseline_posterior = tti::site_multiplicity_posterior(loaded.sites[site], 0.5);
        const auto changed_posterior = tti::site_multiplicity_posterior(loaded_hp_changed.sites[site], 0.5);
        assert(baseline_posterior.size() == changed_posterior.size());
        for (std::size_t candidate = 0; candidate < baseline_posterior.size(); ++candidate) {
            assert(std::abs(baseline_posterior[candidate] - changed_posterior[candidate]) < 1e-12);
        }
    }

    tti::InferenceConfig config;
    config.seed = 1234;
    config.num_nodes = 3;
    config.annealing_stages = 12;
    config.purity = 0.99;
    config.checkpoint_every = 2;
    config.threads = 1;
    config.repeats = 1;
    auto algorithm = tti::AlgorithmRegistry::instance().create("rao_blackwellized_annealed_smc");
    tti::RunOptions one_options{root / "one", {}};
    algorithm->run(tti::load_canonical_table(compressed_input, 0.99, {}), config, one_options, 0);
    tti::RunOptions hp_changed_options{root / "hp_changed", {}};
    algorithm->run(loaded_hp_changed, config, hp_changed_options, 0);
    config.threads = 2;
    tti::RunOptions two_options{root / "two", {}};
    algorithm->run(tti::load_canonical_table(input, 0.99, {}), config, two_options, 0);

    for (const auto& directory : {one_options.outdir, two_options.outdir}) {
        for (const auto& name : {"samples.jsonl.gz", "multiplicity_posterior.tsv.gz", "posterior_summary.tsv.gz", "topology_summary.tsv", "diagnostics.json", "representative_tree.json", "checkpoint.json.gz", "smc_complete.json", "particle_history.jsonl.gz"}) assert(fs::is_regular_file(directory / name));
        const std::string samples = read_gzip(directory / "samples.jsonl.gz");
        assert(samples.find("\"sample_kind\":\"smc_particle\"") != std::string::npos);
        const std::string multiplicity_table = read_gzip(directory / "multiplicity_posterior.tsv.gz");
        assert(multiplicity_table.find("mutation_id\tmultiplicity\tprior\tposterior_mean") == 0);
        assert(multiplicity_table.find("chr1:10:A>G\t") != std::string::npos);
        const std::string posterior_summary = read_gzip(directory / "posterior_summary.tsv.gz");
        assert(posterior_summary.find("clone\tccf_median\tccf_q025\tccf_q975\tphi_median\tphi_q025\tphi_q975") == 0);
        const std::string topology_summary = read_text(directory / "topology_summary.tsv");
        assert(topology_summary.find("parent\tchild\tsupport_count\tretained_samples\tsupport_fraction") == 0);
        const std::string representative = read_text(directory / "representative_tree.json");
        const std::string founder_marker = "\"parent\":\"tumor_root\"";
        std::size_t founder_count = 0;
        std::size_t founder_position = 0;
        while ((founder_position = representative.find(founder_marker, founder_position)) != std::string::npos) {
            ++founder_count;
            founder_position += founder_marker.size();
        }
        assert(founder_count == 1);
    }
    assert(read_gzip(one_options.outdir / "samples.jsonl.gz") ==
           read_gzip(hp_changed_options.outdir / "samples.jsonl.gz"));
    assert(read_gzip(one_options.outdir / "multiplicity_posterior.tsv.gz") ==
           read_gzip(hp_changed_options.outdir / "multiplicity_posterior.tsv.gz"));
    assert(read_gzip(one_options.outdir / "samples.jsonl.gz") == read_gzip(two_options.outdir / "samples.jsonl.gz"));
    // Checkpoint is a resumability/audit artifact, not the cross-thread
    // byte-level deterministic contract: runtime parallelization metadata may
    // legitimately differ even when retained posterior states are identical.
    for (const auto& directory : {one_options.outdir, two_options.outdir}) {
        const std::string checkpoint = read_gzip(directory / "checkpoint.json.gz");
        assert(checkpoint.find("\"checkpoint_version\":3") != std::string::npos);
        assert(checkpoint.find("\"sample_semantics\":\"smc_particle\"") != std::string::npos);
        assert(checkpoint.find("\"checkpoint_semantics\":\"smc_stage_particle_state\"") != std::string::npos);
        assert(checkpoint.find("\"input_sha256\":") != std::string::npos);
        assert(checkpoint.find("\"stage\":") != std::string::npos);
        assert(checkpoint.find("\"beta\":") != std::string::npos);
        assert(checkpoint.find("\"particles\":") != std::string::npos);
        assert(checkpoint.find("\"weights\":") != std::string::npos);
        assert(checkpoint.find("\"ancestor_indices\":") != std::string::npos);
        assert(checkpoint.find("\"rng_state\":") != std::string::npos);
    }
    std::ifstream diagnostics(one_options.outdir / "diagnostics.json");
    std::stringstream diagnostic_text;
    diagnostic_text << diagnostics.rdbuf();
    assert(diagnostic_text.str().find("rao_blackwellized_annealed_smc") != std::string::npos);
    assert(diagnostic_text.str().find("smc_particle") != std::string::npos);
    assert(diagnostic_text.str().find("conditional_ess") != std::string::npos);
    assert(diagnostic_text.str().find("weighted_ess") != std::string::npos);
    assert(diagnostic_text.str().find("rejuvenation") != std::string::npos);
    assert(diagnostic_text.str().find("multiplicity_posterior.tsv.gz") != std::string::npos);
    assert(diagnostic_text.str().find("particle_weighted_quantiles") != std::string::npos);
    assert(diagnostic_text.str().find("mcmc") == std::string::npos);
    fs::remove_all(root, ignored);
    return 0;
}
