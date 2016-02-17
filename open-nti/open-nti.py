#!/usr/bin/env python
# coding: utf-8
# Authors: efrain@juniper.net psagrera@juniper.net
# Version 2.0  20160124 

from datetime import datetime # In order to retreive time and timespan
from datetime import timedelta # In order to retreive time and timespan
from influxdb import InfluxDBClient
from jnpr.junos import *
from jnpr.junos import Device
from jnpr.junos.exception import * 
from jnpr.junos.utils.start_shell import StartShell
from lxml import etree  # Used for xml manipulation
from pprint import pformat
from pprint import pprint
from pybot_jixia import pybot_jixia
from ssh_manager_lite import *
import argparse   # Used for argument parsing
import json
import logging
import logging.handlers
import os  # For exec to work
import pprint
import re # For regular expression usage
import requests
import string
import string  # For split multiline script into multiple lines
import StringIO   # Used for file read/write
import sys  # For exec to work
import threading
import time
import xmltodict
import yaml
import copy

logging.getLogger("paramiko").setLevel(logging.INFO)

####################################################################################
####################################################################################
# Defining the classes and procedures used later on the script 
####################################################################################
####################################################################################

def convert_variable_type(var):

    try:
        result = int(var)
        return result
    except Exception as e:
        pass

    try:
        result = float(var)
        return result
    except Exception as e:
        pass
    return var   # I guess that is a string 

def check_db_status():
    return True
    for i in range(0, 3):
        try: 
            query = "list series"
            response = requests.get('http://%s:%s/db/%s/series?u=%s&p=%s&q=%s' % (db_server,db_port,db_name,db_user,db_user_password,query),timeout=1)
            break
        except requests.exceptions.Timeout as e:
            # Maybe set up for a retry, or continue in a retry loop
            if i < 2:
                continue
            else:
                logger.error('Error trying to connect to database server, check IP connectivity and db server status.\n %s', e)
                sys.exit(1)
        except Exception as e:
            logger.error('Error trying to connect to database daemon, check ports used and server status.\n %s', e)
            sys.exit(1)

    logger.debug('Request response status code: %s', response.status_code)
    try:
        response.raise_for_status()  # It will raise an exception if status_code is error (a 4XX client error or 5XX server error response)
        return True
    except Exception as e:
        logger.error('Error querying open-nti database: %s', e)

def get_latest_datapoints(**kwargs):
    
    dbclient = InfluxDBClient(db_server, db_port, db_admin, db_admin_password)
    dbclient.switch_database(db_name)
    query = "select value from /%s\./ ORDER BY time DESC limit 1 " % (kwargs['host'])
    results_tmp = dbclient.query(query)
    results = {}
    if results_tmp.raw:
        for result_tmp in results_tmp.raw['series']:
            results[result_tmp['name']] = result_tmp['values'][0][1]
    return results

def get_target_hosts():
    my_target_hosts = {}
    for host in sorted(hosts.keys()):
        for tag in tag_list:
            print type(tag)
            print tag
            for hosts_tag in hosts[host].split():
                if re.search(tag, hosts_tag, re.IGNORECASE):
                    my_target_hosts[host] = 1
    return my_target_hosts.keys()

def get_target_commands(my_host):
    my_host_tags = hosts[my_host]
    my_target_commands = {}
    for group_command in sorted(general_commands.keys()):
        for my_host_tag in my_host_tags.strip().split():
            for command_tag in general_commands[group_command]["tags"].split():
                if re.search(my_host_tag, command_tag, re.IGNORECASE):
                    if "commands" in general_commands[group_command].keys():
                        for cmd in general_commands[group_command]["commands"].strip().split("\n"):
                            my_target_commands[cmd] = 1
    return my_target_commands.keys()

def get_ixia_commands(my_host):
    my_host_tags = hosts[my_host]
    my_target_commands = {}
    for group_command in sorted(general_commands.keys()):
        for my_host_tag in my_host_tags.strip().split():
            for command_tag in general_commands[group_command]["tags"].split():
                if re.search(my_host_tag, command_tag, re.IGNORECASE):
                    if "default_views" in general_commands[group_command].keys():
                        for cmd in general_commands[group_command]["default_views"].strip().split("\n"):
                            my_target_commands[cmd] = 1
    return my_target_commands.keys()

