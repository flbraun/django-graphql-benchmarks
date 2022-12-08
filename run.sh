#!/usr/bin/env bash

set -e

git checkout main
docker build -t benchapp .

git checkout main_graphenev2_only
docker build -t benchapp-only-graphenev2 .
git checkout main

docker run --detach -p "8097:8000" --name benchapp benchapp
docker run --detach -p "8098:8000" --name benchapp-only-graphenev2 -e ONLY_GRAPHENE_V2=true benchapp-only-graphenev2
sleep 5; # wait for gunicorn works to be available

rm -f benchmarks/results/*
API_HOST="http://localhost:8097" benchmarks/run-benchmarks.sh drf json strawberry graphene
API_HOST="http://localhost:8098" benchmarks/run-benchmarks.sh graphenev2
docker rm --force $(docker container ls -q --filter "name=benchapp*")

poetry run python benchmarks/format-results.py
DASHBOARD_PORT=8099 poetry run python benchmarks/dashboard.py
