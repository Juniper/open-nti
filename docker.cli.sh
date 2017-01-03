#! /bin/bash

#Load params file with all variables
source ./open-nti.params

echo "$(tput setaf 5)this script (docker.cli.sh) is deprecated, it's been replaced with 'make cli' $(tput sgr0)"
docker exec -it $MAIN_CONTAINER_NAME /bin/bash
