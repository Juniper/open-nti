#!/usr/bin/env python
#
# Copyright (c) Juniper Networks, Inc., 2015-2016.
# All rights reserved.
#

from crontab import CronTab
import re
import sys,getopt,argparse,os.path, math

parser = argparse.ArgumentParser(description='./startcron.py -a add/delete -t 10 (in secs) -c command_to_run')
parser.add_argument('-a','--action', help='add, delete, show', required=True)
parser.add_argument('-c','--command', help='command to add/delete', required=True)
parser.add_argument('-t','--time', help='Time interval to run cron', required=False)
args = parser.parse_args()

try:
    args.action
except ActionNotDefined:
    print("./startcron.py -a add/delete must be defined")

if (args.action == "add"):
    try:
        args.time
    except TimeNotDefined:
        print("./startcron.py -t 10m or 1h must be defined")

    try:
        args.command
    except CommandNotDefined:
        print("./startcron.py -c command must be defined")

    time_min_regex = "(\d+)m"
    time_hours_regex = "(\d+)h"
    if (re.search(time_min_regex, args.time)):
        time = int(re.sub(r'\D', "", args.time))
        if (time < 1 or time > 59):
            print("Incorrect -t value " + str(time) + " for minutes. Value must be between 1 and 59.")
            exit()
    elif (re.search(time_hours_regex, args.time)):
        time = int(re.sub(r'\D', "", args.time))
        if (time < 0 or time > 23):
            print("Incorrect -t format for hours. Value must be between 1 and 23.")
            exit()
    else:
        print("Incorrect -t format " + str(args.time) + ". Format: -t 10m or 1h")
        exit()

cron = CronTab(user='root')

if (args.action == "add"):
    cron_job = cron.new(args.command)
    if (re.search(time_min_regex, args.time)):
         cron_job.minute.every(time)
    else:
        cron_job.every(time).hours()
    #writes content to crontab
    print(cron.render())
    cron.write()
elif (args.action == "delete"):
    #cron.remove_all(command=args.command)
    for cron_job in cron.find_command(args.command):
        print(cron_job)
        cron.remove(cron_job)
        cron.write()
else:
    if (args.command == "all"):
        for job in cron:
            print(job)
    else:
        for cron_job in cron.find_command(args.command):
            print(cron_job)
