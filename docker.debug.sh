#! /bin/bash


#Load params file with all variables
source open-nti.params

docker run --rm -t \
        --volume $(pwd)/$LOCAL_DIR_DATA:/opt/open-nti/data \
        --volume $(pwd)/$LOCAL_DIR_DASHBOARD:/src/dashboards \
        --publish $LOCAL_PORT_STATSD:8125/udp \
        --publish $LOCAL_PORT_EVENT:6000/udp \
        --publish $LOCAL_PORT_JTI:50000/udp \
        --publish $LOCAL_PORT_NA:50010/udp \
        --publish $LOCAL_PORT_ANALYTICSD:50020/udp \
        --publish 80:80 \
        --publish $LOCAL_PORT_GRAFANA:3000 \
        --publish $LOCAL_PORT_INFLUXDB:8083 \
        --publish $LOCAL_PORT_INFLUXDB_API:8086 \
        --publish $LOCAL_PORT_SSH:22 \
        -i $IMAGE_NAME /sbin/my_init -- bash -l
