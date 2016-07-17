#! /usr/local/bin/python

import argparse
from jinja2 import Template
import pprint
import yaml
import logging
from os import path
import os
import re
import json

############################################
### CLI Params
#############################################
parser = argparse.ArgumentParser(description='Process user input')
parser.add_argument("--file", dest="dashboard",
                    help="Definition file for the dashboard to create")
parser.add_argument("--log", dest="log", metavar="LEVEL", default='info',
                    choices=['info', 'warn', 'debug', 'error'],
                    help="Specify the log level ")
args = parser.parse_args()

here = path.abspath(path.dirname(__file__))
pp = pprint.PrettyPrinter(indent=4)

############################################
### Log level configuration
#############################################
logger = logging.getLogger( 'opennti' )

if args.log == 'debug':
    logger.setLevel(logging.DEBUG)
elif args.log == 'warn':
    logger.setLevel(logging.WARN)
elif args.log == 'error':
    logger.setLevel(logging.ERROR)
else:
    logger.setLevel(logging.INFO)

logging.basicConfig(format=' %(name)s - %(levelname)s - %(message)s')

############################################
### Load main configuration file
#############################################

TEMPLATES_DIR = 'templates/'
ROWS_DIR = TEMPLATES_DIR +'rows/'
GRAPHS_DIR = TEMPLATES_DIR + 'graphs/'
TEMPLATINGS_DIR = TEMPLATES_DIR + 'templatings/'
ANNOTATIONS_DIR = TEMPLATES_DIR + 'annotations/'

logger.info('Opening Configuration file {0}'.format(args.dashboard))
dashboard = yaml.load(open(args.dashboard))

############################################
### Process ROWS
#############################################

if 'rows' in dashboard.keys():
    dashboard['rows_data'] = ''
    nbr_rows = 0
    panel_id = 1

    for row in dashboard['rows']:
        logger.info('Add Row : {0}'.format(row))
        row_conf = yaml.load(open(ROWS_DIR + row).read())

        row_conf['panels_data'] = ''
        nbr_panels = 0

        if row_conf['panels']['graphs']:
            ## Find panels for this row
            for graph in row_conf['panels']['graphs']:
                logger.info(' - Add Graph :{0}'.format(graph))
                graph_conf = yaml.load(open(GRAPHS_DIR + graph).read())

                ## Insert Graph ID and increment
                graph_conf['id'] = panel_id
                panel_id = panel_id + 1

                logger.debug('  Found Template for graph :{0}'.format(GRAPHS_DIR + graph_conf['template']))
                graph_tpl = open(GRAPHS_DIR + graph_conf['template'])

                ## Find template for this grah and render
                graph_tpl_rdr = Template(graph_tpl.read()).render(graph_conf)

                ## Add template to list of panels
                if nbr_panels > 0:
                    logger.debug('  Not the first panel add a ","')
                    row_conf['panels_data'] = row_conf['panels_data'] + ','
                row_conf['panels_data'] = row_conf['panels_data'] + graph_tpl_rdr
                nbr_panels =+ 1

                ## Check if template is using some templatings and add to the list
                for templating in graph_conf['templatings_used']:
                    if 'templatings' not in dashboard.keys():
                        dashboard['templatings'] = []
                    dashboard['templatings'].append(templating)
                    logger.debug('  Added templating {0} as a requirement'.format(templating))

        ## Render Row and Add it to the dashboard`
        row_tpl = open(ROWS_DIR + row_conf['template'])
        row_tpl_rdr = Template(row_tpl.read()).render(row_conf)

        if nbr_rows > 0:
            logger.debug('Not the first row add a ","')
            dashboard['rows_data'] = dashboard['rows_data'] + ','
        dashboard['rows_data'] = dashboard['rows_data'] + row_tpl_rdr
        nbr_rows =+ 1

#############################################
### Process ANNOTATIONS
#############################################
if 'annotations' in dashboard.keys():
    logger.info('Nothing here yet')

#############################################
### Process TAGS
#############################################
if 'tags' in dashboard.keys():

    tags = '","'.join(map(str, dashboard['tags']))
    dashboard['tags_data'] = '"' + tags + '"'
    logger.info('Add Tag(s) : {0}'.format(dashboard['tags_data']))

#############################################
### Process TEMPLATINGS
#############################################
if 'templatings' in dashboard.keys():
    dashboard['templatings_data'] = ''
    nbr_templatings = 0

    ## Extract unique values
    list_templatings = set(dashboard['templatings'])

    for templating in list(list_templatings):
        logger.info('Add Templating {0}'.format(templating))
        templating_conf = yaml.load(open(TEMPLATINGS_DIR + templating).read())

        templating_tpl = open(TEMPLATINGS_DIR + templating_conf['template'])
        templating_tpl_rdr = Template(templating_tpl.read()).render(templating_conf)

        ## Add template to list of panels
        if nbr_templatings > 0:
            logger.debug('Not the first templating, add a ","')
            dashboard['templatings_data'] = dashboard['templatings_data'] + ','
        dashboard['templatings_data'] = dashboard['templatings_data'] + templating_tpl_rdr
        nbr_templatings =+ 1

#############################################
### Render Dashboard
#############################################
dashboard_tpl = open(TEMPLATES_DIR + dashboard['template'])
dashboard_tpl_rdr = Template(dashboard_tpl.read().decode("utf8")).render(dashboard)

dashboard_file_name = dashboard['title'].lower() + '.json'
dashboard_file_name = re.sub(r'\s', '_', dashboard_file_name)

logger.info('Dashboard File name : {0}'.format(dashboard_file_name))

with open(dashboard_file_name, "w") as text_file:
    text_file.write(dashboard_tpl_rdr)
    # json.dump(dashboard_json, text_file, indent=2)

## Validate Json
dashboard_json = json.loads(dashboard_tpl_rdr)
