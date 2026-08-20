#include "tumor_tree_inference/registry.hpp"

#include <cassert>
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

void write_table(const std::filesystem::path& path) {
    std::ofstream output(path);
    output << "mutation_id\tchrom\tpos\tref\talt\tbulk_ref\tbulk_alt\tbulk_depth\t"
              "hp1_1_ref\thp1_1_alt\thp2_1_ref\thp2_1_alt\tmajor_cn\tminor_cn\ttotal_cn\t"
              "rho_ASCAT\tmultiplicity_candidates\tmultiplicity_prior\tmodel_include\tmodel_status\n";
    output << "chr1:10:A>G\tchr1\t10\tA\tG\t3\t2\t5\t0\t2\t0\t0\t2\t1\t3\t0.99\t1;2\t1=0.75;2=0.25\tyes\teligible\n";
    output << "chr1:20:C>T\tchr1\t20\tC\tT\t4\t1\t5\t0\t0\t0\t1\t2\t0\t2\t0.99\t1;2\t1=0.5;2=0.5\tyes\teligible\n";
    output << "chr1:30:G>A\tchr1\t30\tG\tA\t2\t3\t5\t0\t1\t0\t0\t3\t1\t4\t0.99\t1;2;3\t1=0.5;2=0.3;3=0.2\tyes\teligible\n";
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
    const fs::path compressed_input = root / "canonical.tsv.gz";
    write_table(input);
    gzip_copy(input, compressed_input);

    tti::InferenceConfig config;
    config.seed = 1234;
    config.num_nodes = 3;
    config.iterations = 12;
    config.burnin = 4;
    config.thin = 1;
    config.purity = 0.99;
    config.checkpoint_every = 2;
    config.threads = 1;
    config.chains = 1;
    auto algorithm = tti::AlgorithmRegistry::instance().create("phylowgs_inspired_tssb_mcmc");
    tti::RunOptions one_options{root / "one", {}};
    algorithm->run(tti::load_canonical_table(compressed_input, 0.99, {}), config, one_options, 0);
    config.threads = 2;
    tti::RunOptions two_options{root / "two", {}};
    algorithm->run(tti::load_canonical_table(input, 0.99, {}), config, two_options, 0);

    for (const auto& directory : {one_options.outdir, two_options.outdir}) {
        for (const auto& name : {"samples.jsonl.gz", "diagnostics.json", "representative_tree.json", "checkpoint.json.gz", "chain_complete.json"}) assert(fs::is_regular_file(directory / name));
    }
    assert(read_gzip(one_options.outdir / "samples.jsonl.gz") == read_gzip(two_options.outdir / "samples.jsonl.gz"));
    // Checkpoint is a resumability/audit artifact, not the cross-thread
    // byte-level deterministic contract: runtime parallelization metadata may
    // legitimately differ even when retained posterior states are identical.
    for (const auto& directory : {one_options.outdir, two_options.outdir}) {
        const std::string checkpoint = read_gzip(directory / "checkpoint.json.gz");
        assert(checkpoint.find("\"checkpoint_version\":1") != std::string::npos);
        assert(checkpoint.find("\"input_sha256\":") != std::string::npos);
        assert(checkpoint.find("\"next_iteration\":12") != std::string::npos);
        assert(checkpoint.find("\"parents\":") != std::string::npos);
        assert(checkpoint.find("\"eta\":") != std::string::npos);
        assert(checkpoint.find("\"z\":") != std::string::npos);
        assert(checkpoint.find("\"counters\":") != std::string::npos);
        assert(checkpoint.find("\"retained_samples\":") != std::string::npos);
        assert(checkpoint.find("\"assignment_counts\":") != std::string::npos);
        assert(checkpoint.find("\"rng_state\":") != std::string::npos);
    }
    std::ifstream diagnostics(one_options.outdir / "diagnostics.json");
    std::stringstream diagnostic_text;
    diagnostic_text << diagnostics.rdbuf();
    assert(diagnostic_text.str().find("finite_K_tssb_inspired") != std::string::npos);
    assert(diagnostic_text.str().find("single_chain_phylowgs_inspired_tssb_mcmc") != std::string::npos);
    assert(diagnostic_text.str().find("all_SNV_categorical_Gibbs_sweep") != std::string::npos);

    config.resume = true;
    bool resume_rejected = false;
    try {
        algorithm->run(tti::load_canonical_table(input, 0.99, {}), config, one_options, 0);
    } catch (const std::runtime_error& error) {
        resume_rejected = std::string(error.what()).find("fail-closed") != std::string::npos;
    }
    assert(resume_rejected);
    fs::remove_all(root, ignored);
    return 0;
}
