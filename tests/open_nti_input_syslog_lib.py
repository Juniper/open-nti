from docker import Client
from kafka import KafkaConsumer
import docker.tls as tls
import influxdb
import time
from os import path
import os
import shutil
import pprint
import subprocess
import json
import os.path
from sys import platform as _platform
import time
import requests
import filecmp
import sys
import socket
from timeout import timeout

pp = pprint.PrettyPrinter(indent=4)

############################################
# Variables initialization
#############################################
# Image and container
IMAGE_NAME = 'juniper/open-nti-input-syslog:unittest'
CONTAINER_NAME = 'open-nti-input-syslog_test'
TCP_RELAY_CONTAINER_NAME = 'tcpreplay_test'

TIMER_AFTER_TRAFFIC=1

if os.getenv('TRAVIS'):
  TIMER_AFTER_TRAFFIC=3

# Local ports that will be redirected to the Open NTI
# Startup will fail if some ports are already in use
TEST_PORT_SYSLOG = 16000

# Local directories that will be mapped into the container
CURRENT_DIR = os.getcwd()
TESTS_DIR   = CURRENT_DIR + "/tests/input-syslog"
TESTS_FIXTURES_DIR = TESTS_DIR + "/fixtures"

DOCKER_IP = '127.0.0.1'
CONTAINER_ID = ''
c = ''

EXTERNAL_IP = ''

## Open NTI container related information
OPENNTI_CID = ''
OPENNTI_IMAGE_NAME = "juniper/open-nti:unittest"
OPENNTI_C_NAME = "open-nti-input-syslog_test_influxdb"
OPENNTI_API_PORT = 18086
OPENNTI_INFLUX_PORT = 18083
OPENNTI_DATABASE_NAME = "juniper"
OPENNTI_IP = '127.0.0.1'
OPENNTI_INTERNAL_IP = ''

## Kafka container related information
KAFKA_CID = ''
KAFKA_IMAGE_NAME = "spotify/kafka"
KAFKA_C_NAME = "open-nti-input-syslog_test_kafka"
KAFKA_API_PORT = 12181
KAFKA_BROKER_PORT = 19092
KAFKA_IP = '127.0.0.1'
KAFKA_INTERNAL_IP = ''

#docker run -p 2181:2181 -p 9092:9092 --env ADVERTISED_HOST=`boot2docker ip` --env ADVERTISED_PORT=9092 spotify/kafka

TCP_REPLAY_CONTAINER_ID = ''
INFLUXDB_HANDLE = ''

#############################################
class StreamLineBuildGenerator(object):
    def __init__(self, json_data):
        self.__dict__ = json.loads(json_data)

def check_docker():
    global c
    # initialize Docker Object
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
        # linux
        c = Client(base_url='unix://var/run/docker.sock', version='1.20')
    elif _platform == "win32":
        exit

    return c

def start_open_nti():
    global c
    global OPENNTI_CID
    global OPENNTI_INTERNAL_IP

    # Force Stop and delete existing container if exist
    try:
        old_container_id = c.inspect_container(OPENNTI_C_NAME)['Id']

        c.stop(container=old_container_id)
        c.remove_container(container=old_container_id)
    except:
        print "Container do not exit"

    container = c.create_container(
        image=OPENNTI_IMAGE_NAME,
        command='/sbin/my_init',
        name=OPENNTI_C_NAME,
        detach=True,
        ports=[
            3000,
            8083,
            8086
        ],
        host_config=c.create_host_config(
            port_bindings={
                '8086': OPENNTI_API_PORT,
                '8083': OPENNTI_INFLUX_PORT,
            },
            binds=[
                CURRENT_DIR + ':/root/fluent',
            ]
        )
    )

    c.start(container)
    OPENNTI_CID = c.inspect_container(OPENNTI_C_NAME)['Id']
    OPENNTI_INTERNAL_IP = c.inspect_container(OPENNTI_C_NAME)['NetworkSettings']['IPAddress']

    # Wait few sec for the container to start
    time.sleep(5)
    return OPENNTI_CID

def stop_open_nti():
    global c
    # Force Stop and delete existing container if exist
    try:
        old_container_id = c.inspect_container(OPENNTI_C_NAME)['Id']
        c.stop(container=old_container_id)
        c.remove_container(container=old_container_id)
    except:
        print "Container do not exit"

def get_influxdb_handle():
    global INFLUXDB_HANDLE

    if INFLUXDB_HANDLE == '':
        INFLUXDB_HANDLE = influxdb.InfluxDBClient(
            host=OPENNTI_IP,
            port=OPENNTI_API_PORT,
            database=OPENNTI_DATABASE_NAME,
            username="juniper",
            password="juniper"
        )

    return INFLUXDB_HANDLE

