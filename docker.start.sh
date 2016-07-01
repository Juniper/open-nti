#! /bin/bash

#Load params file with all variables
source ./open-nti.params

if [ -f "$1" ]
then
    DOCKER_COMPOSE_FILE=$1

fi

echo "Use docker compose file : $DOCKER_COMPOSE_FILE"
docker-compose -f $DOCKER_COMPOSE_FILE up -d

#
# ## Start New Container
# docker run -d --volume $(pwd)/$LOCAL_DIR_DATA:/opt/open-nti/data \
#               --volume $(pwd)/$LOCAL_DIR_DASHBOARD:/src/dashboards \
#               --volume /etc/localtime:/etc/localtime \
#               --restart always \
#               --publish $LOCAL_PORT_STATSD:8125/udp \
#               --publish $LOCAL_PORT_EVENT:6000/udp \
#               --publish $LOCAL_PORT_JTI:50000/udp \
#               --publish $LOCAL_PORT_NA:50010/udp \
#               --publish $LOCAL_PORT_ANALYTICSD:50020/udp \
#               --publish 80:80 \
#               --publish $LOCAL_PORT_GRAFANA:3000 \
#               --publish $LOCAL_PORT_INFLUXDB:8083 \
#               --publish $LOCAL_PORT_INFLUXDB_API:8086 \
#               --publish $LOCAL_PORT_SSH:22 \
#               --name $CONTAINER_NAME $IMAGE_NAME /sbin/my_init
