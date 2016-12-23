FROM phusion/baseimage:0.9.18
MAINTAINER Damien Garros <dgarros@gmail.com>

RUN     apt-get -y update && \
        apt-get -y upgrade && \
        apt-get clean   &&\
        rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# dependencies
RUN     apt-get -y update && \
        apt-get -y install \
        git adduser libfontconfig wget make curl && \
        apt-get clean   &&\
        rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN     rm -f /etc/service/sshd/down
RUN     /usr/sbin/enable_insecure_key

# Latest version
ENV GRAFANA_VERSION 3.1.1-1470047149
ENV INFLUXDB_VERSION 1.0.2
ENV TELEGRAF_VERSION 1.0.1

RUN     apt-get -y update && \
        apt-get -y install \
            build-essential \
            python-simplejson \
            python-support \
            python-dev \
            python-yaml \
            python-pip \
            python-dev \
            libxml2-dev \
            libxslt-dev \
            tcpdump \
            tree \
            nginx-light \
            snmp \
            zlib1g-dev \
            libffi-dev \
            libssl-dev && \
        apt-get clean   &&\
        rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# # Install some python modules
RUN     pip install influxdb && \
        pip install xmltodict && \
        pip install pexpect && \
        easy_install pysnmp && \
        pip install lxml && \
        pip install python-crontab && \
        pip install junos-eznc && \
        pip install pytest && \
        pip install mock &&\
        pip install httplib2 &&\
        pip install cryptography==1.2.1

RUN     mkdir /src

########################
### Install Grafana
########################
RUN     mkdir /src/grafana                                                                                    &&\
        mkdir /opt/grafana                                                                                    &&\
        wget https://grafanarel.s3.amazonaws.com/builds/grafana-${GRAFANA_VERSION}.linux-x64.tar.gz -O /src/grafana.tar.gz &&\
        tar -xzf /src/grafana.tar.gz -C /opt/grafana --strip-components=1                                     &&\
        rm /src/grafana.tar.gz

RUN     /opt/grafana/bin/grafana-cli plugins install grafana-piechart-panel

########################
### Install InfluxDB ###
########################

RUN     curl -s -o /tmp/influxdb_latest_amd64.deb https://dl.influxdata.com/influxdb/releases/influxdb_${INFLUXDB_VERSION}_amd64.deb && \
        dpkg -i /tmp/influxdb_latest_amd64.deb && \
        rm /tmp/influxdb_latest_amd64.deb

ADD     docker/influxdb/types.db /usr/share/collectd/types.db
ADD     docker/influxdb/influxdb-config.toml /config/config.toml
ADD     docker/influxdb/influxdbrun.sh /influxdbrun.sh

RUN     mkdir /etc/service/influxdb
ADD     docker/influxdb/influxdb.launcher.sh /etc/service/influxdb/run

########################
### Install telegraf ###
########################

RUN     curl -s -o /tmp/telegraf_latest_amd64.deb https://dl.influxdata.com/telegraf/releases/telegraf_${TELEGRAF_VERSION}_amd64.deb && \
        dpkg -i /tmp/telegraf_latest_amd64.deb && \
        rm /tmp/telegraf_latest_amd64.deb

ADD     docker/telegraf/telegraf.conf /etc/telegraf/telegraf.conf

RUN     mkdir /etc/service/telegraf
ADD     docker/telegraf/telegraf.launcher.sh /etc/service/telegraf/run

########################
### Configuration    ###
########################

### Configure Grafana ###
ADD     docker/grafana/custom.ini /opt/grafana/conf/custom.ini
ADD     docker/grafana/run.sh /etc/service/grafana/run
ADD     docker/grafana/grafana.init.sh /etc/my_init.d/grafana.init.sh

# Add the default dashboards
RUN     mkdir /src/dashboards && \
        mkdir /opt/grafana/data && \
        chown -R www-data /opt/grafana/data

### Configure nginx ###
ADD     docker/nginx/nginx.conf /etc/nginx/nginx.conf
ADD     docker/nginx/run.sh /etc/service/nginx/run

### open-nti python scripts (for gathering informatino from server to router)  ###
ADD     open-nti/open-nti.py /opt/open-nti/open-nti.py
ADD     open-nti/startcron.py /opt/open-nti/startcron.py
ADD     tests/main/pyez_mock.py /opt/open-nti/pyez_mock.py

### Install fswatch and add scripts to upload data to consul
RUN     wget https://github.com/emcrisostomo/fswatch/releases/download/1.9.3/fswatch-1.9.3.tar.gz &&\
        tar -xzf fswatch-1.9.3.tar.gz &&\
        cd fswatch-1.9.3 &&\
        ./configure &&\
        make &&\
        make install &&\
        ldconfig

RUN     mkdir /opt/consul
ADD     docker/consul/load_consul.py /opt/consul/load_consul.py
ADD     docker/consul/opennti_input.py /opt/consul/opennti_input.py

ADD     docker/consul/watch_dir_and_load.sh /etc/service/consul/run

### Add test files
RUN     mkdir /opt/open-nti/tests

# ################

RUN     chmod +x /etc/service/nginx/run         &&\
        chmod +x /etc/service/grafana/run       &&\
        chmod +x /etc/my_init.d/grafana.init.sh &&\
        chmod +x /etc/service/influxdb/run      &&\
        chmod +x /etc/service/telegraf/run      &&\
        chmod +x /etc/service/consul/run        &&\
        chmod +x /influxdbrun.sh

WORKDIR /
ENV HOME /root
ENV SSL_SUPPORT **False**
ENV SSL_CERT **None**
RUN chmod -R 777 /var/log/

# ## Graphana
EXPOSE 80
EXPOSE 3000

# # Influxdb Admin server WebUI
EXPOSE 8083
EXPOSE 8086

CMD ["/sbin/my_init"]
