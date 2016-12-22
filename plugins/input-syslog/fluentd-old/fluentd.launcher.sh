#!/bin/sh
# `/sbin/setuser memcache` runs the given command as the user `memcache`.
# If you omit that part, the command will be run as root.
# fluentd -c /fluent/fluent.conf -vv

exec /root/fluentd.start.sh >> /var/log/fluentd.log 2>&1
