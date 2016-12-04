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

#3 : Check log within the container**

  ./docker.cli.sh
  
  Check the log for any Error : /opt/open-nti/log

#4 : Enable log in debug mode **

  /open-nti/data/open-nti-variable.yaml
  
  logging_level: 10

    #CRITICAL   50
    #ERROR      40
    #WARNING    30
    #INFO       20
    #DEBUG      10  


  ./docker.cli.sh
  
  Check the log for any Error : /opt/open-nti/log


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