def get_credentials(my_host):
    my_host_tags = hosts[my_host]
    my_target_credentials = {}
    for credential in sorted(credentials.keys()):
        for my_host_tag in my_host_tags.strip().split():
            for credential_tag in credentials[credential]["tags"].split():
                if re.search(my_host_tag, credential_tag, re.IGNORECASE):
                    return credentials[credential]["username"], credentials[credential]["password"] 
        
def execute_command(jdevice,command):
    format = "text"
    command_tmp = command
    if re.search("\| display xml", command, re.IGNORECASE):
        format = "xml"
        command_tmp = command.replace("| display xml","")
    elif re.search("\| count", command, re.IGNORECASE):
        format = "txt-filtered"
        command_tmp = command.split("|")[0]       
    try:
        # Remember... all rpc must have format=xml at execution time, 
        command_result = jdevice.rpc.cli(command_tmp, format="xml")
    except RpcError as err:    
        rpc_error = err.__repr__()
        logger.error("Error found executing command: %s, error: %s:", command ,rpc_error)
        return False 
    if format == "text":
        # We need to confirm that root tag in command_result is <output> if not then raise exception and skip
        return command_result.text
    elif format == "xml":
        return etree.tostring(command_result)
    elif format == "txt-filtered":
        operations = command.split("|")[1:]
        result_tmp = command_result.text
        lines=result_tmp.strip().split('\n')
        for operation in operations:
            logger.info("Processing <%s>", operation )
            if re.search("count", operation, re.IGNORECASE):
                result = "Count: %s lines" % len(lines)
                logger.debug("Count result: <%s>", result ) 
                return result
            match = re.search("match (.*)", operation, re.IGNORECASE)
            if match:
                regex = match.group(1).strip()
                logger.debug("Found regex: <%s>", regex )
                lines_filtered = []
                for line in lines:
                    if re.search(regex, line, re.IGNORECASE):
                        lines_filtered.append(line)
                lines = lines_filtered
                logger.debug("Filtered result:\n%s", "\n".join(lines_filtered) )
            match = re.search("except (.*)", operation, re.IGNORECASE)
            if match:
                regex = match.group(1).strip()
                logger.debug("Found regex: <%s>", regex )
                lines_filtered = []
                for line in lines:
                    if re.search(regex, line, re.IGNORECASE):
                        pass
                    else:
                        lines_filtered.append(line)
                lines = lines_filtered
                logger.debug("Filtered result:\n%s", "\n".join(lines_filtered) )
        return "\n".join(lines)

def eval_variable_name(variable,**kwargs):
    keys={}
    if 'keys' in kwargs.keys():
        # This is due dict are mutable and a normal assigment does NOT copy the value, it copy the reference
        keys=copy.deepcopy(kwargs['keys'])
    if db_schema == 3:
        for key in kwargs:
            variable = variable.replace("$"+key,"")
            variable = variable.replace("..",".")
            variable = re.sub(r"^\.", "", variable)
        return variable, variable
    if db_schema == 2:
        for key in kwargs:
            variable = variable.replace("$"+key,"")
            variable = variable.replace("..",".")
            variable = re.sub(r"^\.", "", variable)
        return "juniper", variable
    else: # default db_schema (option 1) open-nti legacy
        for key in keys.keys():
            variable = variable.replace("$"+key,keys[key])
        variable = variable.replace("$host",kwargs['host'])
        # the host replacement should be move it to other place
        return variable, variable

def eval_tag_name(variable,**kwargs):
    for key in kwargs:
        variable = variable.replace("$"+key,kwargs[key])
    return variable


def eval_variable_value(value,**kwargs):

    if (kwargs["type"] == "integer"):
        value =  re.sub('G','000000000',value)
        value =  re.sub('M','000000',value)
        value =  re.sub('K','000',value)
        return(int(float(value)))
    elif kwargs["type"] == "string":
        return value
    else:
        logger.error('An unkown variable-type found: %s', kwargs["type"])
        return value

def insert_datapoints(datapoints):

    dbclient = InfluxDBClient(db_server, db_port, db_admin, db_admin_password)
    dbclient.switch_database(db_name)
    logger.info('Inserting into database the following datapoints:')
    logger.info(pformat(datapoints))
    response = dbclient.write_points(datapoints)


