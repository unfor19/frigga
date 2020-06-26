#!/bin/bash

generate_apikey(){
    echo ">> Generating Grafana API Key - for Viewer"
    apikey=$(curl -s -L -X POST \
        --user admin:admin \
        -H "Content-Type: application/json" \
        --data '{"name":"local","role":"Viewer","secondsToLive":86400}' \
        http://localhost:3000/api/auth/keys | jq -r .key)
    echo $apikey
}


network=$(docker network ls | grep frigga_net)
[[ ! -z $network ]] && echo "ERROR: wait for network to be deleted, docker network ls, or restart docker daemon" && exit
HOSTNAME=$(hostname) docker stack deploy -c docker-swarm/docker-stack.yml frigga

echo ">> Waiting for Grafana to be ready ..."
counter=0
until [ $counter -gt 6 ]; do
    response=$(curl -s http://admin:admin@localhost:3000/api/health | jq -r .database)
    if [[  $response == "ok" ]]; then
        echo ">> Grafana is ready! Generating API Key"
        generate_apikey
        exit 0
    else
        sleep 10
        counter=$((counter+1))
    fi
done
