![status beta](https://img.shields.io/badge/status-beta-yellow.svg)  
# open-nti-input-syslog
Standalone container running fluentd to parse syslog

This container has been designed to work with the project OpenNTI but it can fit for other projects as well.  
Multiple type of output are supported and can be defined at launch time:
- Influxdb
- Kafka
- MQTT (not yet)
- Stdout

This container can run in standalone mode or it can you can run multiple behind a load-balancer using docker-compose.
_A docker-compose configuration file is (not yet) provided._

## Environment variables

So parameters can be overwritten using environment variables define at launch time.   
Here is the list of variables available with their default value.

```yaml

  # Define type of output
  OUTPUT_KAFKA: false
  OUTPUT_INFLUXDB: false
  OUTPUT_MQTT: false
  OUTPUT_STDOUT: false

  # Input port
  PORT_SYSLOG: 6000

  # parameter for Influxdb
  INFLUXDB_ADDR: localhost
  INFLUXDB_PORT: 8086
  INFLUXDB_DB: juniper
  INFLUXDB_USER: juniper
  INFLUXDB_PWD: juniper
  INFLUXDB_FLUSH_INTERVAL: 2

  # parameter for Kafka
  KAFKA_ADDR: localhost
  KAFKA_PORT: 9092
  KAFKA_DATA_TYPE: json
  KAFKA_TOPIC: events
```
> For latest list of environment variables please refer to Dockerfile

Here is an example to define an environment variable
```
docker run -d -e INFLUXDB_ADDR: 'localhost' -i juniper/open-nti-input-syslog
```

## Build and Tests

The project include few tests to ensure that everything is working as expected
You can run all tests with
```
pip install -r requirements.txt
python -m pytest -v
```
>To run these tests additional containers will be downloaded

In addition, all tests are executed on Travis after each commit.

Inside the test directory there are some packet captures that can be use to generate traffic
You can play them using tcpreplay.
```
cd tests/fixtures/test_syslog_qfx_01
docker run --rm -t -v $(pwd):/data -i dgarros/tcpreplay /usr/bin/tcpreplay --pps=10 --intf1=eth0 syslog_qfx_01_16000.pcap
```
