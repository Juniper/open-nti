# This script has to use the csv data provided by the new collector with following command:
# # ./jtimon-linux-x86_64 --csv-stats --config google-d91.json --stats 2 --log ./d91-kpis.log --max-run 7200
# python all-kpi-nodb.py d91-kpis.log > result.csv
# Then download result.csv to your local PC and check
# ver 20180524, add seq 0 and Sensor type 


import sys,subprocess,os,shutil
import time,math
from datetime import datetime

inputfile = sys.argv[1]


init_delay = 0
log_file = "ocst-logs/log"
result_file = "ocst-result/res"
all_sensors = []


def percentile(data, percentile):
    size = len(data)
    return sorted(data)[int(math.ceil((size * percentile) / 100)) - 1]

def parse_input_file(filename):
    f = open(inputfile)

    for line in f:
        if "sensor_" in line:
            sensor_name = ''.join(line.split(",")[0])
            Seq_no = ''.join(line.split(",")[1])
            com_id = ''.join(line.split(",")[2])
            sub_com_id = ''.join(line.split(",")[3])
            packet_size = ''.join(line.split(",")[4])
            Producer_TS = ''.join(line.split(",")[5])
            Grpc_TS = ''.join(line.split(",")[6])
            RE_creation_ts = ''.join(line.split(",")[7])
            RE_get_ts = ''.join(line.split(",")[8])

            new_name = sensor_name + "_" + com_id
            if new_name not in all_sensors:
                all_sensors.append(new_name)

            temp = sensor_name + "_" + com_id + "," + Seq_no + "," + packet_size + ", " + Producer_TS + "," + Grpc_TS + "," + RE_creation_ts + "," + RE_get_ts
            yield temp

if os.path.exists("ocst-logs"):
    shutil.rmtree("ocst-logs")
if os.path.exists("ocst-result"):
    shutil.rmtree("ocst-result")
os.makedirs("ocst-logs")
os.makedirs("ocst-result")

inputfile = sys.argv[1]
res = open('ocst-logs/all-logs.csv', 'w')
data = parse_input_file(inputfile)
for item in data:
    res.write(item)
res.close()

for sensor in all_sensors:
    sensor_id = sensor.split(":")[0]
    sensor_name = sensor.split(":")[2]
    pfe_id = sensor.split(":")[-1]
    sensor_bak = sensor_id + sensor_name + pfe_id
    sensor_bak = sensor_bak.replace("/","_")
    filename = log_file + "_" + sensor_bak + ".csv"
    res = open(filename, 'w')
    res.write("Sensor,Seq_no,KPI-1,Producer_TS,Grpc_TS,RE_creation_ts,Get_ts\n")
    res.close()    
    cmd = "grep " + sensor_id + " ocst-logs/all-logs.csv | grep " + pfe_id + ", >>" + filename
    s = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout

time.sleep(3)


time.sleep(3)

print "KPI-4, Type, Sensor, 50%, 60%, 70%, 80%, 85%, 90%, 95%, 96%, 97%, 98%, 99%, 100%"    
print "KPI-1, Type, Sensor, 10%, 20%, 30%, 40%, 50%, 60%, 70%, 80%, 85%, 90%, 95%, 100%"

