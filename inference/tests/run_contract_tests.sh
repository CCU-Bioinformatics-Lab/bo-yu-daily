#!/usr/bin/env bash
set -u

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(CDPATH= cd -- "$script_dir/../.." && pwd)

if [ "$#" -gt 1 ]; then
    echo "usage: $0 [path/to/inference_binary]" >&2
    exit 2
fi

if [ "$#" -eq 1 ]; then
    binary=$1
else
    binary=${INFERENCE_BINARY:-}
fi

if [ -z "$binary" ]; then
    for candidate in \
        "$repo_dir/inference/build/tumor_tree_inference" \
        "$repo_dir/inference/build/inference" \
        "$repo_dir/inference/build/bin/tumor_tree_inference"; do
        if [ -x "$candidate" ]; then
            binary=$candidate
            break
        fi
    done
fi

if [ -z "$binary" ]; then
    echo "inference binary not found; build inference/ first or pass its path" >&2
    exit 2
fi

exec python3 "$script_dir/contract_test.py" --binary "$binary"
