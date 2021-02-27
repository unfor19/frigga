#!/bin/bash
set -e
set -o pipefail

PROMETHEUS_HOST="http://localhost:9090"
GRAFANA_API_KEY="$(cat .apikey || true)"

error_msg(){
    msg="$1"
    echo ">> [ERROR] ${msg}"
    exit 1
}


[[ -z "${GRAFANA_API_KEY}" ]] && error_msg ".apikey file is empty"

frigga version

num_series_before=$(frigga pg -u "$PROMETHEUS_HOST" -r)

# Generate .metrics.json
frigga grafana-list \
    -gurl http://localhost:3000 \
    -gkey "${GRAFANA_API_KEY}"

# Apply rules in prometheus.yml according to .metrics.json    
frigga prometheus-apply \
    --prom-yaml-path docker-compose/prometheus.yml \
    --metrics-json-path .metrics.json

# Reload prometheus configuration
frigga prometheus-reload \
    --prom-url "$PROMETHEUS_HOST" \
    --raw

echo ">> [LOG] Sleeping for 10 seconds ..."
sleep 10

# Comparing results
num_series_after=$(frigga pg -u "$PROMETHEUS_HOST" -r)
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