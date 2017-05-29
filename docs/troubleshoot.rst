Troubleshooting Guide
======================

To check if containers are running, execute the following command. By default you should have 3 containers running

.. code-block:: text

  docker ps

To force containers to stop, execute

.. code-block:: text

  make stop

To access the CLI of the main container for debug,
Start a SSH session using the insecure_key provided in the repo and the script "docker.cli.sh"

.. code-block:: text

  make cli

For the Input containers named __open-nti-input-*__ you can access the logs directly from docker by running :

.. code-block:: text

  docker logs <container name or ID>

Data Collection Agent
------------------------

Q - I configured hosts/credential/commands.yaml files but I'm not seeing anything on the dashboard
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#1 : Make sure everything is working as expected, you can run the Data Collection Agent in debug mode

.. code-block:: text

  make cron-debug TAG=lab

#2 : Check if data is properly reaching the database**

 - connect on Influxdb management interface with a browser on port 8083
 - Select Juniper as database on top right corner
 - Run query ```show measurements``` to see what is present
 - Execute query for ```SELECT * FROM "<measurements>"```

.. NOTE::
   Destination tables will vary depending of the incoming traffic
    - For MX > jnpr.jvision
    - For QFX5100/EX4300 > jnpr.analyticsd
    
    Example: 
    
      If the pyez command are excuted with any error , you would see table.
      
      Command : show chassis routing-engine | display xml
      
      Influxdb : (show measurements)
        
        Newly added table : 
          
          <HOSTNAME>.chassis.routing-engine.0.mastership-state
        
        New Query to verify data:
          
          select * from <HOSTNAME>.chassis.routing-engine.0.mastership-state
  
        ## DATA ###
        
        20161102.338446_builder_stable_10"
        2016-12-04T01:22:10.568116882Z	"N/A"	"<HOSTNAME>"	"1"	"<HOSTNAME>.chassis.routing-engine.0.mastership-state"	        "mx960"	"master"
      

#3 : Check log within the container**

    make cli
  
  Check the log for any Error : /opt/open-nti/log

#4 : Enable log in debug mode **


  a) 
  
    /open-nti/data/open-nti-variable.yaml
  
    logging_level: 10

    #CRITICAL   50
    #ERROR      40
    #WARNING    30
    #INFO       20
    #DEBUG      10  


  b)
    
    make cli
    
    Check the log for any Error : /opt/open-nti/log

