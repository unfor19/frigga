#!/bin/bash
set -e
set -o pipefail

get_num_series(){
    source scripts/get_total_dataseries_num.sh http://localhost:9090
}

# Check if debug pod is running, fail otherwise
POD_DEBUG=$(kubectl get pods | grep debug.*Running | cut -f 1 -d " ")

# Make Prometheus HTTP API available from host (background job "&")
kubectl port-forward service/prometheus 9090:9090 &

# Check num of dataseries before
num_series_before=$(get_num_series)

# Apply changes
kubectl exec $POD_DEBUG -- bash /root/frigga/.frigga/kubernetes/apply_changes.sh
echo ">> [LOG] Sleeping for 10 seconds ..."
sleep 10

# Comparing results
num_series_after=$(get_num_series)
echo ">> [LOG] Before: ${num_series_before}"
echo ">> [LOG] After: ${num_series_after}"
if [[ "$num_series_after" -lt "$num_series_before" ]]; then
    echo ">> [LOG] Passed testing! After is smaller than before"
    exit 0
else
    error_msg "Failed testing! Before is smaller or equal to after"
fi