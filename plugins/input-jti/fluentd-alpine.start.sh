#!/bin/sh
# `/sbin/setuser memcache` runs the given command as the user `memcache`.
# If you omit that part, the command will be run as root.

envtpl --keep-template /fluentd/fluent.conf -o /tmp/fluent.conf

fluentd -c /tmp/fluent.conf -p /fluentd/plugins $FLUENTD_OPT
