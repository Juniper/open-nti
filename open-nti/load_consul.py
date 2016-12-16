import logging
import opennti_input
import sys
import os
import requests
import httplib2
import json

# logger = logging.getLogger( 'input' )

if __name__ == "__main__":

    BASE_DIR = ''
    if getattr(sys, 'frozen', False):
        # frozen
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        # unfrozen
        BASE_DIR = os.path.dirname(os.path.realpath(__file__))

    Input = opennti_input.OpenNtiInput(
                hosts_file = BASE_DIR + '/../data/hosts.yaml',
                credentials_file = BASE_DIR + '/../data/credentials.yaml',
                commands_file = BASE_DIR + '/../data/commands.yaml'
            )

    hosts = Input.get_target_hosts()
    print hosts
    # print Input.get_target_commands(host='192.168.194.128')

    for host in hosts:
      for type in ['netconf', 'snmp', 'oc']:

        ## Upload list of commands to Consul
        commands = Input.get_target_commands(host=host, type=type)

        if not commands == []:
          url = "http://localhost:8500/v1/kv/inputs/{0}/{1}/commands".format(type, host)
          headers = {}
          r = requests.put(
            url,
            data=json.dumps(commands),
          )

        if type == 'netconf':
          url = "http://localhost:8500/v1/kv/inputs/{0}/{1}/credential".format(type, host)
          # print url
          credential = Input.get_target_credential(host=host)
          headers = {}
          r = requests.put(
            url,
            data=json.dumps(credential),
          )
