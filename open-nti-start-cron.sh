#!/bin/bash

time=$1
comd=$2
docker exec -it $(docker ps | awk '/open-nti/ {print $1}') /usr/bin/python /opt/open-nti/startcron.py -a add -t "$time" -c "/usr/bin/python /opt/open-nti/open-nti.py -s $comd"
