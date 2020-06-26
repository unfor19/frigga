#!/bin/bash
network=$(docker network ls | grep frigga_net)
[[ ! -z $network ]] && echo "ERROR: wait for network to be deleted, docker network ls, or restart docker daemon" && exit
HOSTNAME=$(hostname) docker stack deploy -c docker-swarm/docker-stack.yml frigga
