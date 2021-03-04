#!/bin/bash
set -e
set -o pipefail

# Copy relevant files to `.frigga/`
source kubernetes/minikube_rsync.sh

kubectl apply -f kubernetes/debug.yml

while [[ -z "$(kubectl get pods | grep debug.*Running)" ]]; do
    echo ">> [LOG] Waiting for the debug pod to be ready"
    sleep 5
done
echo ">> [LOG] Debug pod is ready!"
POD_DEBUG=$(kubectl get pods | grep debug.*Running | cut -f 1 -d " ")

# Copy from `.frigga/` to debug pod
kubectl cp .frigga/ default/"${POD_DEBUG}":/root/frigga/

kubectl apply \
    -f kubernetes/exporters.yml \
    -f kubernetes/monitoring.yml

GRAFANA_HOST="http://grafana.default.svc.cluster.local:3000"
PROMETHEUS_HOST="http://prometheus.default.svc.cluster.local:9090"
NODEEXPORTER_HOST="http://node-exporter.default.svc.cluster.local:9100"
CONTAINEREXPORTER_HOST="http://container-exporter.default.svc.cluster.local:9104"

kubectl exec "$POD_DEBUG" -- bash /root/frigga/.frigga/scripts/wait_for_endpoints.sh "$GRAFANA_HOST" "$PROMETHEUS_HOST" "$NODEEXPORTER_HOST" "$CONTAINEREXPORTER_HOST"
echo ">> [LOG] Ready to apply changes!"