# This script has to use the csv data provided by the new collector with following command:
# gRPC test: ./jtimon-linux-x86_64 --csv-stats --config google-d91.json --stats 2 --log ./d91-kpis.log --max-run 7200
# gNMI test: ./jtimon_gnmi --gnmi --print-kv --config r2-simple.json --log r2.gnmi.kv.log --max-run 7200
# python all-kpis-nodb.py [log ouput from above command] > result.csv
# Then download result.csv to your local PC and check
# ver 20180524, add seq 0 and Sensor type 
# Ver 20180604, better format, and add packet per wrap
# Ver 20190301, Support Brackla
# Ver 20190405, Better format to sort based on KPI and Sensor type
# Ver 20190412, support gNMI nano seconds and gRPC milli-seconds at the same time
# Ver 20191016, add init_sync support
# Ver 20200715, more init_sync support and KPI-7: init_sync time
# Ver 20200717, no feature change. Performance enhancement on log processing.
# Ver 20200724, fix a bug regarding to KPI-7 calculation

import sys,subprocess,os,shutil
import time,math
from datetime import datetime
from audioop import reverse

inputfile = sys.argv[1]

#write result into a local file.
dt = datetime.now().strftime('%Y%m%d_%H%M%S')
kpi_result_filename = 'KPI_result_' + dt + '.csv'

kpi_result = open(kpi_result_filename, "w")

init_delay = 0
log_file = "ocst-logs/log"
result_file = "ocst-result/res"
init_file = "ocst-init/init_sync"
all_sensors = []


def percentile(data, percentile):
    size = len(data)
    return sorted(data)[int(math.ceil((size * percentile) / 100)) - 1]

'''
def parse_input_file(filename):
    f = open(inputfile)

    for line in f:
        if "sensor_" in line:
            sensor_name = ''.join(line.split(",")[0])
            Seq_no = ''.join(line.split(",")[1])
            com_id = ''.join(line.split(",")[2])
            sub_com_id = ''.join(line.split(",")[3])
            packet_size = ''.join(line.split(",")[4])
            Producer_TS = int(''.join(line.split(",")[5]))
            Grpc_TS = int(''.join(line.split(",")[6]))
            RE_creation_ts = int(''.join(line.split(",")[7]))
            RE_get_ts = int(''.join(line.split(",")[8]))

            # Handle gNMI nano seconds here.
            #sensor-path,sequence-number,component-id,sub-component-id,packet-size,p-ts,e-ts,re-stream-creation-ts,re-payload-get-ts
            #gNMI: sensor_1034_2_1:/interfaces/interface/state/:/interfaces/interface/state/:mib2d,0,65535,0,578,1,555,126,443,225,906,901,1555126443248000000,0,0
            #gRPC: sensor_1000_2_1:/interfaces/interface/state/:/interfaces/interface/state/:mib2d,0,65535,0,189,1,550,603,559,107,1550603559116,1550603559058,1550603559060
            if Producer_TS > math.pow(10,13):
                Producer_TS = str(int(Producer_TS / 1000000))
            else:
                Producer_TS = str(Producer_TS)
            if Grpc_TS > math.pow(10,13):
                Grpc_TS = str(int(Grpc_TS / 1000000))
            else:
                Grpc_TS = str(Grpc_TS)
            if RE_creation_ts > math.pow(10,13):
                RE_creation_ts = str(int(RE_creation_ts / 1000000))
            else:
                RE_creation_ts = str(RE_creation_ts)
            if RE_get_ts > math.pow(10,13):
                RE_get_ts = str(int(RE_get_ts / 1000000))
            else:
                RE_get_ts = str(RE_get_ts)
                
            new_name = sensor_name + "_" + com_id
            if new_name not in all_sensors:
                all_sensors.append(new_name)

            temp = sensor_name + "_" + com_id + "," + Seq_no + "," + packet_size + ", " + Producer_TS + "," + Grpc_TS + "," + RE_creation_ts + "," + RE_get_ts + "\n"
            yield temp
'''


