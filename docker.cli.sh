#! /bin/bash

#Load params file with all variables
source ./open-nti.params

docker exec -it $CONTAINER_NAME /bin/bash
