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
# ssh-add ${MINIKUBE_HOME}/.minikube/machines/minikube/id_rsa
# IDENTITY_ADDED=$1

rm -rf .frigga
mkdir .frigga
rsync -Pavr --filter=':- .gitignore' $PWD/ .frigga/
cp .frigga/kubernetes/prometheus-original.yml .frigga/kubernetes/prometheus.yml
# if [[ $IDENTITY_ADDED -eq 0 ]]; then
#     echo ">> [LOG] Added ssh key"
#     rsync -Pavr -e "ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" \
#         --filter=':- .gitignore' $PWD docker@${MINIKUBE_IP}:/home/docker
# else
#     echo ">> [ERROR] Failed to add ssh key"
#     exit
# fi
