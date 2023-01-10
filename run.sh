#!/usr/bin/env bash

set -e

DOCKER_NETWORK=benchtmp

preheat() {
  API_HOST=$1

  docker run \
    --rm \
    --network $DOCKER_NETWORK \
    curlimages/curl -s "$API_HOST/json-api/top-250?foo=[001-100]" > /dev/null
  docker run \
    --rm \
    --network $DOCKER_NETWORK \
    curlimages/curl -s "$API_HOST/drf-api/movies/?foo=[001-100]" > /dev/null
  docker run \
    --rm \
    --network $DOCKER_NETWORK \
    curlimages/curl -s -X POST "$API_HOST/strawberry-graphql/?foo=[001-100]" -H "Content-Type: application/json" -d '{"query": "{\n __schema {\n types {\n name\n }\n }\n}"}' > /dev/null
  docker run \
    --rm \
    --network $DOCKER_NETWORK \
    curlimages/curl -s -X POST "$API_HOST/graphene-graphql/?foo=[001-100]" -H "Content-Type: application/json" -d '{"query": "{\n __schema {\n types {\n name\n }\n }\n}"}' > /dev/null
}

run_bench() {
  API_HOST=$1
  BENCH_SCRIPT=$2
  NAME=$3

  docker run \
    --user $UID \
    --rm \
    -i \
    --network $DOCKER_NETWORK \
    -e API_HOST="$API_HOST" \
    -v $(pwd)/results:/results \
    loadimpact/k6 run --out json=/results/"$NAME".json - < "$BENCH_SCRIPT"
}

rm -f results/*
docker network create $DOCKER_NETWORK

for pyversion in "$@"
do
  git checkout main
  docker build -t benchapp --build-arg BASE_IMAGE=python:${pyversion}-slim-bullseye .

  git checkout main_graphenev2_only
  docker build -t benchapp-only-graphenev2 --build-arg BASE_IMAGE=python:${pyversion}-slim-bullseye .
  git checkout main

  docker run --detach --network $DOCKER_NETWORK --name benchapp benchapp
  docker run --detach --network $DOCKER_NETWORK --name benchapp-only-graphenev2 -e ONLY_GRAPHENE_V2=true benchapp-only-graphenev2
  sleep 5; # wait for gunicorn works to be available

  preheat "http://benchapp:8000"
  run_bench "http://benchapp:8000" k6_scripts/json.js "json@py${pyversion}"
  run_bench "http://benchapp:8000" k6_scripts/drf.js "drf@py${pyversion}"
  run_bench "http://benchapp:8000" k6_scripts/strawberry.js "strawberry@py${pyversion}"
  run_bench "http://benchapp:8000" k6_scripts/graphene.js "graphene@py${pyversion}"
  preheat "http://benchapp-only-graphenev2:8000"
  run_bench "http://benchapp-only-graphenev2:8000" k6_scripts/graphene.js "graphenev2@py${pyversion}"

  docker rm --force $(docker container ls -q --filter "name=benchapp*")
done

docker network rm $DOCKER_NETWORK

poetry run python format-results.py
DASHBOARD_PORT=8099 poetry run python dashboard.py
