#! /bin/bash

source ./open-nti.params
echo "$(tput setaf 5)this script (docker.update.sh) is deprecated, it's been replaced with 'make update' $(tput sgr0)"

echo "OpenNTI - Update the files from Github"
git pull

echo "OpenNTI - Update the containers from Docker Hub"
docker pull $MAIN_IMAGE_NAME:latest
docker pull $INPUT_JTI_IMAGE_NAME:latest
docker pull $INPUT_SYSLOG_IMAGE_NAME:latest
