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

def get_list_hosts_from_consul( consul='localhost', type='' ):

    url = "http://{0}:8500/v1/kv/{1}?keys".format(consul, type)

    hosts = {}

    r = requests.get( url )
    if r.status_code != 200:
      # something wrong happened
      return {}

    keys = r.json()
    if not isinstance(keys, list):
      # something wrong happened
      return {}

    for key in keys:
      items =  key.split('/')
      hosts[items[2]] = 1

    return hosts

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
    for type in ['netconf', 'snmp', 'oc']:

      ## Get the list of existing hosts for this type from consul
      hosts_consul = get_list_hosts_from_consul( consul=args['consul'], type="inputs/{0}".format(type) )

      for host in hosts:

        ## Upload list of commands to Consul
        commands = Input.get_target_commands(host=host, type=type)

        ## Load commands
        if not commands == []:

          # Indicate this host as "processed"
          hosts_consul[host] = 2

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
          hosts_consul[host] = 2
          url = "http://{0}:8500/v1/kv/inputs/{1}/{2}/credential".format(args['consul'], type, host)
          credential = Input.get_target_credential(host=host)
          r = requests.put(
            url,
            data=json.dumps(credential),
          )

      ## Got over the list of hosts from consul and identify hosts that
      ## have not been processed AKA should be removed
      for host in hosts_consul.keys():
        if hosts_consul[host] == 1:
          url = "http://{0}:8500/v1/kv/inputs/{1}/{2}?recurse".format(args['consul'], type, host)
          r = requests.delete(url)
          # print 'Deleted key kv/inputs/{0}/{1}'.format(type, host)
