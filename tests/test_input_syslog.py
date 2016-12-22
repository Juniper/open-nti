from docker import Client
import open_nti_input_syslog_lib

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
from kafka import KafkaConsumer
from timeout import timeout

################################################################################

def test_connect_docker():

    c = open_nti_input_syslog_lib.check_docker()

    # Check if connection to Docker work by listing all images
    list_images = c.images()
    assert len(list_images) >= 1

def test_start_dependancies():
    open_nti_input_syslog_lib.start_open_nti()
    assert open_nti_input_syslog_lib.check_influxdb_running_database_exist()

    open_nti_input_syslog_lib.start_kafka()
    assert open_nti_input_syslog_lib.check_kafka_is_running()

def test_syslog_qfx_influx_01():
    FNAME       = 'test_syslog_qfx_01'
    PCAP_FILE   = FNAME + "/syslog_qfx_01_16000.pcap"

    open_nti_input_syslog_lib.start_fluentd_syslog(output_influx='true')
    open_nti_input_syslog_lib.replay_file(PCAP_FILE)

    time.sleep(5)

    db = open_nti_input_syslog_lib.get_influxdb_handle()
    query = 'SELECT * FROM events'
    result = db.query(query)
    points = result.get_points()


    assert len(list(points)) != 0

@timeout(30)
def test_syslog_qfx_kafka_01():

    FNAME       = 'test_syslog_qfx_01'
    PCAP_FILE   = FNAME + "/syslog_qfx_01_16000.pcap"

    open_nti_input_syslog_lib.start_fluentd_syslog(output_kafka='true')
    time.sleep(1)
    open_nti_input_syslog_lib.replay_file(PCAP_FILE)

    time.sleep(5)

    counter = open_nti_input_syslog_lib.check_kafka_msg()

    assert counter == 100

def teardown_module(module):
    global c
    global TCP_RELAY_CONTAINER_NAME

    # if not os.getenv('TRAVIS'):
    open_nti_input_syslog_lib.stop_fluentd()
    open_nti_input_syslog_lib.stop_open_nti()
    open_nti_input_syslog_lib.stop_kafka()

    try:
        old_container_id = c.inspect_container(TCP_RELAY_CONTAINER_NAME)['Id']
        c.stop(container=old_container_id)
        c.remove_container(container=old_container_id)
    except:
        print "Container do not exit"
