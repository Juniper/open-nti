FROM juniper/pyez:2.1.8

WORKDIR /source
USER root

## To be removed once change merge upstream
RUN apk add --no-cache ca-certificates && \
    update-ca-certificates
RUN apk add --no-cache wget git

ARG TELEGRAF_VERSION=1.7.0

#############################
## Install Telegraf
#############################
RUN wget -q https://dl.influxdata.com/telegraf/releases/telegraf-${TELEGRAF_VERSION}-static_linux_amd64.tar.gz && \
    mkdir -p /usr/src /etc/telegraf && \
    tar -C /usr/src -xzf telegraf-${TELEGRAF_VERSION}-static_linux_amd64.tar.gz && \
    mv /usr/src/telegraf*/telegraf.conf /etc/telegraf/ && \
    chmod +x /usr/src/telegraf*/* && \
    cp -a /usr/src/telegraf*/* /usr/bin/ && \
    rm -rf *.tar.gz* /usr/src /root/.gnupg

COPY start-input-snmp.sh /source/start-input-snmp.sh
RUN chmod +x /source/start-input-snmp.sh

RUN mkdir /data
RUN mkdir /data/templates
#ADD templates /data/templates/
WORKDIR /data

CMD ["/source/start-input-snmp.sh"]
