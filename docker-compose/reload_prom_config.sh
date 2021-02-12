#!/bin/bash
set -e
set -o pipefail

filter="frigga_prometheus"
prom_container_name=$(docker ps --filter name="${filter}" --format "{{.Names}}" || true)
if [[ -z "${prom_container_name}" ]]; then
    echo "The container ${filter} is not running, execute first docker-compose/deploy_stack.sh"
    exit 1
fi

echo ">> [LOG] Reloading prometheus.yml configuration file"
docker exec "${prom_container_name}" kill -HUP 1 || true
sleep 2
reload_result=$(docker logs --tail 4 $prom_container_name 2>&1 || true)
reload_success=$(echo "$reload_result" | grep ".*Completed loading of configuration file.*" || true)
if [[ -n ${reload_success} ]]; then
    echo ""
    echo ">> [LOG] Successfully reloaded prometheus.yml"
    echo ""
else
    echo ">> [ERROR] Failed to reload prometheus.yml"
    echo "${reload_result}"
    exit 1
fi
