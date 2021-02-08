#!/bin/bash
set -e
set -o pipefail

GRAFANA_API_KEY="$(cat .apikey || true)"

error_msg(){
    msg=$1
    echo ">> [ERROR] ${msg}"
    exit 1
}

get_num_series(){
    source scripts/get_total_dataseries_num.sh "http://localhost:9090"
}

[[ -z ${GRAFANA_API_KEY} ]] && error_msg ".apikey file is empty"

num_series_before=$(get_num_series)

# Generate .metrics.json
frigga grafana-list \
    -gurl http://localhost:3000 \
    -gkey "${GRAFANA_API_KEY}"

# Apply rules in prometheus.yml according to .metrics.json    
frigga prometheus-apply \
    --prom-yaml-path docker-compose/prometheus.yml \
    --metrics-json-path .metrics.json

# Reload prometheus configuration
source docker-compose/reload_prom_config.sh show

echo ">> [LOG] Sleeping for 10 seconds ..."
sleep 10

# Comparing results
num_series_after=$(get_num_series)
echo ">> [LOG] Before: ${num_series_before}"
echo ">> [LOG] After: ${num_series_after}"
if [[ "$num_series_after" -lt "$num_series_before" ]]; then
    echo ">> [LOG] Passed testing! After is smaller than before"
    exit 0
elif [[ "$num_series_after" -eq "$num_series_before" ]]; then
    echo ">> [WARNING] Before and after are equal, nothing has changed"
    exit 0    
else
    error_msg "Failed testing! Before is smaller than after"
fi