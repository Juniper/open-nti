#!/bin/sh
alias load_yaml='/usr/bin/python load_consul.py --dir=/opt/open-nti/data >> /var/log/load_consul.log 2>&1'
cd /opt/load_consul
load_yaml; fswatch -o /opt/open-nti/data | while read f; do load_yaml; done ; done
