#!/bin/bash
whoami
pwd
ls -la
which minikube
minikube version
MINIKUBE_IP=$(minikube ip)
MINIKUBE_HOME=/home/runner/work/_temp
echo ">> [LOG] minikube IP = ${MINIKUBE_IP}"
echo ">> MINIKUBE_HOME contents - ${MINIKUBE_HOME}/.minikube/machines/minikube"
ls -la ${MINIKUBE_HOME}
which kubectl
kubectl version