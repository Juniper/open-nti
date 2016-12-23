#!/bin/sh
alias load_yaml='/usr/bin/python load_consul.py --dir=/opt/open-nti/data'
cd /opt/consul
load_yaml; fswatch -o /opt/open-nti/data | while read f; do load_yaml; done ; done >> /var/log/load_consul.log
