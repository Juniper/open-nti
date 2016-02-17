#!/bin/sh
cd /opt/grafana/
exec /sbin/setuser www-data /opt/grafana/bin/grafana-server >>/var/log/grafana.log 2>&1