def get_metadata_and_add_datapoint(datapoints,**kwargs):

    value_tmp  = kwargs['value_tmp']                              
    host = kwargs['host']
    latest_datapoints=kwargs['latest_datapoints']

    match={}
    if 'match' in kwargs.keys():
        # This is due dict are mutable and a normal assigment does NOT copy the value, it copy the reference
        match=copy.deepcopy(kwargs['match'])

    kpi_tags={}
    if 'kpi_tags' in kwargs.keys():
        # This is due dict are mutable and a normal assigment does NOT copy the value, it copy the reference
        kpi_tags=copy.deepcopy(kwargs['kpi_tags'])   

    key=''
    if 'key' in kwargs.keys():
        key=kwargs['key']

    keys={}
    if 'keys' in kwargs.keys():
        # This is due dict are mutable and a normal assigment does NOT copy the value, it copy the reference
        keys=copy.deepcopy(kwargs['keys'])

    # Resolving the variable name 
    value = convert_variable_type(value_tmp)
    variable_name, kpi_tags['kpi'] = eval_variable_name(match["variable-name"],host=host,keys=keys)
    

    # Calculating delta values (only applies for numeric values)
    delta = 0
    if type (value) != str:           
        if variable_name in latest_datapoints.keys():
            # We asume that allways 'value' is the latest 'value' in the list
            latest_value = latest_datapoints[variable_name]
            if latest_value != '':
                delta = value - convert_variable_type(latest_value)
            else:
                delta = value    
        if type (value) == int:
            delta = int(delta)
        elif type (value) == float:
            delta = float(delta)
    else:
        delta = 'N/A'

    # Getting all tags related to the kpi
    if 'tags' in match.keys():
        for tag in match['tags']:
            tag_name = tag.keys()[0]  # We asume that this dict only has one key
            tag_value = eval_tag_name(tag[tag_name],host=host,key=key)
            kpi_tags[tag_name] = tag_value

    # Building the kpi and append it to the other kpis before database insertion
    if type (value) != str:
        kpi = {
            "measurement": variable_name,
            "fields": {
                "value": value, 
                "delta": delta
            }
        }
    else:
        kpi = {
            "measurement": variable_name,
            "fields": {
                "value_str": value, 
                "delta_str": delta
            }
        }

    kpi["tags"] = kpi_tags
    datapoints.append(copy.deepcopy(kpi))

def parse_ixia_result(host,target_command,result,datapoints,latest_datapoints,kpi_tags):
    timestamp = str(int(datetime.today().strftime('%s')))
    for tmp in result:
        columns = [x.replace(' ','_') for x in tmp['columnCaption']]
        rows = tmp['RowVal']
        logger.info("Command =  <%s>, len_cols = <%s> len_rows <%s> " ,target_command, len(columns),len(rows) )
        for row in rows:
            row_data = row[0]
            for i in range(1,len(columns)):
                variable_name = host + "." + target_command.replace(' ','_') + "." + row_data[0].replace(' ','_') + "." + columns[i].replace(' ','_')
                value = convert_variable_type(row_data[i])
                if value != '':
                    kpi_tags['kpi']=variable_name
                    add_datapoint(datapoints=datapoints,variable_name=variable_name,value=value,latest_datapoints=latest_datapoints,kpi_tags=kpi_tags)
                else:
                    value = 0   # This is a hack in order to allways put something on grafana chats (need to review if apply for all variables)
                    kpi_tags['kpi']=variable_name
                    add_datapoint(datapoints=datapoints,variable_name=variable_name,value=value,latest_datapoints=latest_datapoints,kpi_tags=kpi_tags)

