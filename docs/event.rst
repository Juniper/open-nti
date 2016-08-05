Events
======
By default dashboards are configured to display some "events" that are stored in the database into the serie "events"
Their are multiple ways to record entry in the events serie

Insert events via syslog
------------------------
open-nti will access events in the syslog format on port **UDP/6000**.  
The goal is not to send all syslog but only relevant information like Commit or Protocol Flaps

To send only one syslog at commit time you can use the configuration below

.. code-block:: text

  set system syslog host 192.168.99.100 any any
  set system syslog host 192.168.99.100 match UI_COMMIT_COMPLETED
  set system syslog host 192.168.99.100 port 6000


Insert events in the database directly
--------------------------------------

It's possible to insert events with just a HTTP POST request to the database, here is an example using curl

.. code-block:: text

  curl -i -XPOST 'http://10.92.71.225:8086/write?db=juniper' --data-binary 'events,type=Error text="BGP Flap"'
  curl -i -XPOST 'http://10.92.71.225:8086/write?db=juniper' --data-binary 'events,device=qfx5100-01,type=Commit text="Change applied"'

.. NOTE::
  any system that knows how to generate a HTTP POST request can inject an event.
  its very utile if you have a script/tool that run some tests to keep track of when major events happen
