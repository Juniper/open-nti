SNMP Collector Agent
========================

This collector is based on:

Telegraf (https://docs.influxdata.com/telegraf/v1.2/)

IMPORTANT:  **All devices must have the SNMP configuration properly defined (communities, views, filters, etc)**,

By default this collector is enabled, but if you don't need it, you can disable it using any of the following options:

**Permanent option**: Edit the docker-compose file and delete/comment the input-snmp definition

**Temporary option**: Execute 'make scale-input-snmp NBR=0'

Telegraf configuration file
----------------

The basic steps to make the plugin runs are.

1.- Open the telegraf configuration file located at 'open-nti/plugins/input-snmp/templates/telegraf.tmpl'

2.- Inside the '[inputs.snmp]' instance, edit the list of agent to poll

.. code-block:: toml

  [[inputs.snmp]]
    agents = [ "172.30.137.90:161","172.30.137.93:161" ]  # this is an example for a single snmp get 
    version = 2
    community = "public"   # The community to be used

3.- Edit the OIDs to collect

.. code-block:: toml

  [[inputs.snmp.field]]   # this is an example for a single snmp get 
    name = "uptime"
    oid = ".1.3.6.1.2.1.1.3.0"    



  [[inputs.snmp.table]]       # this is an example for a snmp walk
    name = "interface_statistics"
    inherit_tags = [ "hostname" ]   # See note below.
    [inputs.snmp.tagpass]
      ifName = ["[g|x]e-","ae"]    #  This is relevant for filtering unwanted records
    [[inputs.snmp.table.field]]    #  This is the 'key' of the table, the element that helps to differentiate each record on the table.
      name = "ifName"
      oid = ".1.3.6.1.2.1.31.1.1.1.1"
      is_tag = true
    [[inputs.snmp.table.field]]   # Get a element of the table
      name = "ifHCInOctets"
      oid = ".1.3.6.1.2.1.31.1.1.1.6"


NOTE:

.. code-block:: toml

  [[inputs.snmp.field]]   # Try to allways keep this block in order to include hostanme info in all your records inserted on the database
    name = "hostname"
    oid = ".1.3.6.1.2.1.1.5.0"
    is_tag = true



4.- Save the file, then rebuild the container, executing 'make build-snmp'

5.- Restart the snmp-input container, executing 'make restart-snmp'


NOTE:  You can define multiple [inputs.snmp] instances, and on each instance define different agent hosts and different OIDs depending on your requirements.

For more information about telegraf snmp plugin please check https://github.com/influxdata/telegraf/tree/master/plugins/inputs/snmp
