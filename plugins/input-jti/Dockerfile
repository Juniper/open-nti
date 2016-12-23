FROM fluent/fluentd:v0.12.29
MAINTAINER Damien Garros <dgarros@gmail.com>

ENV FLUENTD_JUNIPER_VERSION 0.3.0

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

RUN apk update &&\
    apk add ca-certificates wget &&\
    update-ca-certificates

#############################
## Install consul agent
#############################
RUN     mkdir -p /var/lib/consul /usr/share/consul /etc/consul/conf.d &&\
        chown -R fluent:fluent /usr/share/consul /var/lib/consul &&\
        wget https://releases.hashicorp.com/consul/0.7.2/consul_0.7.2_linux_amd64.zip &&\
        unzip consul_0.7.2_linux_amd64.zip &&\
        mv consul /usr/local/bin/consul &&\
        touch /var/log/consul.log &&\
        chown fluent:fluent /var/log/consul.log &&\
        chown fluent:fluent /usr/local/bin/consul

ADD     consul /etc/consul/conf.d

# Copy Start script to generate configuration dynamically
ADD     fluentd-alpine.start.sh   fluentd-alpine.start.sh
RUN     chown -R fluent:fluent fluentd-alpine.start.sh &&\
        chmod 777 fluentd-alpine.start.sh

COPY    fluent.conf /fluentd/etc/fluent.conf
COPY    plugins /fluentd/plugins

RUN echo "fluent ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER fluent

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
