from docker import Client
import influxdb
import time
import docker.tls as tls
from os import path
import pprint
import subprocess
import sys, getopt, argparse, os.path, math
from sys import platform as _platform

time.sleep(10)
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

    CERTS = path.join(path.expanduser('~'), '.docker', 'machine', 'machines', 'default')

    tls_config = tls.TLSConfig(
        client_cert=(path.join(CERTS, 'cert.pem'), path.join(CERTS, 'key.pem')),
        ca_cert=path.join(CERTS, 'ca.pem'),
        assert_hostname=False,
        verify=True
    )

    url = "https://" + dockerip + ":2376"
    print "URL: " + url
    c = Client(base_url= url, tls=tls_config)
elif _platform == "win32":
    exit

if _platform == "linux" or _platform == "linux2":
    ip = c.inspect_container('open-nti_con')['NetworkSettings']['IPAddress']
elif _platform == "darwin":
    ip = '127.0.0.1'
else:
    exit

def test_connect_docker():
    containers = c.containers()
    assert len(containers) == 1

def test_influxdb_running_database_exist():
    db = influxdb.InfluxDBClient(host=ip, port="8086", database="juniper", username="juniper", password="juniper")
    db_list = db.get_list_database()
    assert len(db_list) == 2
