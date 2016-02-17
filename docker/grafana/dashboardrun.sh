#!/bin/sh
cd /src/dashboards
exec /sbin/setuser www-data /usr/bin/node /src/dashboard-loader/dashboard-loader.js -w . >>/var/log/dashboard.log 2>&1
