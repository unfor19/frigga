#!/bin/bash
GRAFANA_API_KEY=$(cat .apikey)

error_msg(){
    msg=$1
    echo ">> [ERROR] ${msg}"
    exit 1
}

# get_num_series(){
#     result=$(curl -s http://localhost:9090/api/v1/status/tsdb \
#         | jq -c '.data.seriesCountByLabelValuePair | map(select(.name | contains("job="))) | map(.value) | add')
#     echo $result    
# }

[[ -z ${GRAFANA_API_KEY} ]] && error_msg ".apikey file is empty"

# num_series_before=$(get_num_series)

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
reload_succes=$(echo "${reload_result}" | tail -n 3 | grep "Completed loading of configuration file")
if [[ -z ${reload_succes} ]]; then
    echo ""
    echo ">> [LOG] Successfully reloaded prometheus.yml"
    echo ""
else
    echo ">> [ERROR] Failed to reload prometheus.yml"
    echo "${reload_result}"
    exit 1
fi

# sleep 10

# # Comparing results
# num_series_after=$(get_num_series)
# echo ">> [LOG] Before: ${num_series_before}"
# echo ">> [LOG] After: ${num_series_after}"
# if [[ "$num_series_after" -lt "$num_series_before" ]]; then
#     echo ">> [LOG] Passed testing! After is little than before"
#     exit 0
# else
#     error_msg "Failed testing! Before is little than after"
# fi