# This script uses the raw data from JUNOS and EVO then try to compare the data type for all sensor leaves. 
# Usage: python data.py junos_file evo_file

import re,sys,time

def parse_input_file(inputfile):
    f = open(inputfile)
    print("Processing file: %s" % inputfile)

    prefix = ""
    result = {}
    count = 0
    start_time = time.time()

    while True:

        line = f.readline()
        count += 1
        if not line:
            break

        if "timestamp__" in line:
            prefix = ""
            data_type = f.readline().split(": ")[0]
            count += 1
        elif "key: __prefix__" in line:
            prefix_raw = f.readline().split(": ")[1].strip()
            prefix = re.sub("\[.*?\]", "", prefix_raw).replace("']/","")

            ##debug only##
            if "[" in prefix or "]" in prefix:
                print("error in prefix line %s: %s" % (count, prefix_raw))
                exit()

            count += 1
            continue
        elif "key: " in line:
            key_raw = line.split(": ")[1].strip()
            key = re.sub("\[.*?\]", "", key_raw).replace("']/","")

            ##debug only##
            if "[" in key or "]" in key:
                print("error in key line %s: %s", (count, key_raw))
                exit()

            path = prefix + key
            data_type = f.readline().split(":")[0].strip()
            count += 1
            if path not in result.keys():
                result[path] = data_type

    spent = time.time() - start_time
    print("Total time spent %s seconds to parse %s lines of data in file %s. Total %s unique sensor leaves reported" % (spent, count, inputfile, len(result)))
    return result
    
    #for k,v in result.items():
    #   print(k,v)

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python data.py junos_file evo_file")
        exit()

    junos_file = sys.argv[1]
    evo_file = sys.argv[2]
    junos_result = {}
    evo_result = {}

    junos_result = parse_input_file(junos_file)
    evo_result = parse_input_file(evo_file)

    f = open("junos.csv", "w")
    for k,v in junos_result.items():
        f.write(k + "," + v + "\n")
    f.close()
    f = open("evo.csv", "w")
    for k,v in evo_result.items():
        f.write(k + "," + v + "\n")
    f.close()

    for path in junos_result.keys():
        if path in evo_result:
            if junos_result[path] != evo_result[path]:
                print("Error Reported for path %s. JUNOS type: %s, EVO type: %s" % (path, junos_result[path], evo_result[path]))
        else:
            print("Error Reported for path %s. Path exists in JUNOS but not in EVO" % path)
    
    for path in evo_result.keys():
        if path not in junos_result:
            print("Error Reported for path %s. Path exists in EVO but not in JUNOS" % path)
