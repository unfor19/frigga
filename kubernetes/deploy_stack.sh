#!/bin/bash
set -e
set -o pipefail
source kubernetes/minikube_rsync.sh

kubectl apply -f kubernetes/debug.yml

while [[ -z "$(kubectl get pods | grep debug.*Running)" ]]; do
    echo ">> [LOG] Waiting for the debug pod to be ready"
    sleep 5
done
echo ">> [LOG] Debug pod is ready!"
POD_DEBUG=$(kubectl get pods | grep debug.*Running | cut -f 1 -d " ")
# kubectl exec -it $POD_DEBUG bash "mkdir -p /root/frigga"
kubectl cp .frigga/ default/$POD_DEBUG:/root/frigga/
kubectl apply \
    -f kubernetes/exporters.yml \
    -f kubernetes/monitoring.yml
kubectl exec $POD_DEBUG -- bash /root/frigga/.frigga/kubernetes/wait-for-endpoints.sh
echo ">> [LOG] Ready to apply changes!"