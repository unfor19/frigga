#!/bin/bash
set -e
set -o pipefail
MINIKUBE_IP=$(minikube ip)
if [[ -z $FRIGGA_TESTING ]]; then
    MINIKUBE_HOME=${HOME}
else
    MINIKUBE_HOME=/home/runner/work/_temp
fi

rm -rf .frigga
mkdir .frigga
echo $PWD

rsync -Pavr --filter=':- .gitignore' $PWD/ .frigga/
