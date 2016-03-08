from docker import Client
import influxdb
import time
import docker.tls as tls
from os import path
import pprint
import subprocess
import json
import sys, getopt, argparse, os.path, math
from sys import platform as _platform

class StreamLineBuildGenerator(object):
    def __init__(self, json_data):
        self.__dict__ = json.loads(json_data)

if _platform == "linux" or _platform == "linux2":
    # linux
    c = Client(base_url='unix://var/run/docker.sock', version='1.20')
elif _platform == "darwin":
    # MAC OS X
    dockerout = subprocess.check_output(
        ['/usr/local/bin/docker-machine ip default'],
        shell=True, stderr=subprocess.STDOUT
    )

    dockerip = dockerout.splitlines()[0]

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

    url = "https://" + dockerip + ":2376"
    print "URL: " + url
    c = Client(base_url=url, tls=tls_config)
elif _platform == "win32":
    exit

database = "juniper"
db = influxdb.InfluxDBClient(
    host='127.0.0.1', port="8086", database=database, username="juniper",
    password="juniper"
)


def test_connect_docker():
    # Verify one container is running
    containers = c.containers()
    assert len(containers) == 1


def test_influxdb_running_database_exist():
    # Verify we can connect to InfluxDB and DB with a name juniper exists
    # wait in Travis for 10 seconds before run this test
    db_list = db.get_list_database()
    found_db = 0
    for db_entry in db_list:
        if db_entry['name'] == database:
            found_db = 1
        else:
            continue

    if found_db:
        assert 1
    else:
        assert 0


def test_collection_agent():
    # Write datapoint using mocked Junos device
    container_id = c.inspect_container('open-nti_con')['Id']
    exec_job_id = c.exec_create(
        container=container_id,
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

    time.sleep(5)
    query = 'select mean(value) from /P1-tf-mx960-1-re0.route-table.summary.inet.0.actives/;'
    result = db.query(query)
    points = list(result.get_points())

    assert len(points) == 1 and points[0]['mean'] == 16
