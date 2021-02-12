#!/bin/bash
set -e
set -o pipefail

error_msg(){
    msg=$1
    echo ">> [ERROR] ${msg}"
    exit 1
}


PROMETHEUS_HOST="http://prometheus.default.svc.cluster.local:9090"

FRIGGA_FOLDER="/root/frigga/.frigga"
cd "$FRIGGA_FOLDER"

GRAFANA_HOST="http://grafana.default.svc.cluster.local:3000"
RANDOM_KEY_NAME=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 10 ; echo '')
GRAFANA_API_KEY=$(curl -s -X POST -sL --user admin:admin -H "Content-Type: application/json" --data '{"name":"'"${RANDOM_KEY_NAME}"'","role":"Viewer","secondsToLive":86400}' ${GRAFANA_HOST}/api/auth/keys | jq -r .key)

# Install frigga
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install .

echo ">> [LOG] Check num of dataseries before"
num_series_before=$(frigga pg -r -u "$PROMETHEUS_HOST")
echo ">> [LOG] Before: ${num_series_before}"

# Generate .metrics.json 
frigga gl -gurl "$GRAFANA_HOST" -gkey "$GRAFANA_API_KEY"

# Add filters to prometheus.yml
frigga pa -ppath kubernetes/prometheus-original.yml -mjpath .metrics.json

# Reload prometheus
frigga pr -u "$PROMETHEUS_HOST"

echo ">> [LOG] Sleeping for 10 seconds ..."
sleep 10

# Comparing results
num_series_after=$(frigga pg -r -u "$PROMETHEUS_HOST")
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
