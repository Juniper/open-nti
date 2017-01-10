#!/bin/sh
# `/sbin/setuser memcache` runs the given command as the user `memcache`.
# If you omit that part, the command will be run as root.

telegraf --config /home/fluent/telegraf.toml >>/var/log/telegraf-monitoring.log 2>&1 &

envtpl --keep-template /fluentd/etc/fluent.conf -o /tmp/fluent.conf

fluentd -c /tmp/fluent.conf -p /fluentd/plugins $FLUENTD_OPT
