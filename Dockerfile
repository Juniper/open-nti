FROM zhanghaofeng3672/open-nti-evo:latest
MAINTAINER Haofeng Zhang <hfzhang.cn@gmail.com>

### Remove Grafana login
COPY     docker/grafana/custom.ini /opt/grafana/conf/

### open-nti python scripts (for gathering informatino from server to router)  ###
ADD     open-nti/open-nti.py /opt/open-nti/open-nti.py
ADD     open-nti/startcron.py /opt/open-nti/startcron.py
ADD     tests/main/pyez_mock.py /opt/open-nti/pyez_mock.py
