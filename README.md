
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

## Requirements

The requirements is to have docker and docker-compose installed on your Linux server/machine.
Instructions to install docker are available [here](http://docs.docker.com/engine/installation/ubuntulinux/) and for docker-compose [here](https://docs.docker.com/compose/install/)

It's also available for [Mac](https://docs.docker.com/engine/installation/mac/) & [Windows](https://docs.docker.com/engine/installation/windows/)

## How to Install/Start

OpenNTI is available on [Docker Cloud](https://hub.docker.com/r/juniper/open-nti/) and this project provide scripts to easily download/start/stop it.  
```
git clone https://github.com/Juniper/open-nti.git
cd open-nti
./docker.start.sh
```
> On Ubuntu, you'll have to add "sudo" before the last command

By default it will start 3 containers and it's working in **non-persistent mode**, once you stop it all data are gone.  
It's possible to start the main container in **persistent mode** to save the database outside the container, by using the startup script ```docker.start.persistent.sh```. *Persistent mode on Mac OS requires at least v1.12*

### How to update

It's recommended to upgrade the project periodically, both the files from github.com and the containers from Docker Hub.
You can update easily with
```
./docker.update.sh
```

### Customize OpenNTI
#### Customize container's name and ports

All port numbers and names used by start/stop scripts are centralized in one file : [open-nti.params](open-nti.params), you can easily adapt this file with your own port numbers or names. It's mandatory if you are planning to run multiple instances of OpenNTI on the same server.

#### Customize the container itself

If you want to make some modifications, you can always build the container yourself using the script ```./docker.build.sh```.  
>The first time you run "./docker.build.sh", it will take 10-15min to download and compile everything but after that it will be very fast

## How to report feedback / participate in the project

For any issues please open an [issue on Github](https://github.com/Juniper/open-nti/issues).  
For comments, suggestions or questions please use our [google group](https://groups.google.com/forum/#!forum/open-nti)

To participate, please:
- Fork the project
- Send us a pull request

> if you are planning significant changes, please start a discussion first.

**Contributions are more than Welcome**

## How to use

Once the container is running, you can access :
- Graphical User Interface (Grafana) at http://hostip        (Login: admin / Pwd: admin)
- Database admin interface (Influxdb) at http://hostip:8083  (Login: juniper / Pwd: juniper)
- Database REST API (Influxdb) at http://hostip:8088         (Login: juniper / Pwd: juniper / db : juniper)

By default the *Data Streaming Collector* accept data on ports :
 - MX - JTI : **50000**
 - QFX5K - Analyticsd : **50020**

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
    username: '*login*'         (Single quote is to force to be imported as string)
    password: '*password*'      (Single quote is to force to be imported as string)
    method: password            (other supported methods 'key' and 'enc_key' for ssh Key-Based Authentication)
    key_file: ./data/*key_file* (optional: only appies if method key or enc_key is used, it must be located at data directory)
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
 - Analyticsd (qfx5k) streams in JSON/UDP on port **UDP/50020**
 - Juniper Telemetry Interface (MX/PTX) streams in GPB/UDP on port **UDP/50000**

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
By default dashboards are configured to display some "events" that are stored in the database into the serie "events"
Their are multiple ways to record entry in the events serie

## Insert events via syslog

open-nti will access events in the syslog format on port **UDP/6000**.  
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
> any system that knows how to generate a HTTP POST request can inject an event.  
> its very utile if you have a script/tool that run some tests to keep track of when major events happen

## How to change the default dashboard

Any Grafana dashboard copied into the dashboards/ directory will be automatically loaded when the container startup
If you want to replace the default dashboard, you can replace the existing .json file in the dashboards/ directory and rebuild the container with ./build script

## How to troubleshoot

To check if containers are running, execute the following command. By default you should have 3 containers running
```
docker ps
```

To force containers to stop, execute
```
./docker.stop.sh
```

To access the CLI of the main container for debug,  
Start a SSH session using the insecure_key provided in the repo and the script "docker.cli.sh"
```
chmod 600 insecure_key
./docker.cli.sh
```

For the Input containers named __open-nti-input-*__ you can access the logs directly from docker by running :
```
docker logs <container name or ID>
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
