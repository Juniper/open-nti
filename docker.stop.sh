#! /bin/bash

#Load params file with all variables
source ./open-nti.params

if [ -f "$1" ]
then
    DOCKER_COMPOSE_FILE=$1

fi

echo "Use docker compose file : $DOCKER_COMPOSE_FILE"
docker-compose -f $DOCKER_COMPOSE_FILE down
