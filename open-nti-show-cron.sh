#!/bin/bash

#Load params file with all variables
source ./open-nti.params

comd=$1
if [ $comd == "all" ]; then
    docker exec -it $CONTAINER_NAME /usr/bin/python /opt/open-nti/startcron.py -a show  -c "$comd"
    exit 1
fi

docker exec -it $CONTAINER_NAME /usr/bin/python /opt/open-nti/startcron.py -a show  -c "/usr/bin/python /opt/open-nti/open-nti.py -s $comd"
