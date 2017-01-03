#! /bin/bash

#Load params file with all variables
source ./open-nti.params
echo "$(tput setaf 5)this script (docker.stop.persistent.sh) is deprecated, it's been replaced with 'make stop-persistent' $(tput sgr0)"

DOCKER_COMPOSE_FILE="docker-compose/opennti_persistent.yml"

BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$BRANCH" = "master" ]
then
  IMAGE_TAG=latest
else
  IMAGE_TAG=$BRANCH
fi

echo "Use docker compose file : $DOCKER_COMPOSE_FILE"
IMAGE_TAG=$IMAGE_TAG docker-compose -f $DOCKER_COMPOSE_FILE down
