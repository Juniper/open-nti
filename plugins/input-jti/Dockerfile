FROM fluent/fluentd:v0.12.29
MAINTAINER Damien Garros <dgarros@gmail.com>

ENV FLUENTD_JUNIPER_VERSION 0.3.0
ARG TELEGRAF_VERSION=1.1.2

USER root
WORKDIR /home/fluent

## Install python
RUN apk update \
    && apk add python-dev py-pip \
    && pip install --upgrade pip \
    && pip install envtpl \
    && apk del -r --purge gcc make g++ \
    && rm -rf /var/cache/apk/*

ENV PATH /home/fluent/.gem/ruby/2.2.0/bin:$PATH

RUN apk --no-cache --update add \
                            build-base \
                            ruby-dev && \
    apk add bash && \
    apk add tcpdump && \
    apk add sudo && \
    echo 'gem: --no-document' >> /etc/gemrc && \
    gem install --no-ri --no-rdoc \
              influxdb \
              statsd-ruby \
              dogstatsd-ruby \
              ruby-kafka yajl ltsv zookeeper \
              bigdecimal && \
    gem install --prerelease protobuf &&\
    gem install --no-ri --no-rdoc \
                fluent-plugin-juniper-telemetry -v ${FLUENTD_JUNIPER_VERSION} &&\
    apk del build-base ruby-dev && \
    rm -rf /tmp/* /var/tmp/* /var/cache/apk/*

# Copy Start script to generate configuration dynamically
ADD     fluentd-alpine.start.sh   fluentd-alpine.start.sh
RUN     chown -R fluent:fluent fluentd-alpine.start.sh &&\
        chmod 777 fluentd-alpine.start.sh

COPY    fluent.conf /fluentd/etc/fluent.conf
COPY    plugins /fluentd/plugins

RUN echo "fluent ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

#############################
## Install Telegraf
#############################
RUN apk add --no-cache ca-certificates openssl wget && \
    update-ca-certificates

RUN wget -q https://dl.influxdata.com/telegraf/releases/telegraf-${TELEGRAF_VERSION}-static_linux_amd64.tar.gz && \
    mkdir -p /usr/src /etc/telegraf && \
    tar -C /usr/src -xzf telegraf-${TELEGRAF_VERSION}-static_linux_amd64.tar.gz && \
    mv /usr/src/telegraf*/telegraf.conf /etc/telegraf/ && \
    chmod +x /usr/src/telegraf*/* && \
    cp -a /usr/src/telegraf*/* /usr/bin/ && \
    rm -rf *.tar.gz* /usr/src /root/.gnupg

COPY telegraf.toml /home/fluent/telegraf.toml
RUN touch /var/log/telegraf-monitoring.log &&\
    chmod 777 /var/log/telegraf-monitoring.log



USER fluent
EXPOSE 24284

ENV OUTPUT_KAFKA=false \
    OUTPUT_INFLUXDB=true \
    OUTPUT_STDOUT=false \
    PORT_JTI=50000 \
    PORT_ANALYTICSD=50020 \
    INFLUXDB_ADDR=localhost \
    INFLUXDB_PORT=8086 \
    INFLUXDB_DB=juniper \
    INFLUXDB_USER=juniper \
    INFLUXDB_PWD=juniper \
    INFLUXDB_FLUSH_INTERVAL=2 \
    KAFKA_ADDR=localhost \
    KAFKA_PORT=9092 \
    KAFKA_DATA_TYPE=json \
    KAFKA_TOPIC=jnpr.jvision

CMD /home/fluent/fluentd-alpine.start.sh
