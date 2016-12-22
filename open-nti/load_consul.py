import logging
import opennti_input
import sys
import os
import requests
import httplib2
import json
import yaml

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

    ############################################################
    ## Load all files in JSON format
    ############################################################
    for file in ['hosts', 'credentials', 'commands', 'variables']:

      ## TODO Add check to verify that YAML is valid
      file_addr = BASE_DIR + '/../data/{0}.yaml'.format(file)

      file_yaml = []
      with open(file_addr) as f:
        for document in yaml.load_all(f):
          file_yaml.append(document)

    #   file_content = open(file_addr).read()
    #   file_yaml = yaml.load_all(file_content)

      url = "http://localhost:8500/v1/kv/parameters/{0}".format(file)

      r = requests.put(
        url,
        data=json.dumps(file_yaml[0]),
      )

    ############################################################
    ## Load parameters for each Hosts and Inputs
    ############################################################
    hosts = Input.get_target_hosts()
    # print hosts
    # print Input.get_target_commands(host='192.168.194.128')

    for host in hosts:
      for type in ['netconf', 'snmp', 'oc']:

        ## Upload list of commands to Consul
        commands = Input.get_target_commands(host=host, type=type)

        ## Load commands
        if not commands == []:
          url = "http://localhost:8500/v1/kv/inputs/{0}/{1}/commands".format(type, host)
          r = requests.put(
            url,
            data=json.dumps(commands),
          )

        ## Load tags
        tags = Input.get_tags(host=host)
        url = "http://localhost:8500/v1/kv/inputs/{0}/{1}/tags".format(type, host)
        r = requests.put(
            url,
            data=json.dumps(tags),
          )

        ## Load credentials
        if type == 'netconf':
          url = "http://localhost:8500/v1/kv/inputs/{0}/{1}/credential".format(type, host)
          # print url
          credential = Input.get_target_credential(host=host)
          r = requests.put(
            url,
            data=json.dumps(credential),
          )

    ## Load general Parameters
