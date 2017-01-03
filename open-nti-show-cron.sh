#!/bin/bash

#Load params file with all variables
source ./open-nti.params
echo "$(tput setaf 5)this script (open-nti-show-cron.sh) is deprecated, it's been replaced with 'make cron-show' $(tput sgr0)"

comd=$1
if [ $comd == "all" ]; then
    docker exec -it $MAIN_CONTAINER_NAME /usr/bin/python /opt/open-nti/startcron.py -a show  -c "$comd"
    exit 1
fi

docker exec -it $MAIN_CONTAINER_NAME /usr/bin/python /opt/open-nti/startcron.py -a show  -c "/usr/bin/python /opt/open-nti/open-nti.py -s $comd"
