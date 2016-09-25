Data Collection Agent
=====================

Configuration
-------------

**data/hosts.yaml**
In data/hosts.yaml you need to provide the list of devices you want to pull information from
For each device, you need to indicate the name ane one or multiple *tags* (at least one).
Tags will be used later to know which credentials should be used for this device and which commands need to be executed

.. code-block:: yaml

  <hostA>: <tag1> <tag4>
  <hostB>: <tag1> <tag4>
  <hostC>: <tag2> <tag4> <tag5>
  <hostD>: <tag1> <tag4>  <--- Those tags relate the Hosts with the credentials and the commands to use with

Example

.. code-block:: yaml

  mx-edge011: edge mx madrid bgp mpls
  mx-agg011: agg mx madrid bgp isis
  qfx-agg022: agg qfx munich bgp
  qfx5100-02: tor qfx madrid isis


.. NOTE::
  The default configuration assume that hosts defined in hosts.yaml can be resolved with DNS
  if your hosts doesn't have DNS entry, it's possible to indicate the IP address in the hosts.yaml file instead of the name

  `192.168.0.1: edge mx madrid bgp mpls`

  To avoid using Ip addresses in the dashboard, you can use the device hostname defined in the configuration
  instead of the value define in hosts.yaml by setting the parameter **use_hostname** to true in **open-nti.variables.yaml**
  `use_hostname: True`


**data/credentials.yaml**

You need to provide at least one credential profile for your devices

.. code-block:: yaml

  jdi_lab:
    username: '*login*'         (Single quote is to force to be imported as string)
    password: '*password*'      (Single quote is to force to be imported as string)
    method: password            (other supported methods 'key' and 'enc_key' for ssh Key-Based Authentication)
    key_file: ./data/*key_file* (optional: only appies if method key or enc_key is used, it must be located at data directory)
    tags: tag1 tag2

**data/commands.yaml**

.. code-block:: yaml

  generic_commands:  <--- You can name the group as best fits you
     commands: |
        show version | display xml  <--- There is no limit on how many commands can be added into a group
        show isis statistics | display xml <-- Before adding a command, confirm that there is a related parser
        show system buffers
        show system statistics icmp | display xml
        show route summary | display xml
     tags: tag1 tag2

Execution periodic
-------------------
To collect data periodically with the **Data Collection Agent**, you need to setup a cron job inside the container.
As part of the project, open-nti is providing some scripts to easily add/remove cron jobs **inside** the container **from** the host.

Scripts provided:
 - **open-nti-start-cron.sh**: Create a new cron job inside the container
 - **open-nti-show-cron.sh**: Show all cron jobs configured inside the container
 - **open-nti-stop-cron.sh**: Delete a cron job inside the container for a specific tag

To start cron job to execute commands specified above for specific tag every minute:

.. code-block:: text

  ./open-nti-start-cron.sh 1m '--tag tag1'

To start cron job for more than one tag at the same time:

.. code-block:: text

  ./open-nti-start-cron.sh 1m '--tag tag1 tag2'

To start cron job to execute commands specified above for specific tag every 5 minutes:

.. code-block:: text

    ./open-nti-start-cron.sh 5m '--tag tag1'


To start cron job to execute commands specified above for specific tag every hour:

.. code-block:: text

    ./open-nti-start-cron.sh 1h '--tag tag1'

To show all scheduled cron jobs:

.. code-block:: text

  ./open-nti-show-cron.sh 'all'

To stop cron job for specific tag:

.. code-block:: text

  ./open-nti-stop-cron.sh '--tag tag1'

.. NOTE::
  If you want to configure the cron job yourself, open-nti use this command:
  ``/usr/bin/python /opt/open-nti/open-nti.py -s --tag <tag>``
