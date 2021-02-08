#!/bin/bash
kubectl port-forward deployment/grafana 3000:3000
# Open your browser - http://localhost:3000
# Login admin:admin
# View the dashboards