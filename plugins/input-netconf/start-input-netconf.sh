#!/bin/sh

/usr/local/bin/consul-template  -consul consul:8500 \
                                -template "/data/templates/telegraf.tmpl:/opt/telegraf/config/telegraf.conf" \
                                -template "/data/templates/commands.tmpl:/source/commands.yaml" \
                                -template "/data/templates/credentials.tmpl:/source/credentials.yaml" \
                                -log-level debug
