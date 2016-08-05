How to install or upgrade
=========================

Requirements
------------

The requirements is to have docker and docker-compose installed on your Linux server/machine.
Instructions to install are available below
- docker: http://docs.docker.com/engine/installation/ubuntulinux/
- docker-compose: https://docs.docker.com/compose/install/

It's also available for:
- Mac: https://docs.docker.com/engine/installation/mac/
- Windows: https://docs.docker.com/engine/installation/windows/

How to Install/Start
--------------------

OpenNTI is available on .. _[Docker Cloud]: https://hub.docker.com/r/juniper/open-nti/ and this project provide scripts to easily download/start/stop it.

.. code-block:: text

  git clone https://github.com/Juniper/open-nti.git
  cd open-nti
  ./docker.start.sh

.. NOTE::
  On Ubuntu, you'll have to add "sudo" before the last command

By default it will start 3 containers and it's working in **non-persistent mode**, once you stop it all data are gone.
It's possible to start the main container in **persistent mode** to save the database outside the container, b
y using the startup script ``docker.start.persistent.sh``.
`Persistent mode on Mac OS requires at least v1.12`

How to update
-------------

It's recommended to upgrade the project periodically, both the files from github.com and the containers from Docker Hub.
You can update easily with

.. code-block:: text

  ./docker.update.sh
