![Beta](https://img.shields.io/badge/status-beta-yellowgreen.svg?style=flat "Beta")
![Community](https://img.shields.io/badge/support-community-blue.svg?style=flat "Community")

# OpenNTI

OpenNTI is a container packaged with all tools needed to collect and visualize time series data from network devices.
Data can be collected from different sources:

- **Data Collection Agent** : Collect data on devices using CLI/Shell or Netconf
- **Data Streaming Collector** : Take all data streamed by Juniper devices as Input (JTI, Analyticsd, soon Openconfig with gRPC)
- **Statsd interface** : Accept any Statsd packets

It's pre-configured with all tools and with a default dashboard ..
**Send it data, it will graph it**

Thanks to docker, it can run pretty much anywhere on server, on laptop ... on the device itself

More detailed description of a project can be found [here](http://forums.juniper.net/t5/Analytics/Open-Source-Universal-Telemetry-Collector-for-Junos/ba-p/288677) (including a series of videos on how to use it):

# Requirements

The requirement is to have **docker** and **docker-compose** installed on your Linux server/machine.
Please check the [Install Guide](http://open-nti.readthedocs.io/en/latest/install.html)

# Documentation

The complete [documentation is available here](http://open-nti.readthedocs.io/en/latest/)

# Ask a question or Report an Issue ?

Please open an [issue on Github](https://github.com/Juniper/open-nti/issues) this is the fastest way to get an answer.

# Want to contribute ?

Contributions are more than welcome, small or big. We love to receive contributions for **Parsers** or **Dashboards** that you might have created.  
If you are planning a big change, please start a discussion first to make sure we'll be able to merge it.

# Contributors
 - Damien Garros
 - Efrain Gonzalez
 - Michael Pergament
 - Pablo Sagrera Garcia

## Tools used
 - fluentd
 - influxdb
 - telegraf
 - grafana
 - nginx
 - pyez
