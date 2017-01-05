#!/bin/sh

/usr/local/bin/consul agent -config-dir /etc/consul/conf.d >>/var/log/consul.log 2>&1 &

/usr/local/bin/consul-template  -consul consul:8500 \
                                -template "/source/nginx.conf.tpl:/etc/nginx/nginx.conf" \
                                -exec '/usr/sbin/nginx -g "daemon off;"' \
                                -log-level DEBUG
