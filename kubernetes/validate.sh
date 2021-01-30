#!/bin/bash
set -e
set -o pipefail
kubectl get pods
POD_PROMETHEUS=$(kubectl get pods --selector=app=prometheus | grep 1/1.*Running | cut -f 1 -d " " 2>/dev/null || true)
[[ -z ${POD_PROMETHEUS} ]] && echo "The container ${POD_PROMETHEUS} is not running, execute first docker-compose/deploy_stack.sh"

reload_result=$(kubectl logs ${POD_PROMETHEUS})
reload_success=$(echo "${reload_result}" | tail -n 3 | grep ".*Completed loading of configuration file.*")
if [[ -z ${reload_succes} ]]; then
    echo ""
    echo ">> [LOG] Successfully reloaded prometheus.yml"
    echo ""
else
    echo ">> [ERROR] Failed to reload prometheus.yml"
    echo "${reload_result}"
    exit 1
fi
