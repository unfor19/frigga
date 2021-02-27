#!/bin/bash
set -e
set -o pipefail
kubectl get pods
POD_PROMETHEUS=$(kubectl get pods --selector=app=prometheus | grep 1/1.*Running | cut -f 1 -d " " 2>/dev/null || true)
[[ -z ${POD_PROMETHEUS} ]] && echo "The container ${POD_PROMETHEUS} is not running, execute first docker-compose/deploy_stack.sh"