def parse_input_file(filename):
    f = open(inputfile)

    # Raw data: sensor_1019:/junos/services/label-switched-path/usage/:/junos/services/label-switched-path\
    # /usage/:PFE,2097152,0,0,421,1594838958927000000,1594838959003000000,0,0
    for line in f:
        if "sensor_" in line:
            sensor_name = line.split(",")[0]
            Seq_no = line.split(",")[1]
            com_id = line.split(",")[2]
            sub_com_id = line.split(",")[3]
            packet_size = line.split(",")[4]
            Producer_TS = line.split(",")[5]
            Grpc_TS = line.split(",")[6]
            RE_creation_ts = line.split(",")[7]
            RE_get_ts = line.split(",")[8]

            # Handle gNMI nano seconds here.
            # sensor-path,sequence-number,component-id,sub-component-id,packet-size,p-ts,e-ts,re-stream-creation-ts,re-payload-get-ts
            # gNMI: sensor_1034_2_1:/interfaces/interface/state/:/interfaces/interface/state/:mib2d,0,65535,0,578,1,555,126,443,225,906,901,1555126443248000000,0,0
            # gRPC: sensor_1000_2_1:/interfaces/interface/state/:/interfaces/interface/state/:mib2d,0,65535,0,189,1,550,603,559,107,1550603559116,1550603559058,1550603559060
            if len(Producer_TS) == 19:
                Producer_TS = Producer_TS[0:13]
                Grpc_TS = Grpc_TS[0:13]
                RE_creation_ts = RE_creation_ts[0:13]
            # RE_get_ts is the last string of the line. strip from 0:13 can cause "\n" being removed. this will cause log file format issue.
            if int(RE_get_ts) != 0:
                RE_get_ts = RE_get_ts[0:13] + "\n"

            new_name = sensor_name + "_" + com_id
            if new_name not in all_sensors:
                all_sensors.append(new_name)

            temp = new_name + "," + Seq_no + "," + packet_size + "," + Producer_TS + "," + Grpc_TS + "," + RE_creation_ts + "," + RE_get_ts
            yield temp

print "Clean up local directories"
print "*** KPI data will be written in local file: " + kpi_result_filename + "      ***"
print "*** Sensor data raw log:     'ocst-logs' ***"
print "*** Sensor Init Sync data:   'ocst-init' ***"
print "*** Sensor KPI results:      'ocst-result'   ***"
print "*** Please copy above files/folders to local PC for analysis                     ***"

if os.path.exists("ocst-logs"):
    shutil.rmtree("ocst-logs")
if os.path.exists("ocst-result"):
    shutil.rmtree("ocst-result")
if os.path.exists("ocst-init"):
    shutil.rmtree("ocst-init")
os.makedirs("ocst-logs")
os.makedirs("ocst-result")
os.makedirs("ocst-init")

print "Processing collected data"
start_time = time.time()
inputfile = sys.argv[1]
res = open('ocst-logs/all-logs.csv', 'w')
data = parse_input_file(inputfile)
for item in data:
    if item == "\n":
        print "Error"
        continue
    res.write(item)
res.close()
print "Time spent: %s seconds" % (time.time() - start_time)

'''
all_sensors format:
sensor_1030:/nd6-information/ipv6/neighbors/neighbor/state/:/nd6-information/ipv6/neighbors/neighbor/state/:mib2d_65535
sensor_1019:/junos/services/label-switched-path/usage/:/junos/services/label-switched-path/usage/:PFE_0
sensor_1023:/junos/system/linecard/optics/:/junos/system/linecard/optics/:PFE_0
sensor_1022:/junos/system/linecard/npu/memory/:/junos/system/linecard/npu/memory/:PFE_0
sensor_1021:/junos/system/linecard/firewall/:/junos/system/linecard/firewall/:PFE_0
sensor_1024:/junos/system/linecard/packet/usage/:/junos/system/linecard/packet/usage/:PFE_0
'''

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

#define a dict to store filename
sensor_filename = {}
#define a dict to store file handler
sensor_handler = {}

for sensor in all_sensors:
    sensor_id = sensor.split(":")[0]
    sensor_name = sensor.split(":")[2]
    pfe_id = sensor.split(":")[-1]
    sensor_bak = sensor_id + sensor_name + pfe_id
    sensor_bak = sensor_bak.replace("/", "_")
    filename = log_file + "_" + sensor_bak + ".csv"

    #initialize filename dict and file handler dict
    sensor_filename[sensor] = filename
    res = open(filename, 'a')
    sensor_handler[sensor] = res