def parse_result(host,target_command,result,datapoints,latest_datapoints,kpi_tags):
    for junos_parser in junos_parsers:
        regex_command = junos_parser["parser"]["regex-command"]
        if re.search(regex_command, target_command, re.IGNORECASE):
            matches = junos_parser["parser"]["matches"]
            timestamp = str(int(datetime.today().strftime('%s')))
            for match in matches:
                try:
                    if match["method"] == "xpath":
                        # Load xml data
                        xml_data = etree.fromstring(result)
                        if match["type"] == "single-value":
                            try:
                                logger.debug('[%s]: Looking for a match: %s', host, match["xpath"])
                                if xml_data.xpath(match["xpath"]):
                                    value_tmp = xml_data.xpath(match["xpath"])[0].text.strip()
                                    get_metadata_and_add_datapoint(datapoints=datapoints,match=match,value_tmp=value_tmp,latest_datapoints=latest_datapoints,host=host,kpi_tags=kpi_tags)
                                else:
                                    logger.debug('No match found: %s', match["xpath"])
                                    if 'default-if-missing' in match.keys():
                                        logger.debug('Inserting default-if-missing value: %s', match["default-if-missing"])
                                        value_tmp = match["default-if-missing"]
                                        get_metadata_and_add_datapoint(datapoints=datapoints,match=match,value_tmp=value_tmp,latest_datapoints=latest_datapoints,host=host,kpi_tags=kpi_tags)
                            except Exception, e:
                                logger.info('[%s]: Exception found.', host)
                                logging.exception(e)
                                pass  # Notify about the specific problem with the host BUT we need to continue with our list
                        elif match["type"] == "multi-value":
                            nodes = xml_data.xpath(match["xpath"])
                            for node in nodes:
                                #Look for all posible keys or fields to extract and be used for variable-naming
                                #key = node.xpath(match["loop"]["key"])[0].text.replace(" ","_").strip()
                                #print "the key is: " + key
                                keys = {}
                                keys_tmp = copy.deepcopy(match["loop"])
                                #print keys_tmp
                                if 'sub-matches' in keys_tmp.keys():
                                    del keys_tmp['sub-matches']
                                for key_tmp in keys_tmp.keys():
                                    keys[key_tmp]=node.xpath(keys_tmp[key_tmp])[0].text.replace(" ","_").strip()
                                #print keys
                                for sub_match in match["loop"]["sub-matches"]:
                                    try:
                                        logger.debug('[%s]: Looking for a sub-match: %s', host, sub_match["xpath"])
                                        if node.xpath(sub_match["xpath"]):
                                            value_tmp = node.xpath(sub_match["xpath"])[0].text.strip()
                                            get_metadata_and_add_datapoint(datapoints=datapoints,match=sub_match,value_tmp=value_tmp,latest_datapoints=latest_datapoints,host=host,kpi_tags=kpi_tags,keys=keys)
                                        else:
                                            logger.debug('[%s]: No match found: %s', host, match["xpath"])
                                            if 'default-if-missing' in sub_match.keys():
                                                logger.debug('Inserting default-if-missing value: %s', sub_match["default-if-missing"])
                                                value_tmp = sub_match["default-if-missing"]
                                                get_metadata_and_add_datapoint(datapoints=datapoints,match=sub_match,value_tmp=value_tmp,latest_datapoints=latest_datapoints,host=host,kpi_tags=kpi_tags,keys=keys)
                                    except Exception, e:
                                        logger.info('[%s]: Exception found.', host)
                                        logging.exception(e)
                                        pass  # Notify about the specific problem with the host BUT we need to continue with our list
                        else:
                            logger.error('[%s]: An unkown match-type found in parser with regex: %s', host, regex_command)
                    elif match["method"] == "regex": # we need to evaluate a text regex 
                        if match["type"] == "single-value":
                            regex = match["regex"]
                            text_matches = re.search(regex,result,re.MULTILINE)
                            if text_matches:
                                if text_matches.lastindex == len(match["variables"]):
                                    logger.debug('[%s]: We have (%s) matches with this regex %s', host, text_matches.lastindex,regex)
                                    for i in range(0,text_matches.lastindex):
                                        j=i+1
                                        variable_name = eval_variable_name(match["variables"][i]["variable-name"],host=host)
                                        value_tmp = text_matches.group(j).strip()
                                        # Begin function  (pero pendiente de ver si variable-type existe y su valor)
                                        if "variable-type" in match["variables"][i]:
                                            value_tmp = eval_variable_value(value_tmp, type=match["variables"][i]["variable-type"])
                                        get_metadata_and_add_datapoint(datapoints=datapoints,match=match["variables"][i],value_tmp=value_tmp,latest_datapoints=latest_datapoints,host=host,kpi_tags=kpi_tags)
                                else:
                                    logger.error('[%s]: More matches found on regex than variables especified on parser: %s', host, regex_command)
                            else:
                                logger.info('[%s]: No matches found for regex: %s', host, regex)
                        else:
                            logger.error('[%s]: An unkown match-type found in parser with regex: %s', host, regex_command)
                    else: 
                        logger.error('[%s]: An unkown method found in parser with regex: %s', host, regex_command)
                except Exception, e:
                    logger.info('[%s]: Exception found.', host)
                    logging.exception(e)
                    pass  # Notify about the specific problem with the host BUT we need to continue with our list


