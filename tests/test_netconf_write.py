from docker import Client
import docker.tls as tls
from os import path
import pprint
import subprocess
import sys, getopt, argparse, os.path, math

# dockerout = subprocess.check_output(
#     ['/usr/local/bin/docker-machine ip default'],
#     shell=True, stderr=subprocess.STDOUT
# )
#
# dockerip = dockerout.splitlines()[0]
#
# CERTS = path.join(path.expanduser('~'), '.docker', 'machine', 'machines', 'default')
#
# tls_config = tls.TLSConfig(
#     client_cert=(path.join(CERTS, 'cert.pem'), path.join(CERTS, 'key.pem')),
#     ca_cert=path.join(CERTS, 'ca.pem'),
#     assert_hostname=False,
#     verify=True
# )
#
# url = "https://" + dockerip + ":2376"
# print "URL: " + url
# c = Client(base_url= url, tls=tls_config)

c = Client(base_url='unix://var/run/docker.sock', version='1.20')

def test_connect_docker():
    containers = c.containers()
    assert len(containers) == 1
