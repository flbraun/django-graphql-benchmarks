#!/usr/bin/env bash

set -Eeuo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

bench_files="$script_dir/*.js"

for bench in $bench_files; do
  f="$(basename -- $bench .js)"
  set -x
  k6 run --out json="$script_dir/results/$f.json" "$script_dir/$f.js"
  set +x
done

poetry run python "$script_dir/format-results.py"
