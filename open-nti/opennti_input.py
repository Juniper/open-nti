import logging
import pprint
import sys
import yaml
import os
import re

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
logger.propagate = False

pp = pprint.PrettyPrinter(indent=4)

class OpenNtiInput:

  def __init__( self, hosts_file='', credentials_file='', commands_file='' ):

    self.__credentials = {}
    self.__hosts = {}
    self.__commands = {}
    self.__supported_command_type = ['netconf', 'snmp', 'oc']

    ###########################################################
    #  LOAD all credentials in a dict
    ###########################################################

    logger.info('Importing credentials file: %s ',credentials_file)
    try:
      with open(credentials_file) as f:
        self.__credentials = yaml.load(f)
    except Exception, e:
      logger.error('Error importing credentials file: %s', credentials_file)
      sys.exit(0)

    ###########################################################
    #  LOAD all hosts with their tags in a dic               ##
    ###########################################################

    logger.info('Importing host file: %s ',hosts_file)
    try:
      with open(hosts_file) as f:
        for host, tags in yaml.load(f).iteritems():
          list_tags = tags.strip().split()
          self.__hosts[host] = list_tags

    except Exception, e:
      logger.error('Error importing host file: %s', hosts_file)
      sys.exit(0)

    ###########################################################
    #  LOAD all commands with their tags in a dict           ##
    ###########################################################
    logger.info('Importing commands file: {0}'.format(commands_file))

    tmp_command= []
    with open(commands_file) as f:
      try:
        for document in yaml.load_all(f):
          tmp_command.append(document)
      except Exception, e:
        logger.error("Error importing commands file: {0}".format(commands_file))
        sys.exit(0)

    # Clean Up commands for all supported Type
    for type in self.__supported_command_type:
      for group_command in tmp_command[0].keys():
        if type in tmp_command[0][group_command].keys():
          ## If command is a string, convert them to a list
          if isinstance(tmp_command[0][group_command][type], str):
            commands_list = tmp_command[0][group_command][type].strip().split("\n")
            tmp_command[0][group_command][type] = commands_list

          ## Save after cleanup if type is supported
          ## Delete entry in initial variable
          self.__commands[group_command] = tmp_command[0][group_command]
          tmp_command[0].pop(group_command, None)

     ## Go over the list one more time but it should be empty
      for group_command in tmp_command[0].keys():
        logger.error("{0} has a non supported type".format(group_command))

  def get_tags(self, host=None):
    return self.__hosts[host]

  def get_target_hosts(self, tags=[]):

    target_hosts = {}

    if tags == []:
        tags = ['.*']

    logger.debug('Inside get_target_hosts()')

    for host in sorted(self.__hosts.keys()):
      for tag in tags:
        for hosts_tag in self.get_tags(host=host):
          if re.search(tag, hosts_tag, re.IGNORECASE):
            target_hosts[host] = 1

    return target_hosts.keys()

  def get_target_netconf(self, host=''):
    return self.get_target_commands(host=host, type='netconf')

  def get_target_snmp(self, host=''):
    return self.get_target_commands(host=host, type='snmp')

  def get_target_oc(self, host=''):
    return self.get_target_commands(host=host, type='oc')

  def get_target_commands(self, host='', type=''):

    if type not in self.__supported_command_type:
      return None

    my_host_tags = self.get_tags(host=host)

    my_target_commands = {}
    for group_command in sorted(self.__commands.keys()):
      for my_host_tag in my_host_tags:
        for command_tag in self.__commands[group_command]["tags"].split():
          if re.search(my_host_tag, command_tag, re.IGNORECASE):
            if type in self.__commands[group_command].keys():
              for cmd in self.__commands[group_command][type]:
                my_target_commands[cmd] = 1

    return my_target_commands.keys()

  def get_target_credential(self, host=''):

    my_host_tags = self.get_tags(host=host)
    print my_host_tags
    my_target_credentials = {'username': None,
                             'password': None,
                             'port': 830,
                             'method': None,
                             'key_file': None }

    for credential in sorted(self.__credentials.keys()):
      for my_host_tag in my_host_tags:
        for credential_tag in self.__credentials[credential]["tags"].split():
          if re.search(my_host_tag, credential_tag, re.IGNORECASE):

            if not ("username" in self.__credentials[credential].keys()):
              logger.error("Missing username information")
              return None
            else:
              my_target_credentials['username'] = self.__credentials[credential]["username"]

            ## Port
            if ("port" in self.__credentials[credential].keys()):
              my_target_credentials['port'] = self.__credentials[credential]["port"]

            if ("method" in self.__credentials[credential].keys()):
                my_target_credentials['method'] = self.__credentials[credential]["method"]

                if (self.__credentials[credential]["method"] == "key"):
                  if not ("key_file" in self.__credentials[credential].keys()):
                    logger.error("Missing key_file information")
                    return None

                  my_target_credentials['key_file'] = self.__credentials[credential]["key_file"]
                  return my_target_credentials

                elif (self.__credentials[credential]["method"] == "enc_key"):
                  if not ("key_file" in self.__credentials[credential].keys()):
                    logger.error("Missing key_file information")
                    return None

                  if not ("password" in self.__credentials[credential].keys()):
                    logger.error("Missing password information")
                    return None

                  my_target_credentials['password'] = self.__credentials[credential]["password"]
                  my_target_credentials['key_file'] = self.__credentials[credential]["key_file"]

                  return my_target_credentials

                elif (self.__credentials[credential]["method"] == "password"):
                  my_target_credentials['password'] = self.__credentials[credential]["password"]
                  my_target_credentials['key_file'] = self.__credentials[credential]["key_file"]

                  return my_target_credentials

                else:
                  logger.error("Unknown authentication method found")
                  return None
            else:
              if not ("password" in self.__credentials[credential].keys()):
                logger.error("Missing password information")
                return None
              my_target_credentials['password'] = self.__credentials[credential]["password"]

              return my_target_credentials
