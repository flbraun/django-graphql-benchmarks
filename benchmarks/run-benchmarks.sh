#!/usr/bin/env bash

set -Eeuo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

pyversion=$1
shift
frameworks=$@

echo "preheating endpoints at $API_HOST"
for ((i=1;i<=100;i++)); do
  curl -s $API_HOST/json-api/top-250 > /dev/null
  curl -s $API_HOST/drf-api/movies/ > /dev/null
  curl -s -X POST $API_HOST/strawberry-graphql/ -H "Content-Type: application/json" -d '{"query": "{\n __schema {\n types {\n name\n }\n }\n}"}' > /dev/null
  curl -s -X POST $API_HOST/graphene-graphql/ -H "Content-Type: application/json" -d '{"query": "{\n __schema {\n types {\n name\n }\n }\n}"}' > /dev/null
done

for bench in $frameworks; do
  f="$(basename -- $bench .js)"
  set -x
  k6 run --out json="$script_dir/results/$f@py$pyversion.json" "$script_dir/$f.js"
  set +x
done
