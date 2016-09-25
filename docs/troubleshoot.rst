Troubleshooting Guide
======================

To check if containers are running, execute the following command. By default you should have 3 containers running
.. code-block:: text

  docker ps

To force containers to stop, execute
.. code-block:: text

  ./docker.stop.sh

To access the CLI of the main container for debug,
Start a SSH session using the insecure_key provided in the repo and the script "docker.cli.sh"
.. code-block:: text

  chmod 600 insecure_key
  ./docker.cli.sh

For the Input containers named __open-nti-input-*__ you can access the logs directly from docker by running :
.. code-block:: text

  docker logs <container name or ID>


FAQ
---
I'm streaming data from devices but I'm not seeing anything on the Dashboard

To reach the dashboard, traffic have to go through the following path:
**Device** >(A)> **Host** >(B)> **Container** >(C)> **Fluentd** >(B)> **InfluxDB** >(E)> **Grafana**

### A - Check that traffic is reaching the Host

The best solution is to use TCPDUMP on the Host and filter on destination port
.. code-block:: text

  On Unix/Mac
  tcpdump -i <ingress interface> -n dst port <dest port number>

### B - Check that traffic is reaching the container
The best solution is to use TCPDUMP inside the container
.. code-block:: text

  ./docker.cli.sh
  tcpdump -i eth0 -n dst port <dest port number>

  RPF check might be a problem if you see incoming packets in A but not in B.
  If you e.g. use Src IP for which there is no route entry on host OS (Ubuntu
  does RPF check as default), packets would be discarded.


### C - Check Fluentd
Check fluentd logs, inside the container
.. code-block:: text

  ./docker.cli.sh
  tail -f /var/log/fluentd.log

Nothing should be printed if everything is right

### D - Check if data is properly reaching the database
- connect on Influxdb management interface with a browser on port 8083
- Select Juniper as database on top right corner
- Run query ```show measurements``` to see what is present
- Execute query for ```SELECT * FROM "<measurements>"```

> Destination tables will vary depending of the incoming traffic
> - For MX > jnpr.jvision
> - For QFX5100/EX4300 > jnpr.analyticsd
