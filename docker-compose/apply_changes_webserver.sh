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
FRIGGA_URL=http://localhost:8083
PROM_URL=http://prometheus:9090
PROM_YAML_PATH=/etc/prometheus/prometheus.yml
GRAFANA_URL=http://grafana:3000
SLEEP_SECONDS=10
" > .tmp.env.webserver.ci
sed '/^[[:space:]]*$/d' .tmp.env.webserver.ci > .env.webserver.ci
cat .env.webserver.ci
_DOCKER_TAG="${DOCKER_TAG:-"unfor19/frigga:latest"}"

docker run --rm -t --network host -e GRAFANA_API_KEY --env-file .env.webserver.ci "$_DOCKER_TAG" client-run
