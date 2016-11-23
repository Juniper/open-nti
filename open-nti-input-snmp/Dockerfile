FROM phusion/baseimage:0.9.18
MAINTAINER Damien Garros <dgarros@gmail.com>

RUN     apt-get -y update && \
        apt-get -y upgrade && \
        apt-get clean   && \
        rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# dependencies
RUN     apt-get -y update && \
        apt-get -y install \
              curl \
              build-essential \
              unzip

ENV CONSUL_TEMPLATE_VERSION=0.16.0
ENV TELEGRAF_VERSION 1.0.1 

########################
### Install telegraf ###
########################


RUN     curl -s -o /tmp/consul-template_linux_amd64.zip https://releases.hashicorp.com/consul-template/${CONSUL_TEMPLATE_VERSION}/consul-template_${CONSUL_TEMPLATE_VERSION}_linux_amd64.zip && \
        unzip /tmp/consul-template_linux_amd64.zip -d /tmp/ && \
        mv /tmp/consul-template /usr/local/bin/consul-template && \
        rm /tmp/consul-template_linux_amd64.zip -d /var/tmp/

RUN     curl -s -o /tmp/telegraf_latest_amd64.deb https://dl.influxdata.com/telegraf/releases/telegraf_${TELEGRAF_VERSION}_amd64.deb && \
        dpkg -i /tmp/telegraf_latest_amd64.deb && \
        rm /tmp/telegraf_latest_amd64.deb


#RUN mkdir -p /etc/consul-template/config.d /etc/consul-template/template.d

#ADD ./config/consul.cfg /etc/consul-template/config.d/consul.cfg
#ADD ./config/consul-telegraf.cfg /etc/consul-template/config.d/consul-telegraf.cfg
#ADD ./config/telegraf.tmpl /etc/consul-template/template.d/telegraf.tmpl

RUN mkdir /etc/service/consul-template
ADD ./config/consul-template.start.sh /etc/service/consul-template/run
RUN chmod +x /etc/service/consul-template/run


########################
### Configuration    ###
########################

WORKDIR /root
ENV HOME /root

RUN chmod -R 777 /var/log/


CMD ["/sbin/my_init"]

