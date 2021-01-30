#!/bin/bash
set -e
set -o pipefail
POD_DEBUG=$(kubectl get pods | grep debug.*Running | cut -f 1 -d " ")
kubectl exec $POD_DEBUG -- bash /root/frigga/.frigga/kubernetes/apply_changes.sh
