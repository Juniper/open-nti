from docker import Client
import influxdb
import time
import docker.tls as tls
from os import path
import os
import pprint
import subprocess
import json
import os.path
from sys import platform as _platform
import time
import requests

pp = pprint.PrettyPrinter(indent=4)

############################################
# Variables initialization
#############################################
# Images and containers

OPENNTI_NAME = 'open-nti_test'
OPENNTI_IMAGE = 'juniper/open-nti:unittest'
OPENNTI_C = ''
OPENNTI_IP = ''

OPENNTI_IN_JTI_NAME = 'open-nti_in_jti_test'
OPENNTI_IN_JTI_IMAGE = 'juniper/open-nti-input-jti:unittest'
OPENNTI_IN_JTI_C = ''

OPENNTI_IN_LOG_NAME = 'open-nti_in_log_test'
OPENNTI_IN_LOG_IMAGE = 'juniper/open-nti-input-syslog:unittest'
OPENNTI_IN_LOG_C = ''

TCP_REPLAY_IMAGE = 'dgarros/tcpreplay'
TCP_REPLAY_C = ''
TCP_REPLAY_NAME = 'tcpreplay_test'

DATABASE_NAME = 'juniper'
GRAFANA_USER = 'admin'
GRAFANA_PASS = 'admin'

# Local ports that will be redirected to the Open NTI
# Startup will fail if some ports are already in use
TEST_PORT_JTI = 40000
TEST_PORT_ANALYTICSD = 40020
TEST_PORT_STATSD = 48125
TEST_PORT_EVENT = 46000
TEST_PORT_GRAFANA = 43000
TEST_PORT_INFLUXDB = 48083
TEST_PORT_INFLUXDB_API = 48086
INFLUXDB_PORT = 8086

# Local directories that will be mapped into the container
CURRENT_DIR = os.getcwd()
LOCAL_DIR_DATA = CURRENT_DIR + '/main/data'
LOCAL_DIR_LOG = CURRENT_DIR + '/main/logs'
LOCAL_DIR_DB = CURRENT_DIR + '/main/db'
LOCAL_DIR_TESTS = CURRENT_DIR + '/tests/main'
LOCAL_DIR_DASHBOARD = CURRENT_DIR + '/main/dashboards'

LOCAL_PCAP_DIR = LOCAL_DIR_TESTS + '/pcap'
LOCAL_GRAFANA_DIR = LOCAL_DIR_TESTS + '/grafana'
LOCAL_GRAFANA_FILE = LOCAL_GRAFANA_DIR + '/test.json'

DOCKER_IP = '127.0.0.1'

HANDLE_DB = ''

#############################################
def get_handle_db():
    global HANDLE_DB

    if HANDLE_DB == '':
        HANDLE_DB = influxdb.InfluxDBClient(
            host=DOCKER_IP,
            port=TEST_PORT_INFLUXDB_API,
            database=DATABASE_NAME,
            username="juniper",
            password="juniper"
        )

    return HANDLE_DB

#############################################
class StreamLineBuildGenerator(object):
    def __init__(self, json_data):
        self.__dict__ = json.loads(json_data)

def test_connect_docker():
    global c
    global DOCKER_IP

    # initialize Docker Object
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
        # linux
        c = Client(base_url='unix://var/run/docker.sock', version='1.20')

    elif _platform == "win32":
        exit

    # Check if connection to Docker work by listing all images
    list_images = c.images()
    assert len(list_images) >= 1

