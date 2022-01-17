![Beta](https://img.shields.io/badge/status-beta-yellowgreen.svg?style=flat "Beta")
![Community](https://img.shields.io/badge/support-community-blue.svg?style=flat "Community")

All the credit goes to: https://github.com/Juniper/open-nti 
More detailed description of a project can be found [here](http://forums.juniper.net/t5/Analytics/Open-Source-Universal-Telemetry-Collector-for-Junos/ba-p/288677) (including a series of videos on how to use it):

## Enhancement
- Add EVO OS support for Juniper routers
    - in ./data/commands.yaml, add the support:
        top -b -n 1 | shell re  #run top command at RE node, support EVO only 
        top -bn 1 | shell fpc0 #run top command at FPC node. fpc slot has to be specified, support EVO only
- Add dashboard to monitor router healthy status, per chassis level and per process level

 
## Tools used
 - fluentd
 - influxdb
 - telegraf
 - grafana
 - nginx
 - pyez