def collector(**kwargs):

    dbclient = InfluxDBClient(db_server, db_port, db_user, db_user_password, db_name)

    for host in kwargs["host_list"]:
        latest_datapoints = get_latest_datapoints(host=host)
        kpi_tags={}
#       kpi_tags = get_host_base_tags(host=host)
        logger.info("Latest Datapoints are:")
        logger.info(pformat(latest_datapoints))
        # Check host tag to identify what kind of connections will be used (ej junos / ixia  / etc)
        if "ixia" in hosts[host].split():
            connected = False
            try:
                dev = pybot_jixia(ixia_server="172.30.153.72",ixia_port=8009)
                dev.ixia_connect()
                connected = True
                logger.info( "connected" )
            except Exception, e: 
                connected = False
                print e
                print "failed connection"
                continue
            if connected:
                datapoints = []
                kpi_tags = {}
                target_commands = get_ixia_commands(host)
                for target_command in target_commands:
                    result = {}
                    try:
                        result = dev.gather_stats(view=target_command, verbose=False)
                        # Revisar aqui si el output es valido antes de parsear
                        parse_ixia_result(host,target_command,result,datapoints,latest_datapoints,kpi_tags)
                    except Exception, e:
                        logger.error('[%s]: Problems gathering ixia stats  %s', target_command)
                        continue 
                dev.ixia_disconnect ()
                if datapoints:   # Only insert datapoints if there is any :)
                    pprint(datapoints)
                    insert_datapoints(datapoints)

        elif 'ssh' in hosts[host].split():

            connected = False
            logger.info('Connecting to host: %s', host)
            target_commands = get_target_commands(host)
            timestamp_tracking={}
            connector = ssh_manager_lite (target=host)
            try:
                device = connector.open()
                connected = True
            except timeout_exception as tmout:
                raise (tmout)
            print target_commands
            if connected:
                datapoints = []
                timestamp_tracking['collector_ssh_start'] = int(datetime.today().strftime('%s'))
                for target_command in target_commands:
                    logger.info('[%s]: Executing command: %s', host, target_command)
                    result = connector.command_executor(device,target_command)
                    print result
                    if result:
                        logger.debug('[%s]: Parsing command: %s', host, target_command)
                        parse_result(host,target_command,result,datapoints,latest_datapoints)
                        time.sleep(delay_between_commands)
                        
                connector.close(device)
                timestamp_tracking['collector_ssh_ends'] = int(datetime.today().strftime('%s'))  
                if datapoints:
                    insert_datapoints(datapoints)
                logger.info('[%s]: timestamp_tracking - CLI collection %s', host, timestamp_tracking['collector_ssh_ends']-timestamp_tracking['collector_ssh_start'])    

        else: # By default it's a junos device
            # We need to CATCH errors then print then but we need to continue with next host...
            connected = False
            logger.info('Connecting to host: %s', host)
            target_commands = get_target_commands(host)
            timestamp_tracking={}
            timestamp_tracking['collector_start'] = int(datetime.today().strftime('%s'))
            # Establish connection to hosts
            user, passwd = get_credentials(host)
            jdev = Device(user=user, host=host, password=passwd, gather_facts=False, auto_probe=True, port=22)
            for i in range(1, max_connection_retries+1):
                try:
                    jdev.open()
                    jdev.timeout = default_junos_rpc_timeout
                    connected = True
                    break
                except Exception, e:
                    if i < max_connection_retries:
                        logger.error('[%s]: Connection failed %s time(s), retrying....', host, i)
                        time.sleep(1)
                        continue
                    else:
                        logging.exception(e)
                        connected = False  # Notify about the specific problem with the host BUT we need to continue with our list
            # First collect all kpi in datapoints {} then at the end we insert them into DB (performance improvement)
            if connected:
                datapoints = []
                # By default execute show version in order to get version and platform as default tags for all kpi related to this host
                kpi_tags = {}
                target_command = 'show version | display xml'
                version_xpath = "//package-information/comment"
                product_model_xpath = "//product-model"
                logger.info('[%s]: Executing command: %s', host, target_command)
                result = execute_command(jdev,target_command)
                if result:
                    logger.debug('[%s]: Parsing command: %s', host, target_command)
                    xml_data = etree.fromstring(result)
                    value_tmp = xml_data.xpath(version_xpath)[0].text.strip()
                    version = re.search('\[(.*?)\]$', value_tmp)
                    if version:
                        kpi_tags['version'] = version.group(1)
                    else:
                        kpi_tags['version'] = 'unknown'
                    value_tmp = xml_data.xpath(product_model_xpath)[0].text.strip()
                    kpi_tags['product-model'] = convert_variable_type(value_tmp)

                    ## Based on parameter defined in config file
 
                    if use_hostname:
                        hostname_xpth = "//host-name"
                        hostname_tmp = xml_data.xpath(hostname_xpth)[0].text.strip()
                        hostname = convert_variable_type(hostname_tmp)
                        logger.info('[%s]: Host will now be referenced as : %s', host, hostname)
                        host = hostname
                        latest_datapoints = get_latest_datapoints(host=host)
                        logger.info("Latest Datapoints are:")
                        logger.info(pformat(latest_datapoints))
                    else:
                        logger.info('[%s]: Host will be referenced as : %s', host, host)


                    kpi_tags['host']=host
                    kpi_tags['kpi']="base-info"
                    match={}
                    match["variable-name"]="base-info"
                    # We'll add a dummy kpi in oder to have at least one fixed kpi with version/platform data.
                    get_metadata_and_add_datapoint(datapoints=datapoints,match=match,value_tmp=value_tmp,latest_datapoints=latest_datapoints,host=host,kpi_tags=kpi_tags)

                # Now we have all hosts tags that all host kpis will inherit
                # For each target_command execute it, parse it, and insert values into DB
                timestamp_tracking['collector_cli_start'] = int(datetime.today().strftime('%s'))
                for target_command in target_commands:
                    logger.info('[%s]: Executing command: %s', host, target_command)
                    # Execute rpc/command on host and get result
                    result = execute_command(jdev,target_command)
                    if result:
                        logger.debug('[%s]: Parsing command: %s', host, target_command)
                        parse_result(host,target_command,result,datapoints,latest_datapoints,kpi_tags)
                        time.sleep(delay_between_commands)
                jdev.close()
                timestamp_tracking['collector_cli_ends'] = int(datetime.today().strftime('%s'))
                logger.info('[%s]: timestamp_tracking - CLI collection %s', host, timestamp_tracking['collector_cli_ends']-timestamp_tracking['collector_cli_start'])
    
                if datapoints:   # Only insert datapoints if there is any :)
                    insert_datapoints(datapoints)
                
                timestamp_tracking['collector_ends'] = int(datetime.today().strftime('%s'))   
                logger.info('[%s]: timestamp_tracking - total collection %s', host, timestamp_tracking['collector_ends']-timestamp_tracking['collector_start'])
            else:
                logger.error('[%s]: Skiping host due connectivity issue', host)


