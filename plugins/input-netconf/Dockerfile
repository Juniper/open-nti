FROM juniper/pyez:2.0.1

WORKDIR /source
USER root

## To be removed once change merge upstream
RUN apk add --no-cache ca-certificates && \
    update-ca-certificates
RUN apk add --no-cache wget git

ARG TELEGRAF_VERSION=1.1.2
ARG CONSUL_VERSION=0.7.2
ARG CONSUL_TEMPLATE_VERSION=0.16.0

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

#############################
## Install consul template
#############################
RUN wget -q https://releases.hashicorp.com/consul-template/${CONSUL_TEMPLATE_VERSION}/consul-template_${CONSUL_TEMPLATE_VERSION}_linux_amd64.zip &&\
    unzip consul-template_${CONSUL_TEMPLATE_VERSION}_linux_amd64.zip && \
    mv consul-template /usr/local/bin/consul-template &&\
    rm -rf /consul-template_${CONSUL_TEMPLATE_VERSION}_linux_amd64.zip && \
    mkdir -p /consul-template /consul-template/config.d /consul-template/templates

#############################
## Install consul agent
#############################
RUN     mkdir -p /var/lib/consul /usr/share/consul /etc/consul/conf.d &&\
        wget https://releases.hashicorp.com/consul/${CONSUL_VERSION}/consul_${CONSUL_VERSION}_linux_amd64.zip &&\
        unzip consul_${CONSUL_VERSION}_linux_amd64.zip &&\
        mv consul /usr/local/bin/consul

ADD     consul /etc/consul/conf.d

ENV BUILD 1
RUN git clone https://github.com/Juniper/py-netconf-collector.git
RUN pip install -r py-netconf-collector/requirements.txt

COPY start-input-netconf.sh /source/start-input-netconf.sh
RUN chmod +x /source/start-input-netconf.sh

RUN mkdir /data
WORKDIR /data

CMD ["/source/start-input-netconf.sh"]