#4 : For Debugging Parser related issue : Manually runing Data collection script withing the container :

     This step is extremly useful for troubleshooting parser realted issue.The log give details of 
        - commnad that are been executed
        - Parser which are been loaded
        - Error Loading any parser (IF ANY)
        - XPATH element (found / not-found)
        - Data element which are sent to influx-db
      
      if you need additional XPATH detail to be loged to console , modify the "open-nti.py" file.
      
      cd /opt/open-nti/
      
      vi open-nti.py
      
      remove the trailing "#" from "#key =" and "#print"
      
      *** open-nti.py (snippet) *** 
      def parse_result(host,target_command,result,datapoints,latest_datapoints,kpi_tags):  

        elif match["type"] == "multi-value":
        nodes = xml_data.xpath(match["xpath"])
        for node in nodes:
                    #Look for all posible keys or fields to extract and be used for variable-naming
                               #key = node.xpath(match["loop"]["key"])[0].text.replace(" ","_").strip()
                               #print "the key is: " + key          
      
      *** End (snippet)***
      
  a) Enter Docker Container Shell (CLI):
      
      docker exec -it opennti_con /bin/bash 

  b) Run the data collection script in debug mode:
  
      cd /opt/open-nti/
      
      python open-nti.py -c -s (will run script reading input from /opt/open-nti/data)
      
      *** Arguments ***
      
      usage: open-nti.py [-h] [--tag TAG [TAG ...]] [-c] [-t] [-s] [-i INPUT]

      optional arguments:
        -h, --help            show this help message and exit
        --tag TAG [TAG ...]   Collect data from hosts that matches the tag
        -c, --console         Console logs enabled
        -t, --test            Use emulated Junos device
        -s, --start           Start collecting (default 'no')
        -i INPUT, --input INPUT  Directory where to find input files
        
       *** Arguments END ***
       
       *** SAMPLE OUTPUT ***
       
       root@7320064461bc:/opt/open-nti# python open-nti.py -c -s
        Importing credentials file: /opt/open-nti/data/credentials.yaml
        Importing host file: /opt/open-nti/data/hosts.yaml
        Importing commands file: /opt/open-nti/data/commands.yaml
        Importing junos parsers file: ['show-subscribers-summary.parser.yaml', 'show-system-statistics-icmp.parser.yaml', 'show-bgp-neighbor.parser.yaml', 'show-krt-state.parser.yaml', 'show-route-summary.parser.yaml', 'show-pfe-statistics-traffic.parser.yaml', 'show-services-nat-pool-detail.parser.yaml', 'show-services-rpm-probe-results.parser.yaml', 'show-version.parser.yaml']
        Error importing junos parser: show-bgp-neighbor.parser.yaml.bak
        Error importing junos parser: show-bgp-summary.parser.yaml.bak
        Importing pfe parsers file: ['.gitignore']
        Getting hosts that matches the specified tags
        The following hosts are being selected:  ['148.48.48.1']
        Collector Thread-1 scheduled with following hosts: ['148.48.48.1']
        Connecting to host: 148.48.48.1
        [148.48.48.1]: Executing command: show version | display xml
        [148.48.48.1]: Parsing command: show version | display xml
        [148.48.48.1]: Host will now be referenced as : DEMO-MX-RE1 
        
        [DEMO-MX-RE1]: Executing command: show chassis routing-engine | display xml
        [DEMO-MX-RE1]: Parsing command: show chassis routing-engine | display xml
        [DEMO-MX-RE1]: Looking for a sub-match: ./mastership-state
        [DEMO-MX-RE1]: Looking for a sub-match: ./memory-buffer-utilization
        [DEMO-MX-RE1]: No match found: //route-engine
        [DEMO-MX-RE1]: Looking for a sub-match: ./up-time
        [DEMO-MX-RE1]: No match found: //route-engine
        [DEMO-MX-RE1]: Looking for a sub-match: ./cpu-idle
        [DEMO-MX-RE1]: No match found: //route-engine
        [DEMO-MX-RE1]: Looking for a sub-match: ./mastership-state
        [DEMO-MX-RE1]: Looking for a sub-match: ./memory-buffer-utilization
        No latest datapoint found for <{'device': 'DEMO-MX-RE1', 'kpi': 'DEMO-MX-RE1.chassis.routing-engine.1.memory-buffer-utilization', 'version': '20161102.338446_builder_stable_10', 'product-model': 'mx960', 'key': '1'}>
        [DEMO-MX-RE1]: Looking for a sub-match: ./up-time
        [DEMO-MX-RE1]: Looking for a sub-match: ./cpu-idle
        No latest datapoint found for <{'device': 'DEMO-MX-RE1', 'kpi': 'DEMO-MX-RE1.chassis.routing-engine.1.cpu-idle', 'version': '20161102.338446_builder_stable_10', 'product-model': 'mx960', 'key': '1'}>
        [DEMO-MX-RE1]: Parser found and processed, going to next comand.
        [DEMO-MX-RE1]: timestamp_tracking - CLI collection 4
        No latest datapoint found for <{'device': 'DEMO-MX-RE1', 'kpi': 'open-nti-stats', 'version': '20161102.338446_builder_stable_10', 'product-model': 'mx960', 'stats': 'collection-time'}>
        No latest datapoint found for <{'device': 'DEMO-MX-RE1', 'kpi': 'open-nti-stats', 'version': '20161102.338446_builder_stable_10', 'product-model': 'mx960', 'stats': 'collection-successful'}>
        Inserting into database the following datapoints:
        
       *** SAMPLE OUTPUT END ***


Data Streaming Collector
------------------------

Q - I'm streaming data from devices but I'm not seeing anything on the Dashboard
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To reach the dashboard, traffic have to go through the following path:
**Device** >(A)> **Host** >(B)> **Container** >(C)> **Fluentd** >(B)> **InfluxDB** >(E)> **Grafana**

**A - Check the timestamp on the devices and on the server**

Timestamp MUST match on both side, the server and the junos devices.
It's the most common issue.

**B - Check that traffic is reaching the Host**

The best solution is to use TCPDUMP on the Host and filter on destination port

.. code-block:: text

  On Unix/Mac
  tcpdump -i <ingress interface> -n dst port <dest port number>

**C - Check that traffic is reaching the container**

The best solution is to use TCPDUMP inside the container

.. code-block:: text

  ./docker.cli.sh
  tcpdump -i eth0 -n dst port <dest port number>

  RPF check might be a problem if you see incoming packets in A but not in B.
  If you e.g. use Src IP for which there is no route entry on host OS (Ubuntu
  does RPF check as default), packets would be discarded.

**D - Check Fluentd****

Check fluentd logs, inside the container

.. code-block:: text

  docker logs opennti_input_jti

Nothing should be printed if everything is right

**E - Check if data is properly reaching the database**

 - connect on Influxdb management interface with a browser on port 8083
 - Select Juniper as database on top right corner
 - Run query ```show measurements``` to see what is present
 - Execute query for ```SELECT * FROM "<measurements>"```

.. NOTE::
   Destination tables will vary depending of the incoming traffic
    - For MX > jnpr.jvision
    - For QFX5100/EX4300 > jnpr.analyticsd
