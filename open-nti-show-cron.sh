#!/bin/bash

#Load params file with all variables
source ./open-nti.params

# Find container ID
CONTAINER_ID=$(docker ps | grep $CONTAINER_NAME | awk '{print $1}')

echo "Container ID : $CONTAINER_ID"

comd=$1
if [ $comd == "all" ]; then
    docker exec -it $CONTAINER_ID /usr/bin/python /opt/open-nti/startcron.py -a show  -c "$comd"
    exit 1
fi

docker exec -it $CONTAINER_ID /usr/bin/python /opt/open-nti/startcron.py -a show  -c "/usr/bin/python /opt/open-nti/open-nti.py -s $comd"