start_time = time.time()

f = open('ocst-logs/all-logs.csv')
print "Processing log data for each sensor"

for line in f:
    sensor = line.split(',')[0]
    sensor_handler[sensor].write(line)

#close all file handlers after writing contents
for sensor in all_sensors:
    sensor_handler[sensor].close()

# Old code. It's really slow
'''
for line in f:
    for sensor in all_sensors:
        if sensor in line:
            sensor_id = sensor.split(":")[0]
            sensor_name = sensor.split(":")[2]
            pfe_id = sensor.split(":")[-1]
            sensor_bak = sensor_id + sensor_name + pfe_id
            sensor_bak = sensor_bak.replace("/","_")
            filename = log_file + "_" + sensor_bak + ".csv"
            res = open(filename, 'a')            
            res.write(line)
            res.close()
'''
# Old code end.

print "Time spent: %s seconds" % (time.time() - start_time)

#time.sleep(3)
#all_sensors.sort()

# Seperate Init_Sync packets into another file. Right now Init_sync packets are mixed together with streaming packets.
print "Processing Init_Sync Packets"
for sensor in all_sensors:
    #print "Processing sensor: %s" % sensor
    json_point = []
    sensor_id = sensor.split(":")[0]
    sensor_name = sensor.split(":")[2]
    pfe_id = sensor.split(":")[-1]
    sensor_bak = sensor_id + sensor_name + pfe_id
    sensor_bak = sensor_bak.replace("/","_")
    filename = log_file + "_" + sensor_bak + ".csv"
    init_name = init_file + "_" + sensor_bak + ".csv"
    init = open(init_name, "a")

    init.write("Sensor,Seq_no,KPI-1,Producer_TS,Grpc_TS,RE_creation_ts,Get_ts\n")

    for line in open(filename):
        if "sensor_" in line:
            sens = line.split(",")[0]
            seq = int(line.split(",")[1])

            # Should not use sequence numbers starting >=2097152 for this calculation.
            if seq >= 2097152:
                init.write(line)
    init.close()

# write into individual result file
print "Write to result files"
for sensor in all_sensors:
    print "Processing sensor: %s" % sensor
    json_point = []
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
            
            #Should not use sequence numbers starting >=2097152 for this calculation.
            if seq >= 2097152:
                continue
            
            packet_size = int(line.split(",")[2])
            pro_ts = int(line.split(",")[3])
            grpc_ts = int(line.split(",")[4])
            re_ts = int(line.split(",")[5])
            get_ts = int(line.split(",")[6])
            ilatency = grpc_ts - pro_ts
            if "isis" in sensor_name:
                ilatency = 0

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
                temp= "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" %\
                      (sensor,seq,pro_ts, grpc_ts, re_ts, get_ts, packet_size, wrap, "N/A", "Y", "N/A", "N/A", "N/A", ilatency)
                res.write(temp)
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
                        temp= "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" %\
                              (sensor,seq,pro_ts, grpc_ts, re_ts, get_ts, packet_size, wrap, packetdelay, "Y", producer_skew, time_per_wrap, pkt_per_wrap, ilatency)
                        res.write(temp)

                    previous_wrap_seq = seq
                    previous_wrap_ts = pro_ts
                    
                else:
                    if ( grpc_ts - start_grpc_ts ) >= init_delay:
                        temp = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" %\
                               (sensor,seq,pro_ts, grpc_ts, re_ts, get_ts, packet_size, wrap, packetdelay, "N/A", "N/A", "N/A", "N/A", ilatency)
                        res.write(temp)

                previous_grpc_ts = grpc_ts
                previous_producer_ts = pro_ts
                previous_re_ts = re_ts
    res.close()

