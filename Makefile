



PWD = $(shell pwd)
VAR_FILE = open-nti.params
IMAGE_TAG = latest
DOCKER_FILE = docker-compose.yml
DOCKER_FILE_P = docker-compose/opennti_persistent.yml
TIME = 1m
TAG = all

#Load params file with all variables
include $(VAR_FILE)

build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

test:
	docker build -t $(IMAGE_NAME):unittest .
	python -m pytest -v

cli:
	docker exec -it $(CONTAINER_NAME) /bin/bash

start:
	echo "Use docker compose file : $(DOCKER_FILE)"
	docker-compose -f $(DOCKER_FILE) up -d

start-persistent:
	echo "Use docker compose file : $(DOCKER_FILE_P)"
	docker-compose -f $(DOCKER_FILE_P) up -d

stop:
	echo "Use docker compose file : $(DOCKER_FILE)"
	docker-compose -f $(DOCKER_FILE) down

stop-persistent:
	echo "Use docker compose file : $(DOCKER_FILE_P)"
	docker-compose -f $(DOCKER_FILE_P) down

update:
	echo "OpenNTI - Update the files from Github"
	git pull
	echo "OpenNTI - Update the containers from Docker Hub"
	docker pull $(IMAGE_NAME):latest
	docker pull juniper/open-nti-input-jti:latest
	docker pull juniper/open-nti-input-syslog:latest


cron-show:
	# if [ $(TAG) == "all" ]; then
	#   docker exec -it $(CONTAINER_NAME) /usr/bin/python /opt/open-nti/startcron.py -a show  -c "$(TAG)"
	# else
	docker exec -it $(CONTAINER_NAME) /usr/bin/python /opt/open-nti/startcron.py -a show  -c "/usr/bin/python /opt/open-nti/open-nti.py -s $(TAG)"

cron-add:
	docker exec -it $(CONTAINER_NAME) /usr/bin/python /opt/open-nti/startcron.py -a add -t "$(TIME)" -c "/usr/bin/python /opt/open-nti/open-nti.py -s --tag $(TAG)"

cron-delete:
	docker exec -it $(CONTAINER_NAME) /usr/bin/python /opt/open-nti/startcron.py -a delete  -c "/usr/bin/python /opt/open-nti/open-nti.py -s --tag $(TAG)"

cron-debug:
	docker exec -it $(CONTAINER_NAME) /usr/bin/python /opt/open-nti/open-nti.py -s -c --tag $(TAG)