def test_start_opennti_container():
    global OPENNTI_C
    global OPENNTI_IP

    # Force Stop and delete existing container if exist
    try:
        old_container_id = c.inspect_container(OPENNTI_NAME)['Id']
        c.stop(container=old_container_id)
        c.remove_container(container=old_container_id)
    except:
        print "Container do not exit"

    # Create new  container
    container = c.create_container(
        image=OPENNTI_IMAGE,
        command='/sbin/my_init',
        name=OPENNTI_NAME,
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
    OPENNTI_C   = c.inspect_container(OPENNTI_NAME)['Id']
    OPENNTI_IP  = c.inspect_container(OPENNTI_NAME)['NetworkSettings']['IPAddress']

    # Wait few sec for the container to start
    time.sleep(10)

    assert c.inspect_container(OPENNTI_NAME)["State"]["Running"]

#def test_start_opennti_in_jti_container():
#    global OPENNTI_IN_JTI_C
#
#    # Force Stop and delete existing container if exist
#    try:
#        old_container_id = c.inspect_container(OPENNTI_IN_JTI_NAME)['Id']
#        c.stop(container=old_container_id)
#        c.remove_container(container=old_container_id)
#    except:
#        print "Container do not exit"
#
#    # Create new  container
#    container = c.create_container(
#        image=OPENNTI_IN_JTI_IMAGE,
#        name=OPENNTI_IN_JTI_NAME,
#        detach=True,
#        ports=[
#            (50000, 'udp'),
#            (50020, 'udp')
#        ],
#        environment=[
#            "PORT_JTI=50000",
#            "PORT_ANALYTICSD=50020",
#            "INFLUXDB_PORT="+str(INFLUXDB_PORT),
#            "INFLUXDB_DB="+str(DATABASE_NAME),
#            "INFLUXDB_USER=juniper",
#            "INFLUXDB_PWD=juniper",
#            "INFLUXDB_ADDR="+OPENNTI_IP,
#            "INFLUXDB_FLUSH_INTERVAL=1"
#            "OUTPUT_INFLUXDB=true",
#            "OUTPUT_STDOUT=true"
#        ],
#        host_config=c.create_host_config(
#            port_bindings={
#                '50000/udp': TEST_PORT_JTI,
#                '50020/udp': TEST_PORT_ANALYTICSD
#            }
#        )
#    )
#
#    c.start(container)
#    OPENNTI_IN_JTI_C = c.inspect_container(OPENNTI_IN_JTI_NAME)['Id']
#
#    # Wait few sec for the container to start
#    time.sleep(1)
#
#    assert c.inspect_container(OPENNTI_IN_JTI_NAME)["State"]["Running"]

def test_start_opennti_in_log_container():
    global OPENNTI_IN_LOG_C
    global OPENNTI_IP

    # Force Stop and delete existing container if exist
    try:
        old_container_id = c.inspect_container(OPENNTI_IN_LOG_NAME)['Id']
        c.stop(container=old_container_id)
        c.remove_container(container=old_container_id)
    except:
        print "Container do not exit"

    # Create new  container
    container = c.create_container(
        image=OPENNTI_IN_LOG_IMAGE,
        name=OPENNTI_IN_LOG_NAME,
        detach=True,
        ports=[
            (TEST_PORT_EVENT, 'udp')
        ],
        environment=[
            "INFLUXDB_PORT="+str(INFLUXDB_PORT),
            "INFLUXDB_DB="+str(DATABASE_NAME),
            "INFLUXDB_USER=juniper",
            "INFLUXDB_PWD=juniper",
            "INFLUXDB_ADDR="+OPENNTI_IP,
            "PORT_SYSLOG="+str(TEST_PORT_EVENT),
            "OUTPUT_INFLUXDB=true",
            "OUTPUT_STDOUT=true"
        ],
        host_config=c.create_host_config(
            port_bindings={
                str(TEST_PORT_EVENT)+'/udp': TEST_PORT_EVENT
            }
        )
    )

    c.start(container)
    OPENNTI_IN_LOG_C = c.inspect_container(OPENNTI_IN_LOG_NAME)['Id']

    # Wait few sec for the container to start
    time.sleep(1)

    assert c.inspect_container(OPENNTI_IN_LOG_NAME)["State"]["Running"]

def test_influxdb_running_database_exist():
    # Verify we can connect to InfluxDB and DB with a name juniper exists

    db = get_handle_db()

    db_list = db.get_list_database()
    found_db = 0
    for db_entry in db_list:
        if db_entry['name'] == DATABASE_NAME:
            found_db = 1
        else:
            continue

    # DROP CONTINUOUS QUERY "four_weeks" ON "juniper"
    # CREATE RETENTION POLICY open_nti_test ON juniper DURATION INF REPLICATION 1 DEFAULT
    if found_db:
        assert 1
    else:
        assert 0

def test_influxdb_create_default_RP():
    # Verify we can connect to InfluxDB and DB with a name juniper exists
    db = get_handle_db()

    query = 'CREATE RETENTION POLICY "open_nti_test" ON juniper DURATION INF REPLICATION 1 DEFAULT;'
    result = db.query(query)

    # DROP CONTINUOUS QUERY "four_weeks" ON "juniper"
    # CREATE RETENTION POLICY open_nti_test ON juniper DURATION INF REPLICATION 1 DEFAULT

    if result:
        assert 1

# def test_collection_agent_01():
#     # Write datapoint using mocked Junos device
#     global OPENNTI_C
#
#     FIXTURES_DIR = "/opt/open-nti/tests/fixtures/test_collection_agent_01/"
#
#     exec_job_id = c.exec_create(
#         container=OPENNTI_C,
#         cmd='/usr/bin/python ' +
#         '/opt/open-nti/open-nti.py -s -t --tag test --input ' + FIXTURES_DIR
#     )
#
#     result = c.exec_start(exec_job_id, stream=True)
#     for line in result:
#         try:
#             stream_line = StreamLineBuildGenerator(line)
#             # Do something with your stream line
#             # ...
#         except ValueError:
#             # If we are not able to deserialize the received line
#             # as JSON object, just print it out
#             print(line)
#             continue
#
#     db = get_handle_db()
#
#     time.sleep(3)
#     query = 'select mean(value) from ' + \
#         '/P1-tf-mx960-1-re0.route-table.summary.inet.0.actives/;'
#     result = db.query(query)
#     points = list(result.get_points())
#
#     assert len(points) == 1 and points[0]['mean'] == 16

def test_start_tcpreplay_container():
    global TCP_REPLAY_C

    # Force Stop and delete existing container if exist
    try:
        old_container_id = c.inspect_container(TCP_REPLAY_NAME)['Id']
        c.stop(container=old_container_id)
        c.remove_container(container=old_container_id)
    except:
        print "Container do not exit"

    container = c.create_container(
        image=TCP_REPLAY_IMAGE,
        command='/usr/bin/tcpreplay --intf1=eth0 /data/test50000.pcap',
        name=TCP_REPLAY_NAME,
        detach=True,
        volumes=[
            '/data'
        ],
        host_config=c.create_host_config(
            binds=[
                LOCAL_PCAP_DIR + ':/data'
            ]
        )
    )

    c.start(container)

    TCP_REPLAY_C = c.inspect_container(TCP_REPLAY_NAME)['Id']

    # Wait few sec for the container to start
    time.sleep(20)

    assert c.inspect_container(TCP_REPLAY_NAME)["State"]["Running"]


#def test_jti_agent():
#    db = get_handle_db()
#
#    query = 'SELECT "value" FROM "jnpr.jvision" WHERE  ' + \
#        '"type" = \'egress_stats.if_pkts\';'
#    result = db.query(query)
#    points = list(result.get_points())
#
#    assert len(points) >= 1


def test_grafana_running():
    url = 'http://' + DOCKER_IP + ':' + \
        str(TEST_PORT_GRAFANA) + '/api/dashboards/db'

    json_data = open(LOCAL_GRAFANA_FILE)
    resp = requests.post(
        url=url,
        auth=(GRAFANA_USER, GRAFANA_PASS),
        json=json.load(json_data),
        headers={'Content-Type': 'application/json; charset=UTF-8'}
    )
    if resp.status_code != 200:
        print "ERROR: " + str(resp.status_code)
        assert 0

    assert 1

def teardown_module(module):
    global c
    global OPENNTI_C
    global OPENNTI_IN_JTI_C
    global OPENNTI_IN_LOG_C

    # Delete all files in /tests/output/
    if not os.getenv('TRAVIS'):

        c.stop(container=OPENNTI_C)
        c.remove_container(container=OPENNTI_C)

        c.stop(container=OPENNTI_IN_JTI_C)
        c.remove_container(container=OPENNTI_IN_JTI_C)

        c.stop(container=OPENNTI_IN_LOG_C)
        c.remove_container(container=OPENNTI_IN_LOG_C)

        c.stop(container=TCP_REPLAY_C)
        c.remove_container(container=TCP_REPLAY_C)
