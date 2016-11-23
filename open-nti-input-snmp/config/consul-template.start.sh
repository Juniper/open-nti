#!/bin/bash

/usr/local/bin/consul-template  -consul consul:8500 \
                                -wait 2s:10s \
                                -template "/opt/telegraf/config/telegraf_base_config.tmpl:/opt/telegraf/config/telegraf_config/telegraf_base_config.conf:/usr/bin/telegraf -config-directory /opt/telegraf/config/telegraf_config" \
                                -pid-file /var/run/consul-template.pid \
                                -log-level debug 