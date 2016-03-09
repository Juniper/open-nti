from docker import Client
import influxdb
import time
import docker.tls as tls
from os import path
import os
import pprint
import subprocess
import json
import sys, getopt, argparse, os.path, math
from sys import platform as _platform
import time

pp = pprint.PrettyPrinter(indent=4)

############################################
### Variables initialization
#############################################
## Image and container
IMAGE_NAME = 'juniper/open-nti'
CONTAINER_NAME = 'open-nti_test'
DATABASE_NAME = 'juniper'
## Local ports that will be redirected to the Open NTI
## Startup will fail if some ports are already in use
TEST_PORT_JTI = 40000
TEST_PORT_NA = 40010
TEST_PORT_ANALYTICSD = 40020
TEST_PORT_STATSD = 48125
TEST_PORT_EVENT = 46000
TEST_PORT_GRAFANA = 43000
TEST_PORT_INFLUXDB = 48083
TEST_PORT_INFLUXDB_API = 48086

## Local directories that will be mapped into the container
CURRENT_DIR=os.getcwd()
LOCAL_DIR_DATA = CURRENT_DIR + '/data'
LOCAL_DIR_LOG = CURRENT_DIR + '/logs'
LOCAL_DIR_DB = CURRENT_DIR + '/db'
LOCAL_DIR_TESTS = CURRENT_DIR + '/tests'
LOCAL_DIR_DASHBOARD = CURRENT_DIR + '/dashboards'

DOCKER_IP = '127.0.0.1'
CONTAINER_ID = ''
HANDLE_DB = ''

#############################################
def get_handle_db():
    global HANDLE_DB

    if HANDLE_DB == '':
        HANDLE_DB = influxdb.InfluxDBClient(
            host=DOCKER_IP, port=TEST_PORT_INFLUXDB_API, database=DATABASE_NAME, username="juniper",
            password="juniper"
        )

    return HANDLE_DB

#############################################
class StreamLineBuildGenerator(object):
    def __init__(self, json_data):
        self.__dict__ = json.loads(json_data)

# def setup_function(function):
#     print('\nsetup_function()')

def test_connect_docker():
    global c
    global DOCKER_IP

    ## initialize Docker Object
    if _platform == "linux" or _platform == "linux2":
        # linux
        c = Client(base_url='unix://var/run/docker.sock', version='1.20')
    elif _platform == "darwin":
        # MAC OS X
        dockerout = subprocess.check_output(
            ['/usr/local/bin/docker-machine ip default'],
            shell=True, stderr=subprocess.STDOUT
        )

        DOCKER_IP = dockerout.splitlines()[0]

        CERTS = path.join(
            path.expanduser('~'), '.docker', 'machine',
            'machines', 'default'
        )

        tls_config = tls.TLSConfig(
            client_cert=(
                path.join(CERTS, 'cert.pem'), path.join(CERTS, 'key.pem')
            ),
            ca_cert=path.join(CERTS, 'ca.pem'),
            assert_hostname=False,
            verify=True
        )

        url = "https://" + DOCKER_IP + ":2376"
        c = Client(base_url=url, tls=tls_config)

    elif _platform == "win32":
        exit

    ## Check if connection to Docker work by listing all images
    list_images = c.images()
    assert len(list_images) >= 1

def test_start_container():
    global CONTAINER_ID

    ## Force Stop and delete existing container if exist
    try:
        old_container_id = c.inspect_container(CONTAINER_NAME)['Id']

        c.stop(container=old_container_id)
        c.remove_container(container=old_container_id)
    except:
        print "Container do not exit"

    ## Create new container
    container = c.create_container(
        image=IMAGE_NAME,
        command='/sbin/my_init',
        name=CONTAINER_NAME,
        detach=True,
        ports=[
            (8125, 'udp'),
            (6000, 'udp'),
            (50000, 'udp'),
            (50010, 'udp'),
            (50020, 'udp'),
            3000,
            8083,
            8086
        ],
        volumes=[
            '/opt/open-nti/data',
            '/src/dashboards',
            '/opt/open-nti/tests'
        ],
        host_config=c.create_host_config(
            port_bindings={
                '8125/udp': TEST_PORT_STATSD,
                '6000/udp': TEST_PORT_EVENT,
                '50000/udp': TEST_PORT_JTI,
                '50010/udp': TEST_PORT_NA,
                '50020/udp': TEST_PORT_ANALYTICSD,
                3000: TEST_PORT_GRAFANA,
                8083: TEST_PORT_INFLUXDB,
                8086: TEST_PORT_INFLUXDB_API
            },
            binds=[
                LOCAL_DIR_DATA + ':/opt/open-nti/data',
                LOCAL_DIR_DASHBOARD + ':/src/dashboards',
                LOCAL_DIR_TESTS + ':/opt/open-nti/tests',
            ]
        )
    )

    c.start(container)

    CONTAINER_ID = c.inspect_container(CONTAINER_NAME)['Id']

    ## Wait few sec for the container to start
    time.sleep(10)

    assert c.inspect_container(CONTAINER_NAME)["State"]["Running"]

def test_influxdb_running_database_exist():
    # global db
    # Verify we can connect to InfluxDB and DB with a name juniper exists

    ##
    # db = influxdb.InfluxDBClient(
    #     host=DOCKER_IP, port=TEST_PORT_INFLUXDB_API, database=DATABASE_NAME, username="juniper",
    #     password="juniper"
    # )

    db = get_handle_db()

    db_list = db.get_list_database()
    found_db = 0
    for db_entry in db_list:
        if db_entry['name'] == DATABASE_NAME:
            found_db = 1
        else:
            continue

    if found_db:
        assert 1
    else:
        assert 0

def test_collection_agent_01():
    # Write datapoint using mocked Junos device
    global db

    exec_job_id = c.exec_create(
        container=CONTAINER_ID,
        cmd='/usr/bin/python /opt/open-nti/open-nti.py  -s -t --tag test'
    )

    result = c.exec_start(exec_job_id, stream=True)
    for line in result:
        try:
            stream_line = StreamLineBuildGenerator(line)
            # Do something with your stream line
            # ...
        except ValueError:
            # If we are not able to deserialize the received line as JSON object, just print it out
            print(line)
            continue

    db = get_handle_db()

    # db = influxdb.InfluxDBClient(
    #     host=DOCKER_IP, port=TEST_PORT_INFLUXDB_API, database=DATABASE_NAME, username="juniper",
    #     password="juniper"
    # )

    time.sleep(5)
    query = 'select mean(value) from /P1-tf-mx960-1-re0.route-table.summary.inet.0.actives/;'
    result = db.query(query)
    points = list(result.get_points())

    assert len(points) == 1 and points[0]['mean'] == 16

def teardown_module(module):
    global c
    global CONTAINER_ID

    c.stop(container=CONTAINER_ID)
    c.remove_container(container=CONTAINER_ID)
