



PWD = $(shell pwd)
VAR_FILE = open-nti.params
TAG = latest
DOCKER_FILE = docker-compose.yml
DOCKER_FILE_P = docker-compose/opennti_persistent.yml

#Load params file with all variables
include $(VAR_FILE)

build:
	docker build -t $(IMAGE_NAME):$(TAG) .

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
