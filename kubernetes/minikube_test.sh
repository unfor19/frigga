#!/bin/bash
set -e
set -o pipefail
whoami
pwd
ls -la
which minikube
minikube version
MINIKUBE_IP=$(minikube ip)
if [[ -z $FRIGGA_TESTING ]]; then
    MINIKUBE_HOME=${HOME}
else
    MINIKUBE_HOME=/home/runner/work/_temp
fi
echo ">> [LOG] minikube IP = ${MINIKUBE_IP}"
echo ">> MINIKUBE_HOME contents - ${MINIKUBE_HOME}/.minikube/machines/minikube"
ls -la ${MINIKUBE_HOME}
which kubectl
kubectl version