################################################################################################ 
################################################################################################
################################################################################################

# SCRIPT STARTS HERE

################################################################################################
# Create and Parse Arguments
################################################################################################

if getattr(sys, 'frozen', False):
    # frozen
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # unfrozen
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))

full_parser = argparse.ArgumentParser()
full_parser.add_argument("--tag", nargs='+', help="Collect data from hosts that matches the tag")
full_parser.add_argument("-c", "--console", action='store_true', help="Console logs enabled")
full_parser.add_argument("-s", "--start", action='store_true', help="Start collecting (default 'no')")
dynamic_args = vars(full_parser.parse_args())

################################################################################################
# Loading YAML Default Variables 
###############################################################################################

default_variables_yaml_file = BASE_DIR + "/data/open-nti.variables.yaml"
default_variables = {}

with open(default_variables_yaml_file) as f: 
    default_variables = yaml.load(f)

db_schema = default_variables['db_schema']
db_server = default_variables['db_server']
db_port = default_variables['db_port']
db_name = default_variables['db_name']
db_admin = default_variables['db_admin']
db_admin_password = default_variables['db_admin_password']
db_user = default_variables['db_user']
db_user_password = default_variables['db_user_password']
max_connection_retries = default_variables['max_connection_retries']
max_collector_threads = default_variables['max_collector_threads']
delay_between_commands = default_variables['delay_between_commands']
logging_level = default_variables['logging_level']
default_junos_rpc_timeout = default_variables['default_junos_rpc_timeout']
use_hostname = default_variables['use_hostname']

