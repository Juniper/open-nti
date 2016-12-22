from docker import Client
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

pp = pprint.PrettyPrinter(indent=4)

############################################
# Variables initialization
#############################################
# Image and container
IMAGE_NAME = 'juniper/open-nti-input-jti'
CONTAINER_NAME = 'open-nti-input-jti_test'
TCP_RELAY_CONTAINER_NAME = 'tcpreplay_test'

TIMER_AFTER_TRAFFIC=1

if os.getenv('TRAVIS'):
  TIMER_AFTER_TRAFFIC=3

# Local ports that will be redirected to the Open NTI
# Startup will fail if some ports are already in use
TEST_PORT_JTI = 40000
TEST_PORT_ANALYTICSD = 40020

# Local directories that will be mapped into the container
CURRENT_DIR = os.getcwd()
TESTS_DIR   = CURRENT_DIR + "/tests"
TESTS_FIXTURES_DIR = TESTS_DIR + "/fixtures"

DOCKER_IP = '127.0.0.1'
CONTAINER_ID = ''
c = ''

## Open NTI container related information
OPENNTI_CID = ''
OPENNTI_IMAGE_NAME = "juniper/open-nti"
OPENNTI_C_NAME = "open-nti-input-jti_test_influxdb"
OPENNTI_API_PORT = 18086
OPENNTI_INFLUX_PORT = 18083
OPENNTI_DATABASE_NAME = "juniper"
OPENNTI_IP = '127.0.0.1'
OPENNTI_INTERNAL_IP = ''

TCP_REPLAY_CONTAINER_ID = ''
INFLUXDB_HANDLE = ''

#############################################
class StreamLineBuildGenerator(object):
    def __init__(self, json_data):
        self.__dict__ = json.loads(json_data)

#############################################
# Containers management
#############################################

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

def start_fluentd(output_kafka='false', output_influx='false'):
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
            "PORT_JTI=40000",
            "PORT_ANALYTICSD=40020",
            "INFLUXDB_PORT="+str(8086),
            "INFLUXDB_DB="+str(OPENNTI_DATABASE_NAME),
            "INFLUXDB_USER=juniper",
            "INFLUXDB_PWD=juniper",
            "INFLUXDB_ADDR="+OPENNTI_INTERNAL_IP,
            "INFLUXDB_FLUSH_INTERVAL=1",
            "OUTPUT_KAFKA="+output_kafka,
            "OUTPUT_INFLUXDB="+output_influx,
            "OUTPUT_STDOUT=true"
        ],
        ports=[
            (40000, 'udp'),
            (40020, 'udp'),
        ],
        host_config=c.create_host_config(
            port_bindings={
                '40000/udp': TEST_PORT_JTI,
                '40020/udp': TEST_PORT_ANALYTICSD,
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
        command='/usr/bin/tcpreplay --intf1=eth0 /data/' + file_name,
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

################################################################################
################################################################################

def test_connect_docker():
    global c
    global DOCKER_IP

    # initialize Docker Object
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
        # linux
        c = Client(base_url='unix://var/run/docker.sock', version='1.20')
    # elif _platform == "darwin":
    #     # MAC OS X
    #     dockerout = subprocess.check_output(
    #         ['/usr/local/bin/docker-machine ip default'],
    #         shell=True, stderr=subprocess.STDOUT
    #     )
    #
    #     DOCKER_IP = dockerout.splitlines()[0]
    #
    #     CERTS = path.join(
    #         path.expanduser('~'), '.docker', 'machine',
    #         'machines', 'default'
    #     )
    #
    #     tls_config = tls.TLSConfig(
    #         client_cert=(
    #             path.join(CERTS, 'cert.pem'), path.join(CERTS, 'key.pem')
    #         ),
    #         ca_cert=path.join(CERTS, 'ca.pem'),
    #         assert_hostname=False,
    #         verify=True
    #     )
    #
    #     url = "https://" + DOCKER_IP + ":2376"
    #     c = Client(base_url=url, tls=tls_config, version='1.20')

    elif _platform == "win32":
        exit

    # Check if connection to Docker work by listing all images
    list_images = c.images()
    assert len(list_images) >= 1

def test_start_dependancies():

    start_open_nti()
    assert check_influxdb_running_database_exist()

def test_jti_structured_ifd_01():

    FNAME       = sys._getframe().f_code.co_name
    PCAP_FILE   = FNAME + "/jti.pcap"

    start_fluentd(output_influx='true')
    replay_file(PCAP_FILE)

    time.sleep(3)

    db = get_influxdb_handle()
    query = 'SELECT * FROM "jnpr.jvision"'
    result = db.query(query)
    points = result.get_points()
    print result
    print points
    assert len(list(points)) == 112

# def test_analyticsd_structured_ifd_01():
#     CONFIG_FILE = 'fluent_structured.conf'
#
#     FNAME       = sys._getframe().f_code.co_name
#     OUTPUT_FILE = FNAME + ".json"
#     PCAP_FILE   = FNAME + "/analyticsd_ifd.pcap"
#
#     start_fluentd(CONFIG_FILE, OUTPUT_FILE)
#     replay_file(PCAP_FILE)
#
#     time.sleep(TIMER_AFTER_TRAFFIC)
#
#     test_results = filecmp.cmp(
#         TESTS_FIXTURES_DIR + '/' + FNAME +  '/' + OUTPUT_FILE,
#         TESTS_OUTPUT_DIR + '/' + OUTPUT_FILE,
#         shallow=False)
#
#     if not test_results:
#         with open(TESTS_OUTPUT_DIR + '/' + OUTPUT_FILE, 'r') as fin:
#             print fin.read()
#
#     assert test_results
#
# def test_analyticsd_structured_queue_01():
#     CONFIG_FILE = 'fluent_structured.conf'
#
#     FNAME       = sys._getframe().f_code.co_name
#     OUTPUT_FILE = FNAME + ".json"
#     PCAP_FILE   = FNAME + "/analyticsd_queue.pcap"
#
#     start_fluentd(CONFIG_FILE, OUTPUT_FILE)
#     replay_file(PCAP_FILE)
#
#     time.sleep(TIMER_AFTER_TRAFFIC)
#
#     test_results = filecmp.cmp(
#         TESTS_FIXTURES_DIR + '/' + FNAME +  '/' + OUTPUT_FILE,
#         TESTS_OUTPUT_DIR + '/' + OUTPUT_FILE,
#         shallow=False)
#
#
#
#     if not test_results:
#         with open(TESTS_OUTPUT_DIR + '/' + OUTPUT_FILE, 'r') as fin:
#             print fin.read()
#
#     assert test_results

def teardown_module(module):
    global c

    if not os.getenv('TRAVIS'):
        stop_fluentd()
        stop_open_nti()

        try:
            old_container_id = c.inspect_container(TCP_RELAY_CONTAINER_NAME)['Id']
            c.stop(container=old_container_id)
            c.remove_container(container=old_container_id)
        except:
            print "Container do not exit"
