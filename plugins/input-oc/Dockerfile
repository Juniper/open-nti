FROM golang:1.6.2-wheezy

ARG CONSUL_VERSION=0.7.2
ARG CONSUL_TEMPLATE_VERSION=0.16.0

RUN mkdir /go/src/github.com
RUN mkdir /go/src/github.com/influxdata
WORKDIR /go/src/github.com/influxdata

RUN go get -u -v google.golang.org/grpc

RUN apt-get update &&\
    apt-get install -y unzip wget

RUN git clone https://github.com/ajhai/telegraf.git

#RUN  mkdir /go/src/github.com/influxdata/telegraf
#COPY telegraf /go/src/github.com/influxdata/telegraf

########################
### Install Consul   ###
########################
RUN     mkdir -p /var/lib/consul &&\
        mkdir -p /usr/share/consul &&\
        mkdir -p /etc/consul/conf.d &&\
        wget https://releases.hashicorp.com/consul/${CONSUL_VERSION}/consul_${CONSUL_VERSION}_linux_amd64.zip &&\
        unzip  consul_${CONSUL_VERSION}_linux_amd64.zip &&\
        mv consul /usr/local/bin/consul

ADD     consul/config.json /etc/consul/conf.d/config.json
ADD     consul/services.json /etc/consul/conf.d/services.json

################################
### Install Consul Template  ###
################################
RUN wget -q https://releases.hashicorp.com/consul-template/${CONSUL_TEMPLATE_VERSION}/consul-template_${CONSUL_TEMPLATE_VERSION}_linux_amd64.zip &&\
    unzip consul-template_${CONSUL_TEMPLATE_VERSION}_linux_amd64.zip && \
    mv consul-template /usr/local/bin/consul-template &&\
    rm -rf /consul-template_${CONSUL_TEMPLATE_VERSION}_linux_amd64.zip && \
    mkdir -p /consul-template /consul-template/config.d /consul-template/templates

WORKDIR /go/src/github.com/influxdata/telegraf

RUN make

RUN mkdir /source
WORKDIR /source

COPY telegraf.toml /source/telegraf.toml

COPY start-input-oc.sh /source/start-input-oc.sh
RUN chmod +x /source/start-input-oc.sh

CMD ["/source/start-input-oc.sh"]
# CMD /go/bin/telegraf -debug
