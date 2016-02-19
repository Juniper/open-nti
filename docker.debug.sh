#! /bin/bash

docker run --rm -t \
        -p 50000:50000/udp -p 50010:50010/udp -p 50020:50020/udp  \
        -p 8125:8125/udp -p 50021:50021/udp -p 6000:6000/udp \
        -p 80:80 -p 3000:3000 -p 8083:8083 -p 8086:8086 \
        -i juniper/open-nti /sbin/my_init -- bash -l
