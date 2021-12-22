# version 1.1.1.
# to support all the sensors at the same time
# To support my-time in the output

import sys,subprocess,os,shutil
import time,math
from datetime import datetime
from influxdb import InfluxDBClient

'''
Create database
'''
user = "influx"
password = "influx"
dbname = "performance"
host = "localhost"
port = 8086

client = InfluxDBClient(host, port, user, password, dbname)
client.drop_database(dbname)
client.create_database(dbname)

def percentile(data, percentile):
    size = len(data)
    return sorted(data)[int(math.ceil((size * percentile) / 100)) - 1]

def parse_input_file(filename):
    f = open(inputfile)
    line = f.readline()

    while line:
        if "system_id: " in line:
            routername = ''.join(line.split()[-1:])
        if " component_id:" in line:
            component_id = ''.join(line.split()[-1:])
        if "path: sensor" in line:
            re_creation_ts = "N/A"
            my_sensor = ''.join(line.split()[-1:])
            my_sensor_id = ''.join(line.split(":")[3]).strip()
        
            line = f.readline()
            if "sequence_number" in line:
                seq = ''.join(line.split()[-1:])
                line = f.readline()
                while line:
                    if "timestamp:" in line:
                        producer_ts = ''.join(line.split()[-1:])
                    if "key: __timestamp__" in line:
                        line = f.readline()
                        grpc_ts = ''.join(line.split()[-1:])
                    elif "key: __junos_re_stream_creation_timestamp__" in line:
                        line = f.readline()
                        re_creation_ts = ''.join(line.split()[-1:])
                        break
                    else:
                        line = f.readline()
                        if "system_id: " in line:
                            break
                ilatency = int(grpc_ts) - int(producer_ts)
                temp = my_sensor + "_" + component_id + "," + seq + "," + producer_ts + "," + grpc_ts + "," + re_creation_ts + "," + str(ilatency) + "\n"
                yield temp
            else:
                line = f.readline()
        else:
            line = f.readline()

log_file = "ocst-logs/log"
result_file = "ocst-result/res"

if os.path.exists("ocst-logs"):
    shutil.rmtree("ocst-logs")
if os.path.exists("ocst-result"):
    shutil.rmtree("ocst-result")
os.makedirs("ocst-logs")
os.makedirs("ocst-result")

inputfile = sys.argv[1]
res = open('ocst-logs/log-all-sensor.csv', 'w')
data = parse_input_file(inputfile)
for item in data:
    res.write(item)
res.close()

s = subprocess.Popen(["cat ocst-logs/log-all-sensor.csv | awk -F \",\" '{ print $1 }' | sort | uniq"], shell=True, stdout=subprocess.PIPE).stdout
all_sensors = s.read().splitlines()

for sensor in all_sensors:
    sensor_bak = sensor.replace("/","_")
    sensor_bak = sensor_bak.replace(":","")
    filename = log_file + "_" + sensor_bak + ".csv"
    res = open(filename, 'w')
    res.write("Sensor,Seq_no,Producer_TS,Grpc_TS,RE_creation_ts,iLatency\n")
    res.close()    
    cmd = "grep " + sensor + " ocst-logs/log-all-sensor.csv >>" + filename
    s = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout

time.sleep(5)
    
print "KPI-4 iLatency, unit ms"
print "Sensor, Min, 50%, 60%, 70%, 80%, 85%, 90%, 95%, 96%, 97%, 98%, 99%, 100%, average"

