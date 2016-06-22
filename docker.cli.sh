#! /bin/bash

#Load params file with all variables
source ./open-nti.params

CONTAINER_IP='127.0.0.1'

## Try to identify what is the operating system

if [ "$(uname)" == "Darwin" ]
then
    # If we are on Mac, the IP to use is the IP of the docker VM
    CONTAINER_IP=$(docker-machine ip default)

elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]
then
    # If we are on Linux, we are using Docker to get the IP of the container
    CONTAINER_IP=$(docker inspect  --format '{{ .NetworkSettings.IPAddress }}' $CONTAINER_NAME)
    LOCAL_PORT_SSH=22

elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ]
then
    echo "Unable to find Container IP, using $CONTAINER_IP"
else
    echo "Unable to find Container IP, using $CONTAINER_IP"
fi

ssh -i insecure_key -p $LOCAL_PORT_SSH root@$CONTAINER_IP
