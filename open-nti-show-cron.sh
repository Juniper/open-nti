#!/bin/bash

comd=$1

if [ $comd == "all" ]; then
    docker exec -it $(docker ps | awk '/open-nti/ {print $1}') /usr/bin/python /opt/open-nti/startcron.py -a show  -c "$comd"
    exit 1
fi
    
docker exec -it $(docker ps | awk '/open-nti/ {print $1}') /usr/bin/python /opt/open-nti/startcron.py -a show  -c "/usr/bin/python /opt/open-nti/open-nti.py -s $comd"
