
OpenNTI Documentation
=====================

OpenNTI is a container packaged with all tools needed to collect and visualize time series data from network devices.
Data can be collected from different sources:

- **Data Collection Agent** : Collect data on devices using CLI/Shell or Netconf
- **Data Streaming Collector** : Take all data streamed by Juniper devices as Input (JTI, Analyticsd, soon Openconfig with gRPC)
- **Statsd interface** : Accept any Statsd packets

It's pre-configured with all tools and with a default dashboard ..
**Send it data, it will graph it**

Thanks to docker, it can run pretty much anywhere on server, on laptop ... on the device itself

More detailed description of a project can be found [here](http://forums.juniper.net/t5/Analytics/Open-Source-Universal-Telemetry-Collector-for-Junos/ba-p/288677) (including a series of videos on how to use it):

Customize OpenNTI
-----------------
Customize container's name and ports
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
All port numbers and names used by start/stop scripts are centralized in one file : [open-nti.params](open-nti.params), you can easily adapt this file with your own port numbers or names. It's mandatory if you are planning to run multiple instances of OpenNTI on the same server.

Customize the container itself
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to make some modifications, you can always build the container yourself using the script ```./docker.build.sh```.
>The first time you run "./docker.build.sh", it will take 10-15min to download and compile everything but after that it will be very fast

How to report feedback / participate in the project
---------------------------------------------------

For any issues please open an [issue on Github](https://github.com/Juniper/open-nti/issues).
For comments, suggestions or questions please use our [google group](https://groups.google.com/forum/#!forum/open-nti)

To participate, please:
- Fork the project
- Send us a pull request

> if you are planning significant changes, please start a discussion first.

**Contributions are more than Welcome**

.. toctree::
   :maxdepth: 2

   install
   architecture
   datacollectionagent
   datastreaming
   event
   dashboard
   troubleshoot

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
