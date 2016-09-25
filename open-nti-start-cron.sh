#!/bin/bash

#Load params file with all variables
source ./open-nti.params

time=$1
comd=$2
docker exec -it $CONTAINER_NAME /usr/bin/python /opt/open-nti/startcron.py -a add -t "$time" -c "/usr/bin/python /opt/open-nti/open-nti.py -s $comd"
