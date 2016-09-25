#!/bin/bash

#Load params file with all variables
source ./open-nti.params

comd=$1
docker exec -it $CONTAINER_NAME /usr/bin/python /opt/open-nti/startcron.py -a delete  -c "/usr/bin/python /opt/open-nti/open-nti.py -s $comd"
