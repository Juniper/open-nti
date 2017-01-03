#!/bin/bash

#Load params file with all variables
source ./open-nti.params
echo "$(tput setaf 5)this script (open-nti-stop-cron.sh) is deprecated, it's been replaced with 'make cron-delete' $(tput sgr0)"

comd=$1
docker exec -it $MAIN_CONTAINER_NAME /usr/bin/python /opt/open-nti/startcron.py -a delete  -c "/usr/bin/python /opt/open-nti/open-nti.py -s $comd"
