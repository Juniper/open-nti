
Work In Progress

OpenNTI architecture is designed to be modular.
the main components are a Timeserie Database(influxdb) and a graphical interface (grafana)

Based on the need, containers can be added or removed to add functionalities.


Docker compose
==================

All containers are started using docker-compose.yaml

./docker.start.sh

You can create your own docker-compose file and pass it

./docker.start.sh <my docker compose file>

List of available Plugins
=============================

JTI

Event / Syslog




Input plugin container
- https://github.com/Juniper/open-nti-input-syslog
- https://github.com/Juniper/open-nti-input-jti
