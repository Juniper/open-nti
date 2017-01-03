#!/bin/bash

#Load params file with all variables
source ./open-nti.params
echo "$(tput setaf 5)this script (open-nti-start-cron.sh) is deprecated, it's been replaced with 'make cron-add' $(tput sgr0)"

time=$1
comd=$2
docker exec -it $MAIN_CONTAINER_NAME /usr/bin/python /opt/open-nti/startcron.py -a add -t "$time" -c "/usr/bin/python /opt/open-nti/open-nti.py -s $comd"
