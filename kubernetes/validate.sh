#!/bin/bash
POD_PROMETHEUS=$(kubectl get pods | grep debug.*Running | cut -f 1 -d " ")
[[ -z ${POD_PROMETHEUS} ]] && echo "The container ${POD_PROMETHEUS} is not running, execute first docker-compose/deploy_stack.sh"

reload_result=$(kubectl logs ${POD_PROMETHEUS})
reload_succes=$(echo "${reload_result}" | tail -n 5 | grep "Completed loading of configuration file")
if [[ -z ${reload_succes} ]]; then
    echo ""
    echo ">> [LOG] Successfully reloaded prometheus.yml"
    echo ""
else
    echo ">> [ERROR] Failed to reload prometheus.yml"
    echo "${reload_result}"
    exit 1
fi
