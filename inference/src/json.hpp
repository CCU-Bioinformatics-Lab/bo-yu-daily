#pragma once

#include "tumor_tree_inference/algorithm.hpp"

#include <cstdint>
#include <filesystem>
#include <map>
#include <string>
#include <vector>

namespace tumor_tree_inference {

std::string json_escape(const std::string& value);
std::string json_number(double value);
std::string json_u64(std::uint64_t value);
std::string json_string(const std::string& value);
std::string json_bool(bool value);

void atomic_write_text(const std::filesystem::path& path, const std::string& text);
void atomic_write_gzip(const std::filesystem::path& path, const std::string& text);

std::string json_string_array(const std::vector<std::string>& values);
std::string json_int_array(const std::vector<int>& values);
std::string json_u64_array(const std::vector<std::uint64_t>& values);
std::string json_double_array(const std::vector<double>& values);
std::string json_parent_array(const std::vector<int>& values);

struct SampleRecord {
    std::uint64_t iteration = 0;
    double log_posterior = 0.0;
    std::vector<int> parents;
    std::vector<double> eta;
    std::vector<double> phi;
    std::vector<std::uint64_t> occupancy;
};

std::string sample_json(const SampleRecord& sample);
std::string sample_array_json(const std::vector<SampleRecord>& samples);

}  // namespace tumor_tree_inference
