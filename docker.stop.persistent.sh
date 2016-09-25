#! /bin/bash

#Load params file with all variables
source ./open-nti.params

DOCKER_COMPOSE_FILE="docker-compose/opennti_persistent.yml"

echo "Use docker compose file : $DOCKER_COMPOSE_FILE"
docker-compose -f $DOCKER_COMPOSE_FILE down
