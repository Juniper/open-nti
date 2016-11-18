Customize OpenNTI
-----------------
Customize container's name and ports
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
All port numbers and names used by start/stop scripts are centralized in
one file : **open-nti.params**,
you can easily adapt this file with your own port numbers or names.

.. NOTE::
  It's mandatory if you are planning to run multiple instances of OpenNTI on the same server.

Customize the container itself
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you want to make some modifications, you can always build the container yourself using the script ``make build``.

.. NOTE::
  The first time you run ``make build``, it will take 10-15min to download and compile everything but after that it will be very fast
