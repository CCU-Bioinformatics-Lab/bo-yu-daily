#pragma once

#include <filesystem>
#include <string>

namespace tumor_tree_inference {

std::string sha256_file(const std::filesystem::path& path);

}  // namespace tumor_tree_inference
