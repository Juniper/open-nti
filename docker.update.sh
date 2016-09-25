#! /bin/bash

source ./open-nti.params

echo "OpenNTI - Update the files from Github"
git pull

echo "OpenNTI - Update the containers from Docker Hub"
docker pull $IMAGE_NAME
docker pull juniper/open-nti-input-jti:latest
docker pull juniper/open-nti-input-syslog:latest
