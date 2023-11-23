How to install or upgrade
=========================

Requirements
------------

.. _docker: http://docs.docker.com/engine/installation/ubuntulinux/
.. _docker-compose: https://docs.docker.com/compose/install/
.. _Mac: https://docs.docker.com/engine/installation/mac/
.. _Windows: https://docs.docker.com/engine/installation/windows/
.. _DockerCloud: https://hub.docker.com/r/juniper/open-nti/

The requirements is to have docker and docker-compose installed on your Linux server/machine.
Instructions to install are available below
 - docker_
 - docker-compose_

It's also available for:
 - Mac_
 - Windows_

How to Install/Start
--------------------

OpenNTI is available on DockerCloud_ and this project provide scripts to easily download/start/stop it.

.. code-block:: text

  git clone https://github.com/Juniper/open-nti.git
  cd open-nti
  make start

.. NOTE::
  - On Ubuntu, you'll have to add "sudo" before the last command

  - In case of have internet access through a proxy, before executing 'make start', edit all Dockerfiles (those in the main directory and in the plugins directory), and include the lines ENV http_proxy <http_proxy> and ENV https_proxy <https_proxy>. Be sure to clear these environment settings at the Dockerfile but before the final CMD using: ENV http_proxy "" and ENV https_proxy "". The ENV settings are used for both build and execution: without clearing these, it will prevent connectivity between containers (172.17.0.0/16).

By default it will start 3 containers and it's working in **non-persistent mode**, once you stop it all data are gone.
It's possible to start the main container in **persistent mode** to save the database outside the container, b
y using the startup script ``make start-persistent``.
`Persistent mode on Mac OS requires at least v1.12`

How to update
-------------

It's recommended to upgrade the project periodically, both the files from github.com and the containers from Docker Hub.
You can update easily with

.. code-block:: text

  make update
