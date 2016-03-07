
# open-nti

open-nti is a container packaged with all tools needed to collect and visualize time series data from network devices.
Data can be collected from different sources:

- **Data Collection Agent** : Collect data on devices using CLI/Shell or Netconf
- **Data Streaming Collector** : Take all data streamed by Juniper devices as Input (Jvision, Analyticsd, network agent)
- **Statsd interface** : Accept any Statsd packets

It's pre-configured with all tools and with a default dashboard ..
**Send it data, it will graph it**

Thanks to docker, it can run pretty much anywhere on server, on laptop ... on the device itself

More detailed description of a project can be found here (including a series of videos on how to use it):
http://forums.juniper.net/t5/Analytics/Open-Source-Universal-Telemetry-Collector-for-Junos/ba-p/288677

## Requirements

The only requirement is to have docker installed on your Linux server/machine
Instructions to install docker are available [here](http://docs.docker.com/engine/installation/ubuntulinux/)

It's also available for [Mac](https://docs.docker.com/engine/installation/mac/) & [Windows](https://docs.docker.com/engine/installation/windows/)

## How to Install

```
git clone https://github.com/Juniper/open-nti.git
cd open-nti
./docker.build.sh
./docker.start.sh
```
> On Ubuntu, you'll have to add "sudo" before the last 2 commands

By default the container is named "open-nti_con"  
>The first time you run "./docker.build.sh", it will take 10-15min to download and compile everything but after that it will be very fast

## How to report feedback / participate in the project

For any issues please open an [issue on Github](issues)
For comments, suggestions or questions please use our [google group](https://groups.google.com/forum/#!forum/open-nti)

To participate, please:
```
- Fork the project
- Send us a pull request
```
**Contributions are more than Welcome**

## How to use

Once the container is running, you can access :
- Graphical User Interface (Grafana) at http://hostip        (Login: admin / Pwd: admin)
- Database admin interface (Influxdb) at http://hostip:8083  (Login: juniper / Pwd: juniper)
- Database REST API (Influxdb) at http://hostip:8088         (Login: juniper / Pwd: juniper / db : juniper)

By default the *Data Streaming Collector* accept data on ports :
 - MX - Jvision : **50000**
 - QFX10K - Network Agent : **50010**
 - QFX5K - Analyticsd : **50020**

>**MAC OSX users**: If you want to run this container directly on MAC OSX you will need to install NAT rules to >forward ports from OSX to Docker VM.  
>There is a script which will add/delete rules automatically based on container name:   >https://github.com/mpergament/docker-virtualbox-nat-macosx

To use the *Data Collection Agent* you need to provide few informations

> For now, there are 2 dashboards predefined, one for the Data Collection Agent and one for the Data Streaming > Collector. in the future, these will be merged into a single dashboard.

# Data Collection Agent

### Configuration

**data/hosts.yaml**

In data/hosts.yaml you need to provide the list of devices you want to pull information from
For each device, you need to indicate the name ane one or multiple *tags* (at least one).  
Tags will be used later to know which credentials should be used for this device and which commands need to be executed
```yaml
<hostA>: <tag1> <tag4>
<hostB>: <tag1> <tag4>
<hostC>: <tag2> <tag4> <tag5>
<hostD>: <tag1> <tag4>  <--- Those tags relate the Hosts with the credentials and the commands to use with
```
Example
```yaml
mx-edge011: edge mx madrid bgp mpls
mx-agg011: agg mx madrid bgp isis
qfx-agg022: agg qfx munich bgp
qfx5100-02: tor qfx madrid isis
```

> The default configuration assume that hosts defined in hosts.yaml can be resolved with DNS
> if your hosts doesn't have DNS entry, it's possible to indicate the IP address in the hosts.yaml file instead of the name
> ```
> 192.168.0.1: edge mx madrid bgp mpls
> ```
> To avoid using Ip addresses in the dashboard, you can use the device hostname defined in the configuration instead of the value define in hosts.yaml by setting the parameter **use_hostname** to true in __open-nti.variables.yaml__
> ```
> use_hostname: True
> ```

**data/credentials.yaml**

You need to provide at least one credential profile for your devices

```yaml
jdi_lab:
    username: *login*
    password: *password*
    tags: tag1 tag2
```

**data/commands.yaml**

```yaml
generic_commands:  <--- You can name the group as best fits you
   commands: |
      show version | display xml  <--- There is no limit on how many commands can be added into a group
      show isis statistics | display xml <-- Before adding a command, confirm that there is a related parser
      show system buffers
      show system statistics icmp | display xml
      show route summary | display xml
   tags: tag1 tag2
```

### Execution periodic

To collect data periodically with the __Data Collection Agent__, you need to setup a cron job inside the container.  
As part of the project, open-nti is providing some scripts to easily add/remove cron jobs __inside__ the container __from__ the host.

Scripts provided:
 - **open-nti-start-cron.sh**: Create a new cron job inside the container  
 - **open-nti-show-cron.sh**: Show all cron jobs configured inside the container
 - **open-nti-stop-cron.sh**: Delete a cron job inside the container for a specific tag  

To start cron job to execute commands specified above for specific tag every minute:
```
./open-nti-start-cron.sh 1m '--tag tag1'
```

To start cron job for more than one tag at the same time:
```
./open-nti-start-cron.sh 1m '--tag tag1 tag2'
```

To start cron job to execute commands specified above for specific tag every 5 minutes:
```
./open-nti-start-cron.sh 5m '--tag tag1'
```

To start cron job to execute commands specified above for specific tag every hour:
```
./open-nti-start-cron.sh 1h '--tag tag1'
```
To show all scheduled cron jobs:
```
./open-nti-show-cron.sh 'all'
```

To stop cron job for specific tag:
```
./open-nti-stop-cron.sh '--tag tag1'
```

> If you want to configure the cron job yourself, open-nti use this command:
> /usr/bin/python /opt/open-nti/open-nti.py -s --tag <tag>

# Data Streaming Collector

Currently the collector accept:
 - Network agent (qfx10k) streams in JSON/UDP on port **50010**
 - Analyticsd (qfx5k) streams in JSON/UDP on port **50020**
 - Juniper Telemetry Interface (mx) streams in GPB/UDP on port **50000**

> **it's important that all devices have the correct time defined**, it's recommended to configure NTP everywhere

# statsd interface

open-nti is using telegraf to support statsd  
Statsd is a popular tool to send metrics over the network, it has been designed by etsy
More information below :
 - https://github.com/etsy/statsd/blob/master/docs/metric_types.md
 - https://github.com/influxdata/telegraf/tree/master/plugins/inputs/statsd

Here is an example of how to insert statsd data into the Database
```
root@d3e82264a08b:/# echo "opennti,device=qfx5100,type=int.rx:100|g" | nc -w 1 -u 127.0.0.1 8125

opennti define the serie  
device=qfx5100,type=int.rx will be converted as tag1  
100 is the value  
g indicate gauge  
```

# Events

By default the dashboard is configured to display some "events" that are stored in the database into the serie "events"
Their are multiple ways to record entry in the events serie

> This feature is *still experimental*, some users observed delay between events and visualization in the dashboard
> if you are not seeing your event, try to increase the time windows.

## Insert events via syslog

open-nti will access events in the syslog format on port UDP 6000.  
The goal is not to send all syslog but only relevant information like Commit or Protocol Flaps

To send only one syslog at commit time you can use the configuration below
```
set system syslog host 192.168.99.100 any any
set system syslog host 192.168.99.100 match UI_COMMIT_COMPLETED
set system syslog host 192.168.99.100 port 6000
```

## Insert events in the database manually

It's possible to insert events with just a HTTP POST request to the database, here is an example using curl
```
curl -i -XPOST 'http://10.92.71.225:8086/write?db=juniper' --data-binary 'events,type=Error text="BGP Flap"'
curl -i -XPOST 'http://10.92.71.225:8086/write?db=juniper' --data-binary 'events,device=qfx5100-01,type=Commit text="Change applied"'

```

## How to run multiple instance of the same container on the same server

By default, only 1 container can run on the same server because of default parameters
In order to run multiple container on the same Server, you need to customize the script "docker.start.sh" to :
 - Change the container name
 - Change the external ports the container is listening to

Below an example of start command that will allow multiple container on the same server
```
docker run -d  \
    -p 150000:50000/udp -p 150010:50010/udp -p 150020:50020/udp \
    -p 18083:8083 -p 18086:8086 -p 8080:80 -p 13000:3000 \
    juniper/open-nti /sbin/my_init
```
In this case I added "1" to each ports number

## How to change the default dashboard

Any Grafana dashboard copied into the dashboards/ directory will be automatically loaded when the container startup
If you want to replace the default dashboard, you can replace the existing .json file in the dashboards/ directory and rebuild the container with ./build script

## How to troubleshoot

To check if the container is running, execute
```
docker ps | grep open-nti_con
```

To force the container to stop, execute
```
 docker stop open-nti_con
```

To access the CLI of the container for debug , there are multi option
1 - Start the container in debug mode, you'll be directly on the CLI
```
./docker.debug.sh
```

2 - Start a SSH session using the insecure_key provided in the repo and the script "docker.cli.sh"
```
chmod 600 insecure_key
./docker.cli.sh
```

Once in CLI mode, you can check fluentd log
If everything is all right, nothing would be print on this log.
```
tail -f /var/log/fluentd.log
```

## Tools used
 - fluentd
 - influxdb
 - telegraf
 - grafana
 - nginx
 - pyez

# Contributors
 - Damien Garros
 - Efrain Gonzalez
 - Michael Pergament
 - Pablo Sagrera Garcia
