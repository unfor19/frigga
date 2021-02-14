#!/bin/bash
set -e
set -o pipefail

generate_apikey(){
    echo ">> Grafana - Generating API Key - for Viewer"
    apikey=$(curl -s -L -X POST \
        --user admin:admin \
        -H "Content-Type: application/json" \
        --data '{"name":"local","role":"Viewer","secondsToLive":86400}' \
        http://localhost:3000/api/auth/keys | jq -r .key)
    echo "$apikey"
    echo "$apikey" > .apikey && echo ">> API Key was saved in .apikey file"
    echo ">> Export the key as environment variable for later use"
    echo "export GRAFANA_API_KEY=${apikey}"
}

grafana_update_admin_password(){
    echo ">> Grafana - Changing admin password to 'admin'"
    response=$(curl -s -X PUT -H "Content-Type: application/json" -d '{
    "oldPassword": "admin",
    "newPassword": "admin",
    "confirmNew": "admin"
    }' http://admin:admin@localhost:3000/api/user/password)
    msg=$(echo "$response" | jq -r .message)
    echo ">> Grafana - ${msg}"
}

network=$(docker network ls | grep frigga_net || true)
[[ -n "$network" ]] && echo "ERROR: wait for network to be deleted, docker network ls, or restart docker daemon" && exit
cp docker-compose/prometheus-original.yml docker-compose/prometheus.yml

_DOCKER_TAG="${DOCKER_TAG:-"unfor19/frigga:latest"}"
echo "DOCKER_TAG=${_DOCKER_TAG}" > .env.ci

docker-compose --project-name frigga --env-file .env.ci \
    --file docker-compose/docker-compose.yml \
    up --detach

echo ">> Waiting for Grafana to be ready ..."
counter=0
until [ $counter -gt 6 ]; do
    response=$(curl -s http://admin:admin@localhost:3000/api/health | jq -r .database || true)
    if [[  $response == "ok" ]]; then
        echo ">> Grafana is ready!"
        grafana_update_admin_password
        generate_apikey
        exit 0
    else
        sleep 10
        counter=$((counter+1))
    fi
done
