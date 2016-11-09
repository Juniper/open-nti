Data Streaming Collector
========================

Currently the collector accept:
 - Analyticsd (QFX5k) streams in JSON/UDP on port **UDP/50020**
 - Juniper Telemetry Interface (MX/PTX) streams in GPB/UDP on port **UDP/50000**

.. IMPORTANT::
  **it's important that all devices have the correct time defined**,
  it's recommended to configure NTP everywhere

statsd interface
----------------

open-nti is using telegraf to support statsd
Statsd is a popular tool to send metrics over the network, it has been designed by etsy.

More information below:

 - https://github.com/etsy/statsd/blob/master/docs/metric_types.md
 - https://github.com/influxdata/telegraf/tree/master/plugins/inputs/statsd

Here is an example of how to insert statsd data into the Database

.. code-block:: text

  root@d3e82264a08b:/# echo "opennti,device=qfx5100,type=int.rx:100|g" | nc -w 1 -u 127.0.0.1 8125

opennti define the serie
device=qfx5100,type=int.rx will be converted as tag1
100 is the value
g indicate gauge