# Calculate KPI 1
print "Write KPI-1 Packet Size Data"
kpi_result.write("KPI-1 Packet Size, unit Bytes\n")
kpi_result.write("KPI-1, Type, Sensor, 10%, 20%, 30%, 40%, 50%, 60%, 70%, 80%, 85%, 90%, 95%, 100%, Pkt/Wrap\n")
print_list = []
for sensor in all_sensors:
    
    kpi1_list = []
    all_wraptime = []
    sensor_id = sensor.split(":")[0]
    sensor_name = sensor.split(":")[2]
    pfe_id = sensor.split(":")[-1]
    sensor_bak = sensor_id + sensor_name + pfe_id
    sensor_bak = sensor_bak.replace("/","_")

    res_name = result_file + "_" + sensor_bak + ".csv"
    f = open(res_name)
    
    for line in f:
        if sensor in line:
            packet_size = int(''.join(line.split(",")[6]))
            kpi1_list.append(packet_size)
            is_wrap = ''.join(line.split(",")[9])
            wrap_number = int(''.join(line.split(",")[7]))
            packet_wrap = ''.join(line.split(",")[12])
            if is_wrap == "Y" and wrap_number > 1:
                all_wraptime.append(packet_wrap)
    
    if len(all_wraptime) > 0:
        for i in range(len(all_wraptime)):
            all_wraptime[i]=int(all_wraptime[i])
        average_pktnum = int(sum(all_wraptime)/len(all_wraptime))
    else:
        average_pktnum = "n/a"    
    
    if ":PFE_" in sensor:
        kpi1_hdr = "KPI-1, PFE"
    else:
        kpi1_hdr = "KPI-1, RE"
        
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

        mylist = [kpi1_hdr, sensor, p50, p60, p70, p80, p85, p90, p95, p96, p97, p98, p99, p100, average_pktnum]
        print_list.append(mylist)
        
        #print "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" %\
        # (kpi1_hdr, sensor, p50, p60, p70, p80, p85, p90, p95, p96, p97, p98, p99, p100, average_pktnum)
    else:
        mylist = [kpi1_hdr, sensor, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        print_list.append(mylist)
        #print "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (kpi1_hdr, sensor, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    f.close()

print_list.sort(key = lambda x: x[0], reverse = True)
for line in print_list:
    kpi_result.write(','.join([str(x) for x in line]))
    kpi_result.write("\n")

print "Write KPI-4 internal Latency Data"
kpi_result.write("\nKPI-4 iLatency, unit ms\n")
kpi_result.write("KPI-4, Type, Sensor, 50%, 60%, 70%, 80%, 85%, 90%, 95%, 96%, 97%, 98%, 99%, 100%\n")
print_list = []  
for sensor in all_sensors:
    
    kpi4_list = []
    
    sensor_id = sensor.split(":")[0]
    sensor_name = sensor.split(":")[2]
    pfe_id = sensor.split(":")[-1]
    sensor_bak = sensor_id + sensor_name + pfe_id
    sensor_bak = sensor_bak.replace("/","_")

    res_name = result_file + "_" + sensor_bak + ".csv"
    f = open(res_name)
    
    for line in f:
        if sensor in line:
            ilatency = int(''.join(line.split(",")[13]))
            kpi4_list.append(ilatency)
    
    if ":PFE_" in sensor:
        kpi4_hdr = "KPI-4, PFE"
    else:
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
        
        mylist = [kpi4_hdr, sensor, p50, p60, p70, p80, p85, p90, p95, p96, p97, p98, p99, p100]
        print_list.append(mylist)
        
        #print "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" %\
        # (kpi4_hdr, sensor, p50, p60, p70, p80, p85, p90, p95, p96, p97, p98, p99, p100)
    else:
        mylist = [kpi4_hdr, sensor, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        print_list.append(mylist)
        #print "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (kpi4_hdr, sensor, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    
    f.close()
    
print_list.sort(key = lambda x: x[0], reverse = True)
for line in print_list:
    kpi_result.write(','.join([str(x) for x in line]))
    kpi_result.write("\n")


#for KPI-1 Packet per wrap
'''
print "KPI-1 Packet per Wrap"
print "Sensor, Min, 50%, 60%, 70%, 80%, 85%, 90%, 95%, 100%, average"
for sensor in all_sensors:
    #print "Processing sensor: %s" % sensor
    all_wraptime = []
    json_point = []
    sensor_id = sensor.split(":")[0]
    sensor_name = sensor.split(":")[2]
    pfe_id = sensor.split(":")[-1]
    sensor_bak = sensor_id + sensor_name + pfe_id
    sensor_bak = sensor_bak.replace("/","_")

    res_name = result_file + "_" + sensor_bak + ".csv"
    
    f = open(res_name)
 
    for line in f:
        if sensor in line:
            is_wrap = ''.join(line.split(",")[9])
            wrap_number = int(''.join(line.split(",")[7]))
            packet_wrap = ''.join(line.split(",")[12])
            if is_wrap == "Y" and wrap_number > 1:
                all_wraptime.append(packet_wrap)
    f.close()
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
    
    print "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" %\
     (sensor, min_latency, p50, p60, p70, p80, p85, p90, p95, p100, average_latency)
'''
#for KPI-3 wrap time
print "Write KPI-3 sensor wrap time Data"
kpi_result.write("\nKPI-3 Wrap time, unit ms\n")
kpi_result.write("KPI-3, Type, Sensor, Min, 50%, 60%, 70%, 80%, 85%, 90%, 95%, 100%, average\n")

for sensor in all_sensors:
    #print "Processing sensor: %s" % sensor
    json_point = []
    all_wraptime = []
    sensor_id = sensor.split(":")[0]
    sensor_name = sensor.split(":")[2]
    pfe_id = sensor.split(":")[-1]
    sensor_bak = sensor_id + sensor_name + pfe_id
    sensor_bak = sensor_bak.replace("/","_")

    res_name = result_file + "_" + sensor_bak + ".csv"
    f = open(res_name)
    for line in f:
        if sensor in line:
            is_wrap = ''.join(line.split(",")[9])
            time_wrap = ''.join(line.split(",")[11])
            wrap_number = int(''.join(line.split(",")[7]))
            if is_wrap == "Y" and wrap_number > 1:
                    all_wraptime.append(time_wrap)
    f.close()
    
    if ":PFE_" in sensor:
        kpi3_hdr = "KPI-3, PFE"
    else:
        kpi3_hdr = "KPI-3, RE"
        
        
    if len(all_wraptime) == 0:
        if "_65535" in sensor:
            kpi_result.write(kpi3_hdr + "," + sensor +", N/A, N/A, N/A, N/A, N/A, N/A, N/A, N/A, N/A, N/A\n")
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
    
    kpi_result.write(kpi3_hdr + "," + sensor + "," + str(min_latency) + "," + str(p50) + "," + str(p60) + "," + str(p70)\
                     + "," + str(p80) + "," + str(p85) + "," + str(p90) + "," + str(p95) + "," + str(p100) + "," + str(average_latency))
    kpi_result.write("\n")

# for KPI-7 wrap time
print "Write KPI-7 sensor Init Sync time Data"
kpi_result.write("\nKPI-7 Init Sync time, unit ms\n")
kpi_result.write("KPI-7, Type, Sensor, Init_Sync_Packets, Init_Sync_time\n")

for sensor in all_sensors:
    # print "Processing sensor: %s" % sensor
    json_point = []
    sensor_id = sensor.split(":")[0]
    sensor_name = sensor.split(":")[2]
    pfe_id = sensor.split(":")[-1]
    sensor_bak = sensor_id + sensor_name + pfe_id
    sensor_bak = sensor_bak.replace("/", "_")
    init_name = init_file + "_" + sensor_bak + ".csv"
    init = open(init_name, "r")

    packets = 0

    for line in init:
        if sensor in line:
            if packets == 0:
                first_line = line
            packets += 1
            last_line = line

    if packets == 0 or packets == 1:
        dump_time = 0
    else:
        begin_time = int(''.join(first_line.split(",")[3]))
        end_time = int(''.join(last_line.split(",")[3]))
        dump_time = end_time - begin_time

    init.close()

    if ":PFE_" in sensor:
        kpi7_hdr = "KPI-7, PFE"
    else:
        kpi7_hdr = "KPI-7, RE"

    kpi_result.write(kpi7_hdr + "," + sensor + "," + str(packets) + "," + str(dump_time))
    kpi_result.write("\n")

'''
    my_list = [kpi7_hdr, sensor, packets, dump_time]
    json_point.append(my_list)

json_point.sort(key=lambda x: x[0], reverse=True)
for line in json_point:
    kpi_result.write(','.join([str(x) for x in line]))
    kpi_result.write("\n")
'''
kpi_result.close()
exit()
