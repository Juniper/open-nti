#!/bin/sh
mkdir -p /opt/telegraf/config
opennti=$(cat /etc/hosts | grep "opennti " | cut -f1)
sed s/opennti/$opennti/g /source/telegraf.tmpl > /opt/telegraf/config/telegraf.conf
/usr/bin/telegraf --config /opt/telegraf/config/telegraf.conf 

while true; do echo "bla"; sleep 1; done