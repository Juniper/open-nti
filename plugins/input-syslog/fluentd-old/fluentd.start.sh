#!/bin/sh
# `/sbin/setuser memcache` runs the given command as the user `memcache`.
# If you omit that part, the command will be run as root.

/usr/local/bin/envtpl --keep-template /root/fluent/fluent.conf.tpl -o /tmp/fluent.conf
/bin/bash -l -c "fluentd -c /tmp/fluent.conf -vv" >> /var/log/fluentd.log 2>&1
