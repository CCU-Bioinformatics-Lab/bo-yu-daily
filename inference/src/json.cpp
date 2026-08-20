#include "json.hpp"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iomanip>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <thread>

#include <zlib.h>

namespace tumor_tree_inference {
namespace {

std::filesystem::path temporary_path(const std::filesystem::path& path) {
    const auto now = std::chrono::steady_clock::now().time_since_epoch().count();
    const auto thread_id = std::hash<std::thread::id>{}(std::this_thread::get_id());
    return path.parent_path() /
           ("." + path.filename().string() + ".tmp-" + std::to_string(now) +
            "-" + std::to_string(thread_id));
}

void replace_atomically(const std::filesystem::path& temporary,
                        const std::filesystem::path& destination) {
    std::error_code error;
    std::filesystem::rename(temporary, destination, error);
    if (error) {
        std::filesystem::remove(temporary);
        throw std::runtime_error("cannot atomically publish " + destination.string() + ": " + error.message());
    }
}

template <typename T>
std::string array_json(const std::vector<T>& values, const std::function<std::string(const T&)>& encode) {
    std::string result = "[";
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i != 0) result += ",";
        result += encode(values[i]);
    }
    result += "]";
    return result;
}

}  // namespace

std::string json_escape(const std::string& value) {
    std::ostringstream escaped;
    escaped << std::hex << std::setfill('0');
    for (unsigned char character : value) {
        switch (character) {
            case '"': escaped << "\\\""; break;
            case '\\': escaped << "\\\\"; break;
            case '\b': escaped << "\\b"; break;
            case '\f': escaped << "\\f"; break;
            case '\n': escaped << "\\n"; break;
            case '\r': escaped << "\\r"; break;
            case '\t': escaped << "\\t"; break;
            default:
                if (character < 0x20U) {
                    escaped << "\\u" << std::setw(4) << static_cast<unsigned>(character);
                } else {
                    escaped << static_cast<char>(character);
                }
        }
    }
    return escaped.str();
}

std::string json_number(double value) {
    if (!std::isfinite(value)) throw std::runtime_error("refusing to write non-finite JSON number");
    std::ostringstream result;
    result << std::setprecision(17) << value;
    return result.str();
}

std::string json_u64(std::uint64_t value) { return std::to_string(value); }

std::string json_string(const std::string& value) { return "\"" + json_escape(value) + "\""; }

std::string json_bool(bool value) { return value ? "true" : "false"; }

void atomic_write_text(const std::filesystem::path& path, const std::string& text) {
    std::filesystem::create_directories(path.parent_path());
    const auto temporary = temporary_path(path);
    try {
        std::ofstream output(temporary, std::ios::binary | std::ios::trunc);
        if (!output) throw std::runtime_error("cannot create temporary artifact: " + temporary.string());
        output.write(text.data(), static_cast<std::streamsize>(text.size()));
        output.flush();
        if (!output) throw std::runtime_error("cannot write artifact: " + path.string());
        output.close();
        if (!output) throw std::runtime_error("cannot close artifact: " + path.string());
        replace_atomically(temporary, path);
    } catch (...) {
        std::error_code ignored;
        std::filesystem::remove(temporary, ignored);
        throw;
    }
}

void atomic_write_gzip(const std::filesystem::path& path, const std::string& text) {
    std::filesystem::create_directories(path.parent_path());
    const auto temporary = temporary_path(path);
    gzFile output = gzopen(temporary.string().c_str(), "wb6");
    if (output == nullptr) throw std::runtime_error("cannot create gzip artifact: " + temporary.string());
    try {
        std::size_t offset = 0;
        while (offset < text.size()) {
            const std::size_t remaining = text.size() - offset;
            const unsigned chunk = static_cast<unsigned>(std::min<std::size_t>(remaining, 1U << 20U));
            if (gzwrite(output, text.data() + offset, static_cast<int>(chunk)) != static_cast<int>(chunk)) {
                gzclose(output);
                throw std::runtime_error("cannot write gzip artifact: " + path.string());
            }
            offset += chunk;
        }
        if (gzclose(output) != Z_OK) throw std::runtime_error("cannot close gzip artifact: " + path.string());
        replace_atomically(temporary, path);
    } catch (...) {
        std::error_code ignored;
        std::filesystem::remove(temporary, ignored);
        throw;
    }
}

std::string json_string_array(const std::vector<std::string>& values) {
    return array_json<std::string>(values, [](const std::string& value) { return json_string(value); });
}

std::string json_int_array(const std::vector<int>& values) {
    return array_json<int>(values, [](int value) { return std::to_string(value); });
}

std::string json_u64_array(const std::vector<std::uint64_t>& values) {
    return array_json<std::uint64_t>(values, [](std::uint64_t value) { return json_u64(value); });
}

std::string json_double_array(const std::vector<double>& values) {
    return array_json<double>(values, [](double value) { return json_number(value); });
}

std::string json_parent_array(const std::vector<int>& values) { return json_int_array(values); }

std::string sample_json(const SampleRecord& sample) {
    return "{\"iteration\":" + json_u64(sample.iteration) +
           ",\"log_posterior\":" + json_number(sample.log_posterior) +
           ",\"parents\":" + json_parent_array(sample.parents) +
           ",\"eta\":" + json_double_array(sample.eta) +
           ",\"phi\":" + json_double_array(sample.phi) +
           ",\"occupancy\":" + json_u64_array(sample.occupancy) + "}";
}

std::string sample_array_json(const std::vector<SampleRecord>& samples) {
    std::string result = "[";
    for (std::size_t i = 0; i < samples.size(); ++i) {
        if (i != 0) result += ",";
        result += sample_json(samples[i]);
    }
    result += "]";
    return result;
}

}  // namespace tumor_tree_inference