def get_external_ip():
    return [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

def start_kafka():
    global c
    global KAFKA_CID
    global KAFKA_INTERNAL_IP
    global KAFKA_BROKER_PORT
    global KAFKA_API_PORT

    # Force Stop and delete existing container if exist
    try:
        old_container_id = c.inspect_container(KAFKA_C_NAME)['Id']

        c.stop(container=old_container_id)
        c.remove_container(container=old_container_id)
    except:
        print "Container do not exit"

    container = c.create_container(
        image=KAFKA_IMAGE_NAME,
        name=KAFKA_C_NAME,
        detach=True,
        environment=[
            "ADVERTISED_PORT="+str(KAFKA_BROKER_PORT),
            "ADVERTISED_HOST="+str(get_external_ip())
        ],
        ports=[
            2181,
            9092
        ],
        host_config=c.create_host_config(
            port_bindings={
                '2181': KAFKA_API_PORT,
                '9092': KAFKA_BROKER_PORT,
            }
        )
    )

    c.start(container)
    KAFKA_CID = c.inspect_container(KAFKA_C_NAME)['Id']
    KAFKA_INTERNAL_IP = c.inspect_container(KAFKA_C_NAME)['NetworkSettings']['IPAddress']

    # Wait few sec for the container to start
    time.sleep(5)
    return KAFKA_CID

def stop_kafka():
    global c
    # Force Stop and delete existing container if exist
    try:
        old_container_id = c.inspect_container(KAFKA_C_NAME)['Id']
        c.stop(container=old_container_id)
        c.remove_container(container=old_container_id)
    except:
        print "Container do not exit"

@timeout(5)
def check_kafka_msg(topic='events', nbr_msg=100):

    ## Collect Messages from Bus
    consumer = KafkaConsumer(
        bootstrap_servers=get_external_ip()+':'+str(KAFKA_BROKER_PORT),
        auto_offset_reset='earliest')

    consumer.subscribe([topic])

    counter = 0
    for message in consumer:
        counter = counter + 1
        if counter == nbr_msg:
            break

    return counter

def check_influxdb_running_database_exist():
    # Verify we can connect to InfluxDB and DB with a name juniper exists

    db = get_influxdb_handle()

    db_list = db.get_list_database()
    found_db = 0
    for db_entry in db_list:
        if db_entry['name'] == OPENNTI_DATABASE_NAME:
            found_db = 1
        else:
            continue

    return found_db

def check_kafka_is_running():
    # Verify we can connect to InfluxDB and DB with a name juniper exists

    consumer = KafkaConsumer(bootstrap_servers=get_external_ip()+':'+str(KAFKA_BROKER_PORT),
                             auto_offset_reset='earliest')

    mytopic = consumer.topics()

    return 1

def start_fluentd_syslog(output_kafka='false', output_influx='false'):
    global c
    global CONTAINER_ID

    # Force Stop and delete existing container if exist
    try:
        old_container_id = c.inspect_container(CONTAINER_NAME)['Id']

        c.stop(container=old_container_id)
        c.remove_container(container=old_container_id)
    except:
        print "Container do not exit"

    container = c.create_container(
        image=IMAGE_NAME,
        name=CONTAINER_NAME,
        detach=True,
        environment=[
            "PORT_SYSLOG=16000",
            "INFLUXDB_PORT="+str(8086),
            "INFLUXDB_DB="+str(OPENNTI_DATABASE_NAME),
            "INFLUXDB_USER=juniper",
            "INFLUXDB_PWD=juniper",
            "INFLUXDB_ADDR="+OPENNTI_INTERNAL_IP,
            "INFLUXDB_FLUSH_INTERVAL=1",
            "KAFKA_ADDR="+str(get_external_ip()),
            "KAFKA_PORT="+str(KAFKA_BROKER_PORT),
            "KAFKA_TOPIC=events",
            "OUTPUT_KAFKA="+output_kafka,
            "OUTPUT_INFLUXDB="+output_influx,
            "OUTPUT_STDOUT=true"
        ],
        ports=[
            (16000, 'udp'),
        ],
        host_config=c.create_host_config(
            port_bindings={
                '16000/udp': TEST_PORT_SYSLOG,
            }
        )
    )
    c.start(container)

    time.sleep(1)
    CONTAINER_ID = c.inspect_container(CONTAINER_NAME)['Id']
    return CONTAINER_ID

def stop_fluentd():
    global c

    # Force Stop and delete existing container if exist
    try:
        old_container_id = c.inspect_container(CONTAINER_NAME)['Id']
        c.stop(container=old_container_id)
        c.remove_container(container=old_container_id)
    except:
        print "Container do not exit"

def replay_file(file_name):
    global c

    try:
        old_container_id = c.inspect_container(TCP_RELAY_CONTAINER_NAME)['Id']
        c.stop(container=old_container_id)
        c.remove_container(container=old_container_id)
    except:
        print "Container do not exit"

    container = c.create_container(
        image='dgarros/tcpreplay',
        command='/usr/bin/tcpreplay --pps=100 --intf1=eth0 /data/' + file_name,
        name=TCP_RELAY_CONTAINER_NAME,
        volumes=[
            '/data'
        ],
        host_config=c.create_host_config(
            binds=[
                TESTS_FIXTURES_DIR + ':/data',
            ]
        )
    )
    c.start(container)
