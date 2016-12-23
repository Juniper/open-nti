FROM fluent/fluentd:v0.12.29
MAINTAINER Damien Garros <dgarros@gmail.com>

USER root
WORKDIR /home/fluent

ARG CONSUL_VERSION=0.7.2

## Install python
RUN apk update &&\
    apk add python-dev py-pip ca-certificates &&\
    pip install --upgrade pip &&\
    pip install envtpl &&\
    update-ca-certificates &&\
    apk del -r --purge gcc make g++ &&\
    rm -rf /var/cache/apk/*

ENV PATH /home/fluent/.gem/ruby/2.2.0/bin:$PATH

RUN apk --no-cache --update add \
                            build-base \
                            ruby-dev && \
    echo 'gem: --no-document' >> /etc/gemrc && \
    gem install --no-ri --no-rdoc \
              ruby-kafka yajl ltsv zookeeper \
              influxdb \
              fluent-plugin-kafka \
              bigdecimal && \
    apk del build-base ruby-dev && \
    rm -rf /tmp/* /var/tmp/* /var/cache/apk/*

# Copy Start script to generate configuration dynamically
ADD     fluentd-alpine.start.sh         fluentd-alpine.start.sh
RUN     chown -R fluent:fluent fluentd-alpine.start.sh &&\
        chmod 777 fluentd-alpine.start.sh

RUN apk update &&\
    apk add ca-certificates wget &&\
    update-ca-certificates

## Install consul agent
RUN     mkdir -p /var/lib/consul /usr/share/consul /etc/consul/conf.d &&\
        chown -R fluent:fluent /usr/share/consul /var/lib/consul &&\
        wget https://releases.hashicorp.com/consul/${CONSUL_VERSION}/consul_${CONSUL_VERSION}_linux_amd64.zip &&\
        unzip consul_${CONSUL_VERSION}_linux_amd64.zip &&\
        mv consul /usr/local/bin/consul &&\
        touch /var/log/consul.log &&\
        rm -f consul_${CONSUL_VERSION}_linux_amd64.zip &&\
        chown fluent:fluent /var/log/consul.log &&\
        chown fluent:fluent /usr/local/bin/consul

ADD     consul /etc/consul/conf.d

COPY    fluent.conf /fluentd/etc/fluent.conf
COPY    plugins /fluentd/plugins

USER fluent

RUN   gem install --no-ri --no-rdoc fluent-plugin-newsyslog
RUN   gem install --no-ri --no-rdoc fluent-plugin-rewrite-tag-filter
EXPOSE 24220

ENV OUTPUT_KAFKA=false \
    OUTPUT_INFLUXDB=false \
    OUTPUT_MQTT=false \
    OUTPUT_STDOUT=false \
    PORT_SYSLOG=6000 \
    INFLUXDB_ADDR=localhost \
    INFLUXDB_PORT=8086 \
    INFLUXDB_DB=juniper \
    INFLUXDB_USER=juniper \
    INFLUXDB_PWD=juniper \
    INFLUXDB_FLUSH_INTERVAL=5s \
    INFLUXDB_NUM_THREADS=2 \
    INFLUXDB_QUEUE_LIMIT=2048 \
    INFLUXDB_CHUNK_LIMIT=100m \
    KAFKA_ADDR=localhost \
    KAFKA_PORT=9092 \
    KAFKA_DATA_TYPE=json \
    KAFKA_TOPIC=events

CMD /home/fluent/fluentd-alpine.start.sh
