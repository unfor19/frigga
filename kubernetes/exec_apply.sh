#!/bin/bash
set -e
set -o pipefail

echo ">> [LOG] Check if debug pod is running, fail otherwise"
POD_DEBUG=$(kubectl get pods | grep debug.*Running | cut -f 1 -d " ")

# Apply changes
echo ">> [LOG] Executing kubernetes/apply_changes.sh in debug pod"
kubectl exec $POD_DEBUG -- bash /root/frigga/.frigga/kubernetes/apply_changes.sh
