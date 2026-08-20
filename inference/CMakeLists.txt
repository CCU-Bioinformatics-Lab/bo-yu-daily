cmake_minimum_required(VERSION 3.14)
project(tumor_tree_inference LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(ZLIB REQUIRED)
find_package(Threads REQUIRED)

add_library(tumor_tree_inference_core
    src/algorithm.cpp
    src/hash.cpp
    src/json.cpp
    src/model.cpp
    src/registry.cpp
)
target_include_directories(tumor_tree_inference_core
    PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include
)
target_link_libraries(tumor_tree_inference_core PUBLIC ZLIB::ZLIB Threads::Threads)
target_compile_options(tumor_tree_inference_core PRIVATE
    $<$<OR:$<CXX_COMPILER_ID:GNU>,$<CXX_COMPILER_ID:Clang>>:-Wall -Wextra -Wpedantic>
)

add_executable(tumor_tree_inference src/main.cpp)
target_link_libraries(tumor_tree_inference PRIVATE tumor_tree_inference_core)
target_compile_options(tumor_tree_inference PRIVATE
    $<$<OR:$<CXX_COMPILER_ID:GNU>,$<CXX_COMPILER_ID:Clang>>:-Wall -Wextra -Wpedantic>
)

include(CTest)
if(BUILD_TESTING)
    add_executable(tumor_tree_inference_smoke tests/smoke.cpp)
    target_link_libraries(tumor_tree_inference_smoke PRIVATE tumor_tree_inference_core)
    add_test(NAME tumor_tree_inference_smoke COMMAND tumor_tree_inference_smoke)
endif()
