#!/bin/bash
set -e
set -o pipefail
GRAFANA_HOST="http://grafana.default.svc.cluster.local:3000"
PROMETHEUS_HOST="http://prometheus.default.svc.cluster.local:9090"
NODEEXPORTER_HOST="http://node-exporter.default.svc.cluster.local:9100"
CONTAINEREXPORTER_HOST="http://container-exporter.default.svc.cluster.local:9104"

HEALTH_ENDPOINTS=("${PROMETHEUS_HOST}/-/ready" "${GRAFANA_HOST}/api/health" "${NODEEXPORTER_HOST}/metrics" "${CONTAINEREXPORTER_HOST}/metrics")
for endpoint in "${HEALTH_ENDPOINTS[@]}"; do
    counter=1
    while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' ${endpoint})" != "200" ]]; do
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
