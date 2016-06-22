#!/bin/bash

#Load params file with all variables
source ./open-nti.params

# Find container ID
CONTAINER_ID=$(docker ps | grep $CONTAINER_NAME | awk '{print $1}')

echo "Container ID : $CONTAINER_ID"

comd=$1
docker exec -it $CONTAINER_ID /usr/bin/python /opt/open-nti/startcron.py -a delete  -c "/usr/bin/python /opt/open-nti/open-nti.py -s $comd"
