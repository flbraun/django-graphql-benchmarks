#!/usr/bin/env bash

set -Eeuo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

echo "preheating $API_HOST"
for ((i=1;i<=100;i++)); do
  curl -s $API_HOST > /dev/null
done

for bench in "$@"; do
  f="$(basename -- $bench .js)"
  set -x
  k6 run --out json="$script_dir/results/$f.json" "$script_dir/$f.js"
  set +x
done