for sensor in all_sensors:
    #print "Processing sensor: %s" % sensor
    json_point = []
    kpi4_list = []
    sensor_id = sensor.split(":")[0]
    sensor_bak = sensor.replace("/","_")
    sensor_bak = sensor_bak.replace(":","")
    filename = log_file + "_" + sensor_bak + ".csv"
    res_name = result_file + "_" + sensor_bak + ".csv"
    res = open(res_name, "a")
    
    # Don't write average for now
    temp = "Sensor,Seq_no,Producer_TS,Grpc_TS,RE_creation_ts,Wrap_No,KPI-2,Is_Wrap,KPI-3,Time/wrap,Pkt/wrap\n"
    res.write(temp)
    
    start_grpc_ts = 0
    start_producer_ts = 0
    
    wrap = 0
    is_1st_seq = True
    previous_wrap_ts = 0
    previous_wrap_seq = 0
    
    previous_re_ts = 0
    previous_producer_ts = 0
    previous_grpc_ts = 0
    
    for line in open(filename):
        if "sensor_" in line:
            sens = line.split(",")[0] 
            seq = int(line.split(",")[1])
            pro_ts = int(line.split(",")[2])
            grpc_ts = int(line.split(",")[3])
            if line.split(",")[4] == "N/A":
                re_ts = 0
            else:
                re_ts = int(line.split(",")[4])
            ilatency = int(line.split(",")[5])

            if is_1st_seq:
                start_grpc_ts = grpc_ts
                start_producer_ts = pro_ts
                wrap = 1
                previous_wrap_seq = seq
                previous_wrap_ts = pro_ts
                previous_re_ts = re_ts
                previous_grpc_ts = grpc_ts
                previous_producer_ts = pro_ts
                is_1st_seq = False
            else:
                '''
                for KPI-2 inter-packet-delay
                '''
                packetdelay = pro_ts - previous_producer_ts
                if re_ts != previous_re_ts:
                    wrap = wrap + 1
                    pkt_per_wrap = seq - previous_wrap_seq
                    if pkt_per_wrap == 1:
                        time_per_wrap = pro_ts - previous_wrap_ts
                    else:
                        time_per_wrap = previous_producer_ts - previous_wrap_ts
                    
                    '''
                    for KPI-3, Wrap time and skew
                    if "interface" in sensor:
                        
                        #if it's a new wrap, previous_grpc_ts should be the last packet of previous wrap
                        #calculate how many reporting-interval for previous wrap
                        grpc_wrap_skew = grpc_ts - ( (previous_grpc_ts - start_grpc_ts) // 2000 + 1 ) * 2000 - start_grpc_ts
                        producer_skew = pro_ts - ( (previous_producer_ts - start_producer_ts) // 2000 + 1 ) * 2000 - start_producer_ts
                    else:
                        grpc_wrap_skew = grpc_ts - ( (previous_grpc_ts - start_grpc_ts) // 10000 + 1 ) * 10000 - start_grpc_ts
                        producer_skew = pro_ts - ( (previous_producer_ts - start_producer_ts) // 10000 + 1 ) * 10000 - start_producer_ts
                    
                    #User relative time skew
                    if "interface" in sensor:
                        
                        #if it's a new wrap, previous_grpc_ts should be the last packet of previous wrap
                        #calculate how many reporting-interval for previous wrap
                        grpc_wrap_skew = grpc_ts - (2000 - ((previous_grpc_ts - start_grpc_ts) % 2000))  - previous_grpc_ts
                        producer_skew = pro_ts - (2000 - ((previous_producer_ts - start_producer_ts) % 2000))  - previous_producer_ts
                    else:
                        grpc_wrap_skew = grpc_ts - (10000 - ((previous_grpc_ts - start_grpc_ts) % 10000))  - previous_grpc_ts
                        producer_skew = pro_ts - (10000 - ((previous_producer_ts - start_producer_ts) % 10000))  - previous_producer_ts
                    '''
                    producer_skew = pro_ts - start_producer_ts
                    if ( grpc_ts - start_grpc_ts ) >= 600000:
                        temp= "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (sensor,seq,pro_ts, grpc_ts, re_ts, wrap, "N/A", "Y", producer_skew, time_per_wrap, pkt_per_wrap)
                        res.write(temp)
                        kpi4_list.append(ilatency)

                        json_point.append(
                            {
                                "measurement": "performance",
                                "tags": {
                                    "sensor": sensor,
                                },
                                "time": grpc_ts,
                                "fields": {
                                    "producer": producer_skew,
                                    "packetdelay": 0,
                                    "ilatency": ilatency,
                                    "wraptime": time_per_wrap,
                                    "packet": pkt_per_wrap
                                }
                            }
                        )

                        if len(json_point) >=10000:
                            client.write_points(json_point,time_precision="ms")
                            #print "Write database %s datapoints" % (len(json_point))
                            json_point = []

                    previous_wrap_seq = seq
                    previous_wrap_ts = pro_ts
                    
                else:
                    if ( grpc_ts - start_grpc_ts ) >= 600000:
                        temp = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (sensor,seq,pro_ts, grpc_ts, re_ts, wrap, packetdelay, "N/A", "N/A", "N/A", "N/A")
                        res.write(temp)
                        kpi4_list.append(ilatency)
                        json_point.append(
                            {
                                "measurement": "performance",
                                "tags": {
                                    "sensor": sensor,
                                },
                                "time": grpc_ts,
                                "fields": {
                                    "producer": 0,
                                    "packetdelay": packetdelay,
                                    "ilatency": ilatency,
                                    "wraptime": 0,
                                    "packet": 0
                                }
                            }
                        )

                        if len(json_point) >=10000:
                            client.write_points(json_point,time_precision="ms")
                            #print "Write database %s datapoints" % (len(json_point))
                            json_point = []

                previous_grpc_ts = grpc_ts
                previous_producer_ts = pro_ts
                previous_re_ts = re_ts
    client.write_points(json_point,time_precision="ms")
    #print "Write database %s datapoints" % (len(json_point))
    json_point = []

    if len(kpi4_list) > 0:
        max_latency = max(kpi4_list)
        min_latency = min(kpi4_list)
        
        p50 = percentile(kpi4_list, 50)
        p60 = percentile(kpi4_list, 60)
        p70 = percentile(kpi4_list, 70)
        p80 = percentile(kpi4_list, 80)
        p85 = percentile(kpi4_list, 85)
        p90 = percentile(kpi4_list, 90)
        p95 = percentile(kpi4_list, 95)
        p96 = percentile(kpi4_list, 96)
        p97 = percentile(kpi4_list, 97)
        p98 = percentile(kpi4_list, 98)
        p99 = percentile(kpi4_list, 99)
        p100 = percentile(kpi4_list, 100)
        
        print "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (sensor, p50, p60, p70, p80, p85, p90, p95, p96, p97, p98, p99, p100)
    else:
        print "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (sensor, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

