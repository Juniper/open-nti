#!/bin/sh
# `/sbin/setuser memcache` runs the given command as the user `memcache`.
# If you omit that part, the command will be run as root.
exec /influxdbrun.sh >> /var/log/influxdb.log 2>&1
