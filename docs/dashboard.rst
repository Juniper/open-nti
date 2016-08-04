
I created a Dashboard generator based on Python and Jinja2.
It's been an open item for long time and it was too often in my way so I decided to take a stab at it.
It's still very early stage and I'm sharing it to get feedback as early as possible.

Top of my head, I can think of multiple tasks for which it will help:

Convert JTI graphs to the new variables names
Create graphs for the new JTI sensors (LSP, FW etc ..)
Add templating for interface
Create Dashboard for Netconf in mode 2 & 3
Create Dashboard on demand and more personalized
In a nutshell, I templatized a grafana dashboard into multiple pieces:

The skeleton of the dashboard
- The rows, composed of multiple panels or graphs
- The graphs
- The annotations
- The templatings

To generate a dashboard you need to create a yaml file that indicate: the title, which rows, which annotations etc ..

---
  title: Data Steaming Collector ALPHA
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

To generate the dashboard based on this config file, you just have to call this command line

cd dashboards/
python gendashboard.py --file data_streaming_collector.yaml
The rows are defined in the directory templates/rows/ and the graphs in the directory ll templates/graphs/

The idea is to define which template for each configuration file, so we don't need to turn everything into a variable in the templates. If 2 graphs are very different we can just have different templates. I believe it will keep the YAML file light and easily readable
