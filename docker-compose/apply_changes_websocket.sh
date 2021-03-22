#!/bin/bash
set -e
set -o pipefail

export GRAFANA_API_KEY="$(cat .apikey || true)"

error_msg(){
    msg="$1"
    echo ">> [ERROR] ${msg}"
    exit 1
}


[[ -z "${GRAFANA_API_KEY}" ]] && error_msg ".apikey file is empty"

_DOCKER_TAG="${DOCKER_TAG:-"unfor19/frigga:latest"}"
docker run --rm -t "$_DOCKER_TAG" version

docker run --rm -t --network host "$_DOCKER_TAG" \
    client-start --grafana-url http://grafana:3000 \
        --prom-url http://prometheus:9090 \
        --frigga-url ws://localhost:8085 \
        --grafana-api-key "${GRAFANA_API_KEY}" \
        --prom-yaml-path "prometheus.yml" \
        --raw
