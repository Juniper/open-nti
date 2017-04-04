
Dashboard Generator
=========================

OpenNTI integrate a Dashboard generator based on Python and Jinja2.

This dashboard generator can be very useful in many situations:
 - Convert JTI graphs to the new variables names
 - Create graphs for the new JTI sensors (LSP, FW etc ..)
 - Add templating for interface
 - Create Dashboard for Netconf in mode 2 & 3
 - Create Dashboard on demand and more personalized

In a nutshell, it templatized a grafana dashboard into multiple pieces:

The skeleton of the dashboard:
 - **Rows**, composed of multiple panels or graphs
 - **Graphs**,
 - **Annotations**, events overlay on the graphs
 - **Templatings**, drop down menu to narrow the scope

To generate a dashboard you need to create a yaml file that indicate: the title, which rows, which annotations etc ..

.. code-block:: yaml

  title: Data Streaming Collector ALPHA
  template: "dashboard_base.j2"

  tags:
    - opennti

  rows:
    - int-traffic.yaml
    - int-queue.yaml
    - int-buffer.yaml

  templatings:
    - host_regex.yaml
    - interface.yaml

  annotations:
    - commit.yaml
    - bgp_state.yaml

To generate the dashboard based on this config file, you just have to call this command line

.. code-block:: text

  cd dashboards/
  python gendashboard.py --file data_streaming_collector.yaml

The rows are defined in the directory ``templates/rows/`` and the graphs in the directory ``templates/graphs/``
The idea is to define which template for each configuration file, so we don't need to turn everything into a variable in the templates.
If 2 graphs are very different we can just have different templates.

It will keep the YAML file light and easily readable.

.. NOTE::
  You can browse all `rows`, `graphs`, `templatings` and `annotations` available in the :ref:`dashboard_lib`
