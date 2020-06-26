#!/bin/bash
show_logs=$1
filter=frigga_prometheus
prom_container_name=$(docker ps --filter name=${filter} --format "{{.Names}}")
[[ -z ${prom_container_name} ]] && echo "The container ${filter} is not running, execute first docker-swarm/deploy_stack.sh"

echo ">> Reloading prometheus.yml configuration file"
reloaded=$(docker exec ${prom_container_name} kill -HUP 1)
if [[ -z ${reloaded} ]]; then
    echo ">> Reloaded"
    [[ ! -z ${show_logs} ]] && docker logs ${prom_container_name}
else
    echo ${reloaded}
fi

