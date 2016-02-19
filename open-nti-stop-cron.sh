#!/bin/bash

comd=$1
docker exec -it $(docker ps | awk '/open-nti/ {print $1}') /usr/bin/python /opt/open-nti/startcron.py -a delete  -c "/usr/bin/python /opt/open-nti/open-nti.py -s $comd"
