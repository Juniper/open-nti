FROM fluent/fluentd:v0.12.43
MAINTAINER Damien Garros <dgarros@gmail.com>

USER root
WORKDIR /home/fluent

## Install python
RUN apk update \
    && apk add python-dev py-pip \
    && pip install --upgrade pip \
    && pip install envtpl \
    && apk del -r --purge gcc make g++ \
    && rm -rf /var/cache/apk/*

RUN apk add --no-cache --virtual .build-deps \
        build-base ruby-dev && \
    gem install --no-ri \
        yajl ltsv bigdecimal \
        influxdb zookeeper && \
    gem install ruby-kafka -v 0.3.17 && \
    apk del .build-deps && \
    rm -rf /var/cache/apk/* && \
    rm -rf /tmp/* /var/tmp/* /usr/lib/ruby/gems/*/cache/*.gem

# Copy Start script to generate configuration dynamically

ADD   fluentd-alpine.start.sh  fluentd-alpine.start.sh
RUN   chmod 777 fluentd-alpine.start.sh

COPY  fluent.conf /fluentd/etc/fluent.conf
COPY  plugins /fluentd/plugins

RUN   gem install --no-ri fluent-plugin-newsyslog
RUN   gem install --no-ri fluent-plugin-rewrite-tag-filter -v 1.6.0

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
