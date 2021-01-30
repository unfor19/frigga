#!/bin/bash
set -e
set -o pipefail
MINIKUBE_IP=$(minikube ip)
if [[ -z $FRIGGA_TESTING ]]; then
    MINIKUBE_HOME=${HOME}
else
    MINIKUBE_HOME=/home/runner/work/_temp
fi

AGENT_PID=$(eval `ssh-agent -s`)
echo ">> [LOG] ssh-agent PID = $AGENT_PID"

rm -rf .frigga
mkdir .frigga
rsync -Pavr --filter=':- .gitignore' $PWD/ .frigga/
cp .frigga/kubernetes/prometheus-original.yml .frigga/kubernetes/prometheus.yml
