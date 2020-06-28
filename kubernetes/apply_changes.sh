#!/bin/bash
GRAFANA_HOST="http://grafana.monitoring.svc.cluster.local:3000"
GRAFANA_API_KEY=$(curl -X POST -sL --user admin:admin -H "Content-Type: application/json" --data '{"name":"local1","role":"Viewer","secondsToLive":86400}' ${GRAFANA_HOST}/api/auth/keys | jq .key)

frigga gl -gurl ${GRAFANA_HOST} -gkey ${GRAFANA_API_KEY}
# generated .metrics.json

