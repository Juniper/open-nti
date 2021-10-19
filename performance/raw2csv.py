import sys,subprocess,os,shutil
import time,math
from datetime import datetime

def parse_input_file(filename):
    f = open(inputfile)
    line = f.readline()
    re_creation_ts = "N/A"
    producer_ts = "N/A"
    sequence_number = "N/A"
    
    while line:
        print "processing:" + line
        if "system_id: " in line:
            routername = ''.join(line.split()[-1:])
            prefix = ""
        elif ("component_id:" in line) and ("sub_component" not in line):
            component_id = ''.join(line.split()[-1:])
        elif "sub_component" in line:
            sub_component_id = ''.join(line.split()[-1:])
        elif "path: sensor" in line:
            my_sensor = ''.join(line.split()[-1:])
        elif "sequence_number" in line:
            seq = ''.join(line.split()[-1:])
        elif "timestamp:" in line:
            producer_ts = ''.join(line.split()[-1:])    
        elif "sync_response:" in line:
            sync_response = ''.join(line.split()[-1:])    
            line = f.readline()

            while line:
                if "key: __prefix__" in line:
                    line = f.readline()
                    prefix = ''.join(line.split()[-1:])
                elif "key:" in line:
                    key = ''.join(line.split()[-1:])
                    whole_path = prefix + key
                    line = f.readline()
                    if "_value:" in line:
                        vale = ''.join(line.split()[-1:])
                        temp = routername + "," + my_sensor + "," + component_id + "," + sub_component_id + "," + seq + "," + producer_ts + "," + sync_response + "," + whole_path + "," + vale + "\n"
                    else:
                        temp = "ERROR, No value detected!!"
                    res.write(temp)

                line = f.readline()
                if "system_id: " in line:
                    break
        line = f.readline()

inputfile = sys.argv[1]
res = open('kvs.csv', 'w')
data = parse_input_file(inputfile)
res.close()