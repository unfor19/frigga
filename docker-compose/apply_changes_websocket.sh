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

echo  "
FRIGGA_URL=ws://localhost:8084
PROM_URL=http://prometheus:9090
PROM_YAML_PATH=prometheus.yml
GRAFANA_URL=http://grafana:3000
SLEEP_SECONDS=10
" > .tmp.env.websocket.ci
sed '/^[[:space:]]*$/d' .tmp.env.websocket.ci > .env.websocket.ci
cat .env.websocket.ci
_DOCKER_TAG="${DOCKER_TAG:-"unfor19/frigga:latest"}"

docker run --rm -t --network host -e GRAFANA_API_KEY --env-file .env.websocket.ci "$_DOCKER_TAG" client-websocket-run
