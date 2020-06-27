#!/bin/bash
GRAFANA_API_KEY=$(cat .apikey)

error_msg(){
    msg=$1
    echo ">> [ERROR] ${msg}"
    exit
}

[[ -z ${GRAFANA_API_KEY} ]] && error_msg ".apikey file is empty"

# Generate .metrics.json
frigga grafana-list \
    -gurl http://localhost:3000 \
    -gkey "${GRAFANA_API_KEY}"

# Apply rules in prometheus.yml according to .metrics.json    
frigga prometheus-apply \
    --prom-yaml-path docker-compose/prometheus.yml \
    --metrics-json-path .metrics.json

# Reload prometheus configuration
reload_result=$(source docker-compose/reload_prom_config.sh show)
reload_succes=$(echo "${reload_result}" | tail -n 5 | grep "Completed loading of configuration file")
if [[ -z ${reload_succes} ]]; then
    echo "Successfully reloaded prometheus.yml"
    exit 0
else
    echo "Failed to reload prometheus.yml"
    echo "${reload_result}"
    exit 1
fi