################################################################################################
# Validate Arguments
###############################################################################################
tag_list = []
###  Known and fixed arguments
if dynamic_args['tag']:
    tag_list = dynamic_args['tag']
else:
    tag_list = [ ".*" ]

if not(dynamic_args['start']):
    print "Mising <start> option, so nothing to do"
    sys.exit(0)



################################################################################################
# open-nti starts here start 
################################################################################################

# Setting up logging directories and files
timestamp = time.strftime("%Y-%m-%d", time.localtime(time.time()))
log_dir = BASE_DIR + "/" + default_variables['log_dir']
logger = logging.getLogger("_open-nti_")
if not os.path.exists(log_dir):
    os.makedirs(log_dir, 0755)
formatter = '%(asctime)s %(name)s %(levelname)s %(threadName)-10s:  %(message)s'
logging.basicConfig(filename=log_dir + "/"+ timestamp + '_open-nti.log',level=logging_level,format=formatter, datefmt='%Y-%m-%d %H:%M:%S')

if dynamic_args['console']:
    print "Console logs enabled"
    console = logging.StreamHandler()
    console.setLevel (logging.DEBUG)
    logging.getLogger('').addHandler(console)

###############

#  LOAD all credentials in a dict

credentials_yaml_file = BASE_DIR + "/data/" + default_variables['credentials_file']
credentials = {}
logger.debug('Importing credentials file: %s ',credentials_yaml_file)
with open(credentials_yaml_file) as f: 
    credentials = yaml.load(f)

#  LOAD all hosts with their tags in a dic

hosts_yaml_file = BASE_DIR + "/data/" + default_variables['hosts_file']
hosts = {}
logger.debug('Importing host file: %s ',hosts_yaml_file)
with open(hosts_yaml_file) as f: 
    hosts = yaml.load(f)

#  LOAD all commands with their tags in a dict

commands_yaml_file = BASE_DIR + "/data/" + default_variables['commands_file']
commands = []
logger.debug('Importing commands file: %s ',commands_yaml_file)
with open(commands_yaml_file) as f: 
    for document in yaml.load_all(f):
        commands.append(document)    

general_commands = commands[0]

#  LOAD all parsers

junos_parsers = []
junos_parsers_yaml_files = os.listdir(BASE_DIR + "/" + default_variables['junos_parsers_dir'])
logger.debug('Importing junos parsers file: %s ',junos_parsers_yaml_files)
for junos_parsers_yaml_file in junos_parsers_yaml_files:
    with open(BASE_DIR + "/" + default_variables['junos_parsers_dir'] + "/"  + junos_parsers_yaml_file) as f: 
        junos_parsers.append(yaml.load(f))

pfe_parsers = []
pfe_parsers_yaml_files = os.listdir(BASE_DIR + "/" + default_variables['pfe_parsers_dir'])
logger.debug('Importing pfe parsers file: %s ',pfe_parsers_yaml_files)
for pfe_parsers_yaml_file in pfe_parsers_yaml_files:
    with open(BASE_DIR + "/" + default_variables['pfe_parsers_dir'] + "/" + pfe_parsers_yaml_file) as f: 
        pfe_parsers.append(yaml.load(f))

if __name__ == "__main__":


    logger.debug('Getting hosts that matches the specified tags')
    #  Get all hosts that matches with the tags
    target_hosts = get_target_hosts()
    logger.debug('The following hosts are being selected:  %s', target_hosts)

    # Test DB connectivity before starting to collect data
    if check_db_status():
        # Create a list of jobs and then iterate through
        # the number of threads appending each thread to
        # the job list 
        target_hosts_lists = [target_hosts[x:x+len(target_hosts)/max_collector_threads+1] for x in range(0, len(target_hosts), len(target_hosts)/max_collector_threads+1)]
        
        jobs = []
        i=1   
        for target_hosts_list in target_hosts_lists:
            logger.info('Collector Thread-%s scheduled with following hosts: %s', i, target_hosts_list)
            thread = threading.Thread(target=collector, kwargs={"host_list":target_hosts_list})
            jobs.append(thread)
            i=i+1

        # Start the threads 
        for j in jobs:
            j.start()
    
        # Ensure all of the threads have finished
        for j in jobs:
            j.join()
