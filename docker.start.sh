#! /bin/bash

docker stop open-nti_con
docker rm open-nti_con

docker run -d --volume $(pwd)/data:/opt/open-nti/data \
              --volume $(pwd)/logs:/opt/open-nti/logs \
              --volume $(pwd)/db:/var/lib/influxdb \
              --volume $(pwd)/dashboards:/src/dashboards \
              --restart always \
              --publish 8125:8125/udp --publish 6000:6000/udp \
              --publish 50000:50000/udp --publish 50010:50010/udp --publish 50020:50020/udp \
              --publish 80:80 --publish 3000:3000 --publish 8083:8083 --publish 8086:8086 \
              --name open-nti_con juniper/open-nti /sbin/my_init