for sensor in all_sensors:
    #print "Processing sensor: %s" % sensor
    json_point = []
    kpi4_list = []
    kpi1_list = []
    sensor_id = sensor.split(":")[0]
    sensor_name = sensor.split(":")[2]
    pfe_id = sensor.split(":")[-1]
    sensor_bak = sensor_id + sensor_name + pfe_id
    sensor_bak = sensor_bak.replace("/","_")
    filename = log_file + "_" + sensor_bak + ".csv"
    res_name = result_file + "_" + sensor_bak + ".csv"
    res = open(res_name, "a")
    
    # Don't write average for now
    temp = "Sensor,Seq_no,Producer_TS,Grpc_TS,RE_creation_ts,Get_ts, KPI-1,Wrap_No,KPI-2,Is_Wrap,Wrap_Time_Skew,KPI-3,Pkt/wrap,KPI-4\n"
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
            packet_size = int(line.split(",")[2])
            pro_ts = int(line.split(",")[3])
            grpc_ts = int(line.split(",")[4])
            re_ts = int(line.split(",")[5])
            get_ts = int(line.split(",")[6])
            ilatency = grpc_ts - pro_ts
            if "isis" in sensor_name:
                ilatency = 0
            kpi1_list.append(packet_size)

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
                temp= "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (sensor,seq,pro_ts, grpc_ts, re_ts, get_ts, packet_size, wrap, "N/A", "Y", "N/A", "N/A", "N/A", ilatency)
                res.write(temp)
                kpi4_list.append(ilatency)
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
                    if ( grpc_ts - start_grpc_ts ) >= init_delay:
                        temp= "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (sensor,seq,pro_ts, grpc_ts, re_ts, get_ts, packet_size, wrap, packetdelay, "Y", producer_skew, time_per_wrap, pkt_per_wrap, ilatency)
                        res.write(temp)
                        kpi4_list.append(ilatency)


                    previous_wrap_seq = seq
                    previous_wrap_ts = pro_ts
                    
                else:
                    if ( grpc_ts - start_grpc_ts ) >= init_delay:
                        temp = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (sensor,seq,pro_ts, grpc_ts, re_ts, get_ts, packet_size, wrap, packetdelay, "N/A", "N/A", "N/A", "N/A", ilatency)
                        res.write(temp)
                        kpi4_list.append(ilatency)


                previous_grpc_ts = grpc_ts
                previous_producer_ts = pro_ts
                previous_re_ts = re_ts

    if ":PFE_" in sensor:
        kpi1_hdr = "KPI-1, PFE"
        kpi4_hdr = "KPI-4, PFE"
    else:
        kpi1_hdr = "KPI-1, RE"
        kpi4_hdr = "KPI-4, RE"
        
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
        
        print "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (kpi4_hdr, sensor, p50, p60, p70, p80, p85, p90, p95, p96, p97, p98, p99, p100)
    else:
        print "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (kpi4_hdr, sensor, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
    if len(kpi1_list) > 0:
        max_size = max(kpi1_list)
        min_size = min(kpi1_list)

        p50 = percentile(kpi1_list, 10)
        p60 = percentile(kpi1_list, 20)
        p70 = percentile(kpi1_list, 30)
        p80 = percentile(kpi1_list, 40)
        p85 = percentile(kpi1_list, 50)
        p90 = percentile(kpi1_list, 60)
        p95 = percentile(kpi1_list, 70)
        p96 = percentile(kpi1_list, 80)
        p97 = percentile(kpi1_list, 85)
        p98 = percentile(kpi1_list, 90)
        p99 = percentile(kpi1_list, 95)
        p100 = percentile(kpi1_list, 100)
        
        
        print "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (kpi1_hdr, sensor, p50, p60, p70, p80, p85, p90, p95, p96, p97, p98, p99, p100)
    else:
        print "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (kpi1_hdr, sensor, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

#for KPI-1 Packet per wrap

print "KPI-1 Packet per Wrap"
print "Sensor, Min, 50%, 60%, 70%, 80%, 85%, 90%, 95%, 100%, average"
for sensor in all_sensors:
    #print "Processing sensor: %s" % sensor
    json_point = []
    sensor_id = sensor.split(":")[0]
    sensor_name = sensor.split(":")[2]
    pfe_id = sensor.split(":")[-1]
    sensor_bak = sensor_id + sensor_name + pfe_id
    sensor_bak = sensor_bak.replace("/","_")

    res_name = result_file + "_" + sensor_bak + ".csv"
    cmd = "cat " + res_name + " | grep -v \"N/A\" | grep Y | awk -F \",\" '{ print $(NF-1) }'"
    s = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout
    all_wraptime = s.read().splitlines()
    
    if len(all_wraptime) == 0:
        if "_65535" in sensor:
            print "%s, N/A, N/A, N/A, N/A, N/A, N/A, N/A, N/A, N/A, N/A" % (sensor)
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

#for KPI-3 wrap time

print "KPI-3 Wrap time, unit ms"
print "Sensor, Min, 50%, 60%, 70%, 80%, 85%, 90%, 95%, 100%, average"
for sensor in all_sensors:
    #print "Processing sensor: %s" % sensor
    json_point = []
    sensor_id = sensor.split(":")[0]
    sensor_name = sensor.split(":")[2]
    pfe_id = sensor.split(":")[-1]
    sensor_bak = sensor_id + sensor_name + pfe_id
    sensor_bak = sensor_bak.replace("/","_")

    res_name = result_file + "_" + sensor_bak + ".csv"
    cmd = "cat " + res_name + " | grep -v \"N/A\" | grep Y | awk -F \",\" '{ print $(NF-2) }'"
    s = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout
    all_wraptime = s.read().splitlines()
    
    if len(all_wraptime) == 0:
        if "_65535" in sensor:
            print "%s, N/A, N/A, N/A, N/A, N/A, N/A, N/A, N/A, N/A, N/A" % (sensor)
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
    
exit()