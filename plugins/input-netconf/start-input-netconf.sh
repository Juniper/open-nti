#!/bin/sh

/usr/local/bin/consul agent -config-dir /etc/consul/conf.d >>/var/log/consul.log 2>&1 &

/usr/local/bin/consul-template  -consul consul:8500 \
                                -template "/data/templates/telegraf.tmpl:/opt/telegraf/config/telegraf.conf" \
                                -template "/data/templates/commands.tmpl:/source/commands.yaml" \
                                -template "/data/templates/credentials.tmpl:/source/credentials.yaml" \
                                -exec "/usr/bin/telegraf --config /opt/telegraf/config/telegraf.conf" \
                                -log-level INFO
