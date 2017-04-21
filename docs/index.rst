
OpenNTI Documentation
=====================

.. _here: http://forums.juniper.net/t5/Analytics/Open-Source-Universal-Telemetry-Collector-for-Junos/ba-p/288677

OpenNTI is a container packaged with all tools needed to collect and visualize time series data from network devices.
Data can be collected from different sources:
 - **Data Collection Agent** : Collect data on devices using CLI/Shell or Netconf
 - **Data Streaming Collector** : Take all data streamed by Juniper devices as Input (JTI, Analyticsd, soon Openconfig with gRPC)
 - **Statsd interface** : Accept any Statsd packets
 - **SNMP Collection Agent** : Collect data on devices using SNMP
 
It's pre-configured with all tools and with a default dashboard ..
**Send it data, it will graph it**

Thanks to docker, it can run pretty much anywhere on server, on laptop ... on the device itself

More detailed description of a project can be found here_ (including a series of videos on how to use it):

How to report feedback / participate in the project
---------------------------------------------------

.. _Github: https://github.com/Juniper/open-nti/issues
.. _Google-Group: https://groups.google.com/forum/#!forum/open-nti

For any issues please open an issue on Github_.
For comments, suggestions or questions please use our Google-Group_

To participate, please:
 - Fork the project
 - Send us a pull request

.. NOTE::
  if you are planning significant changes, please start a discussion first.

**Contributions are more than Welcome**

User Documentation
==================

* :ref:`installation-docs`
* :ref:`dashboards-docs`
* :ref:`troubleshooting-docs`

Additional Documentation
========================

* :ref:`architecture-docs`
* :ref:`input-plugins-docs`


.. _installation-docs:

.. toctree::
   :maxdepth: 2
   :caption: Installation

   install
   customize

.. _architecture-docs:

.. toctree::
   :maxdepth: 2
   :caption: Architecture

   architecture

.. _input-plugins-docs:

.. toctree::
   :maxdepth: 2
   :caption: Input Plugins

   datacollectionagent
   datastreaming
   event
   snmpcollectionagent

.. _dashboards-docs:

.. toctree::
   :maxdepth: 2
   :caption: Dashboards

   dashboard
   dashboardlib

.. _troubleshooting-docs:

.. toctree::
   :maxdepth: 2
   :caption: Troubleshooting

   troubleshoot