'''
for KPI-3 wrap time

print "KPI-3 Wrap time, unit ms"
print "Sensor, Min, 50%, 60%, 70%, 80%, 85%, 90%, 95%, 100%, average"
for sensor in all_sensors:
    #print "Processing sensor: %s" % sensor
    json_point = []
    sensor_id = sensor.split(":")[0]
    sensor_bak = sensor.replace("/","_")
    res_name = result_file + "_" + sensor_bak + ".csv"
    cmd = "cat " + res_name + " | grep -v \"N/A\" | grep Y | awk -F \",\" '{ print $(NF-1) }'"
    s = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout
    all_wraptime = s.read().splitlines()
    
    if len(all_wraptime) == 0:
        continue
    
    for i in range(len(all_wraptime)):
        all_wraptime[i]=int(all_wraptime[i])
    
    max_latency = max(all_wraptime)
    min_latency = min(all_wraptime)
    average_latency = sum(all_wraptime)/len(all_wraptime)    
    
    p50 = percentile(all_wraptime, 50)
    p60 = percentile(all_wraptime, 60)
    p70 = percentile(all_wraptime, 70)
    p80 = percentile(all_wraptime, 80)
    p85 = percentile(all_wraptime, 85)
    p90 = percentile(all_wraptime, 90)
    p95 = percentile(all_wraptime, 95)
    p100 = percentile(all_wraptime, 100)
    
    print "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (sensor, min_latency, p50, p60, p70, p80, p85, p90, p95, p100, average_latency)
'''
    
exit()