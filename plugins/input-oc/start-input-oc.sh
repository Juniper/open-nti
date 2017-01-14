#!/bin/sh

/usr/local/bin/consul agent -config-dir /etc/consul/conf.d >>/var/log/consul.log 2>&1 &

/usr/local/bin/consul-template  -consul consul:8500 \
                                -template "/source/telegraf.toml:/opt/telegraf/config/telegraf.conf" \
                                -exec "/go/bin/telegraf --config /opt/telegraf/config/telegraf.conf" \
                                -log-level INFO
