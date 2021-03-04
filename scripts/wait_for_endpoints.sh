#!/bin/bash
set -e
set -o pipefail
# GRAFANA_HOST="http://localhost:3000/api/health"
# PROMETHEUS_HOST="http://localhost:9090/-/ready"
# NODEEXPORTER_HOST="http://localhost:9100/metrics"
# CONTAINEREXPORTER_HOST="http://localhost:9104/metrics"

wait_for_endpoints(){
    declare endpoints=($@)
    for endpoint in "${endpoints[@]}"; do
        counter=1
        while [[ $(curl -s -o /dev/null -w ''%{http_code}'' "$endpoint") != "200" ]]; do 
            counter=$((counter+1))
            echo ">> [LOG] Waiting for - ${endpoint}"
            if [[ $counter -gt 60 ]]; then
                echo ">> [ERROR] Not healthy - ${endpoint}"
                exit 1
            fi
            sleep 3
        done
        echo ">> [LOG] Healthy endpoint - ${endpoint}"
    done    
}

wait_for_endpoints $@

# wait_for_endpoints "$GRAFANA_HOST" "$PROMETHEUS_HOST" "$NODEEXPORTER_HOST" "$CONTAINEREXPORTER_HOST"
