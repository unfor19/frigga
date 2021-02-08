#!/bin/bash
prune=$1
kubectl delete \
    -f kubernetes/debug.yml \
    -f kubernetes/exporters.yml \
    -f kubernetes/monitoring.yml

minikube ssh "sudo rm -rf /home/docker/.frigga/ /home/docker/frigga" && echo ">> [LOG] Deleted frigga folder from minikube"
[[ ! -z $prune ]] && minikube ssh "docker system prune --volumes -a -f" && echo ">> [LOG] Successfully Docker system pruned"
rm -rf .frigga
