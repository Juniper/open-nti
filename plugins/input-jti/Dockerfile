FROM psagrera/fluent-jti:1.2 

ENV FLUENTD_OPT=""

ADD     fluentd-alpine.start.sh   fluentd-alpine.start.sh
RUN     chmod 777 fluentd-alpine.start.sh

COPY fluent.conf  /fluentd
COPY    plugins   /fluentd/plugins

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
    KAFKA_COMPRESSION_CODEC=none \
    KAFKA_TOPIC=jnpr.jvision

CMD /fluentd-alpine.start.sh
