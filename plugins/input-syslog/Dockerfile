# 20220314 JES
#FROM fluent/fluentd:v0.12.29
FROM fluent/fluentd:v1.14.5-1.1
MAINTAINER Damien Garros <dgarros@gmail.com>

ENV FLUENTD_JUNIPER_VERSION 0.2.11

USER root
WORKDIR /home/fluent

## Install python
# 20220314 JES
#RUN apk update \
#    && apk add python-dev py-pip \
#    && pip install --upgrade pip \
#    && pip install envtpl \
#    && ael -r --purge gcc make g++ \
#    && rm -rf /var/cache/apk/*
RUN apk update \
    && apk add python3-dev py3-pip \
    && pip install --upgrade pip \
    && pip install envtpl \
    && apk del -r --purge gcc make g++ \
    && rm -rf /var/cache/apk/*

ENV PATH /home/fluent/.gem/ruby/2.2.0/bin:$PATH

# 20220314 JES
#RUN apk --no-cache --update add \
#                            build-base \
#                            ruby-dev && \
#    echo 'gem: --no-document' >> /etc/gemrc && \
#    gem install --no-ri --no-rdoc \
#              yajl ltsv zookeeper \
#              influxdb \
#              bigdecimal && \
#    gem install ruby-kafka -v 0.3.17 && \
#    apk del build-base ruby-dev && \
#    rm -rf /tmp/* /var/tmp/* /var/cache/apk/*

#RUN apk --no-cache update add \
#                            build-base \
#                            ruby-dev && \
#    echo 'gem: --no-document' >> /etc/gemrc && \
#    gem install --no-document  \
#              yajl ltsv zookeeper \
#              influxdb \
#              bigdecimal && \
#    gem install ruby-kafka -v 0.3.17 && \
#    apk del build-base ruby-dev && \
#    rm -rf /tmp/* /var/tmp/* /var/cache/apk/*

RUN apk --no-cache --update add \
                            build-base \
                            ruby-dev 
RUN echo 'gem: --no-document' >> /etc/gemrc && \
    gem install --no-document  \
              yajl ltsv zookeeper \
              influxdb \
              bigdecimal && \
    gem install ruby-kafka -v 0.3.17 && \
    apk del build-base ruby-dev && \
    rm -rf /tmp/* /var/tmp/* /var/cache/apk/*

RUN apk update  \
    && apk add ruby-dev

# Copy Start script to generate configuration dynamically
ADD     fluentd-alpine.start.sh         fluentd-alpine.start.sh
RUN     chown -R fluent:fluent fluentd-alpine.start.sh
RUN     chmod 777 fluentd-alpine.start.sh

COPY    fluent.conf /fluentd/etc/fluent.conf
COPY    plugins /fluentd/plugins

# 20220314 JES
#USER fluent
USER root

# 20220314 JES
#RUN   gem install --no-ri --no-rdoc fluent-plugin-newsyslog
#RUN   gem install --no-ri --no-rdoc fluent-plugin-rewrite-tag-filter -v 1.6.0
RUN   gem install --no-document  fluent-plugin-newsyslog
RUN   gem install --no-document  fluent-plugin-rewrite-tag-filter -v 2.4.0 
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
