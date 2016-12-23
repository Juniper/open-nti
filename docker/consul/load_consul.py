import logging
import opennti_input
import sys
import os
import requests
import httplib2
import json
import yaml
import argparse

# logger = logging.getLogger( 'input' )

if __name__ == "__main__":

    full_parser = argparse.ArgumentParser()
    full_parser.add_argument("--dir", default="/opt/open-nti/data", help="Directory where to find Yaml file to upload")
    full_parser.add_argument("--consul", default="consul", help="Address of consul server ")

    args = vars(full_parser.parse_args())

    BASE_DIR = ''
    if getattr(sys, 'frozen', False):
        # frozen
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        # unfrozen
        BASE_DIR = os.path.dirname(os.path.realpath(__file__))

    Input = opennti_input.OpenNtiInput(
                hosts_file = args['dir'] + '/hosts.yaml',
                credentials_file =  args['dir'] + '/credentials.yaml',
                commands_file =  args['dir'] + '/commands.yaml'
            )

    ############################################################
    ## Load all files in JSON format
    ############################################################
    for file in ['hosts', 'credentials', 'commands', 'variables']:

      ## TODO Add check to verify that YAML is valid
      file_addr =  args['dir'] + '/{0}.yaml'.format(file)

      file_yaml = []
      with open(file_addr) as f:
        for document in yaml.load_all(f):
          file_yaml.append(document)

      url = "http://{0}:8500/v1/kv/parameters/{1}".format(args['consul'], file)

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
          url = "http://{0}:8500/v1/kv/inputs/{1}/{2}/commands".format(args['consul'], type, host)
          r = requests.put(
            url,
            data=json.dumps(commands),
          )

        ## Load tags
        tags = Input.get_tags(host=host)
        url = "http://{0}:8500/v1/kv/inputs/{1}/{2}/tags".format(args['consul'], type, host)
        r = requests.put(
            url,
            data=json.dumps(tags),
          )

        ## Load credentials
        if type == 'netconf':
          url = "http://{0}:8500/v1/kv/inputs/{1}/{2}/credential".format(args['consul'], type, host)
          # print url
          credential = Input.get_target_credential(host=host)
          r = requests.put(
            url,
            data=json.dumps(credential),
          )

    ## Load general Parameters
