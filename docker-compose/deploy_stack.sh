#!/bin/bash
set -e
set -o pipefail

get_random_string(){
    local MD5_BIN="md5sum" # Linux and Windows
    local COMMAND_OUTPUT=$(command -v md5sum)
    local random_string
    if [ ${#COMMAND_OUTPUT} -lt 1 ]; then
        MD5_BIN="md5" # macOS
    fi

    random_string=$(date | ${MD5_BIN} | tr -dc '[:alnum:]\n\r' | tr '[:upper:]' '[:lower:]')

    echo "${random_string:0:7}"
}


generate_apikey(){
    local random_string=$(get_random_string)
    echo ">> Grafana - Generating API Key - for Viewer"
    apikey=$(curl -s -L -X POST \
        --user admin:admin \
        -H "Content-Type: application/json" \
        --data '{"name":"'"${random_string}"'","role":"Viewer","secondsToLive":86400}' \
        http://localhost:3000/api/auth/keys | jq -r .key)
    echo "$apikey"
    echo "$apikey" > .apikey && echo ">> API Key was saved in .apikey file"
    echo ">> Export the key as environment variable for later use"
    echo "export GRAFANA_API_KEY=${apikey}"
}


grafana_update_admin_password(){
    local msg
    echo ">> Grafana - Changing admin password to 'admin'"
    response=$(curl -s -X PUT -H "Content-Type: application/json" -d '{
    "oldPassword": "admin",
    "newPassword": "admin",
    "confirmNew": "admin"
    }' http://admin:admin@localhost:3000/api/user/password)
    msg=$(echo "$response" | jq -r .message)
    echo ">> Grafana - ${msg}"
}


pre_deploy(){
    local _DOCKER_TAG
    cp docker-compose/prometheus-original.yml docker-compose/prometheus.yml

    # fixed permissions denied when frigga tries to change prometheus.yml
    chmod 777 docker-compose/prometheus.yml
    _DOCKER_TAG="${DOCKER_TAG:-"unfor19/frigga:latest"}"
    echo "DOCKER_TAG=${_DOCKER_TAG}" > .env.ci    
}


deploy(){
    docker-compose --project-name frigga --env-file .env.ci \
        --file docker-compose/docker-compose.yml \
        up --detach

    local GRAFANA_HOST="http://localhost:3000/api/health"
    local PROMETHEUS_HOST="http://localhost:9090/-/ready"
    local NODEEXPORTER_HOST="http://localhost:9100/metrics"
    local CONTAINEREXPORTER_HOST="http://localhost:9104/metrics"

    source scripts/wait_for_endpoints.sh "$GRAFANA_HOST" "$PROMETHEUS_HOST" "$NODEEXPORTER_HOST" "$CONTAINEREXPORTER_HOST"
}


post_deploy(){
    grafana_update_admin_password
    generate_apikey
}


# main
pre_deploy
deploy
post_deploy

