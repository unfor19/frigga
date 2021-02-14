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

export \
    FRIGGA_URL="http://localhost:8083" \
    PROM_URL="http://prometheus:9090" \
    PROM_YAML_PATH="/etc/prometheus/prometheus.yml" \
    GRAFANA_URL="http://grafana:3000" \
    SLEEP_SECONDS=10

frigga client-run
