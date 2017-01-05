FROM nginx:1.11.8-alpine
MAINTAINER Damien Garros <dgarros@gmail.com>

ARG CONSUL_VERSION=0.7.2
ARG CONSUL_TEMPLATE_VERSION=0.16.0

RUN apk update &&\
    apk add wget

RUN apk add --no-cache ca-certificates && \
    update-ca-certificates

#############################
## Install consul agent
#############################
RUN     mkdir -p /var/lib/consul /usr/share/consul /etc/consul/conf.d &&\
        wget https://releases.hashicorp.com/consul/${CONSUL_VERSION}/consul_${CONSUL_VERSION}_linux_amd64.zip &&\
        unzip consul_${CONSUL_VERSION}_linux_amd64.zip &&\
        mv consul /usr/local/bin/consul

#############################
## Install consul template
#############################
RUN wget -q https://releases.hashicorp.com/consul-template/${CONSUL_TEMPLATE_VERSION}/consul-template_${CONSUL_TEMPLATE_VERSION}_linux_amd64.zip &&\
    unzip consul-template_${CONSUL_TEMPLATE_VERSION}_linux_amd64.zip && \
    mv consul-template /usr/local/bin/consul-template &&\
    rm -rf /consul-template_${CONSUL_TEMPLATE_VERSION}_linux_amd64.zip && \
    mkdir -p /consul-template /consul-template/config.d /consul-template/templates

ADD     consul /etc/consul/conf.d

COPY  nginx.conf.tpl /source/nginx.conf.tpl
COPY  start-lb-udp.sh /source/start-lb-udp.sh

RUN   chmod +x /source/start-lb-udp.sh

WORKDIR /source

CMD ["/source/start-lb-udp.sh"]
