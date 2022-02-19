# Determine the current git Branch and use that for docker
BRANCH ?= $(shell git rev-parse --abbrev-ref HEAD)
ifeq ($(BRANCH),master)
  IMAGE_TAG = latest
else
  IMAGE_TAG = $(BRANCH)
endif

TEST_TAG=unittest

PWD = $(shell pwd)
VAR_FILE ?= open-nti.params
DOCKER_FILE = docker-compose.yml
DOCKER_FILE_P = docker-compose-persistent.yml
DOCKER_FILE_MAIN = docker-compose-persistent-main.yml
TIME ?= 1m
TAG ?= all
NBR ?= 1

#Load params file with all variables
include $(VAR_FILE)

# Define run options for Docker-compose
RUN_OPTIONS = IMAGE_TAG=$(IMAGE_TAG)

#build: build-main build-jti build-syslog build-snmp build-oc build-internal
build: build-main build-jti build-syslog build-oc build-internal

build-main:
	@echo "======================================================================"
	@echo "Build Docker image - $(MAIN_IMAGE_NAME):$(IMAGE_TAG)"
	@echo "======================================================================"
	docker build -t $(MAIN_IMAGE_NAME):$(IMAGE_TAG) .

build-jti:
	@echo "======================================================================"
	@echo "Build Docker image - $(INPUT_JTI_IMAGE_NAME):$(IMAGE_TAG)"
	@echo "======================================================================"
	docker build -f $(INPUT_JTI_DIR)/Dockerfile -t $(INPUT_JTI_IMAGE_NAME):$(IMAGE_TAG) $(INPUT_JTI_DIR)

build-syslog:
	@echo "======================================================================"
	@echo "Build Docker image - $(INPUT_SYSLOG_IMAGE_NAME):$(IMAGE_TAG)"
	@echo "======================================================================"
	docker build -f $(INPUT_SYSLOG_DIR)/Dockerfile -t $(INPUT_SYSLOG_IMAGE_NAME):$(IMAGE_TAG) $(INPUT_SYSLOG_DIR)

build-snmp:
	@echo "======================================================================"
	@echo "Build Docker image - $(INPUT_SNMP_IMAGE_NAME):$(IMAGE_TAG)"
	@echo "======================================================================"
	docker build -f $(INPUT_SNMP_DIR)/Dockerfile -t $(INPUT_SNMP_IMAGE_NAME):$(IMAGE_TAG) $(INPUT_SNMP_DIR)

build-oc:
	@echo "======================================================================"
	@echo "Build Docker image - $(INPUT_OC_IMAGE_NAME):$(IMAGE_TAG)"
	@echo "======================================================================"
	docker build -f $(INPUT_OC_DIR)/Dockerfile -t $(INPUT_OC_IMAGE_NAME):$(IMAGE_TAG) $(INPUT_OC_DIR)

build-internal:
	@echo "======================================================================"
	@echo "Build Docker image - $(INPUT_INTERNAL_IMAGE_NAME):$(IMAGE_TAG)"
	@echo "======================================================================"
	docker build -f $(INPUT_INTERNAL_DIR)/Dockerfile -t $(INPUT_INTERNAL_IMAGE_NAME):$(IMAGE_TAG) $(INPUT_INTERNAL_DIR)

test: test-build test-run

test-build:
	docker build -t $(MAIN_IMAGE_NAME):$(TEST_TAG) .
	docker build -f $(INPUT_JTI_DIR)/Dockerfile -t $(INPUT_JTI_IMAGE_NAME):$(TEST_TAG) $(INPUT_JTI_DIR)
	docker build -f $(INPUT_SYSLOG_DIR)/Dockerfile -t $(INPUT_SYSLOG_IMAGE_NAME):$(TEST_TAG) $(INPUT_SYSLOG_DIR)
	docker build -f $(INPUT_SNMP_DIR)/Dockerfile -t $(INPUT_SNMP_IMAGE_NAME):$(TEST_TAG) $(INPUT_SNMP_DIR)
	docker build -f $(INPUT_INTERNAL_DIR)/Dockerfile -t $(INPUT_INTERNAL_IMAGE_NAME):$(TEST_TAG) $(INPUT_INTERNAL_DIR)

cli:
	docker exec -i -t $(MAIN_CONTAINER_NAME) /bin/bash

start:
	@echo "Use docker compose file: $(DOCKER_FILE)"
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_FILE) up -d

start-persistent:
	@echo "Use docker compose file: $(DOCKER_FILE_P)"
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_FILE_P) up -d

start-main:
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_FILE_MAIN) up -d

stop:
	@echo "Use docker compose file: $(DOCKER_FILE)"
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_FILE) down

stop-persistent:
	@echo "Use docker compose file: $(DOCKER_FILE_P)"
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_FILE_P) down

update:
	@echo "OpenNTI - Update the files from Github"
	git pull
	@echo "OpenNTI - Update the containers from Docker Hub"
	docker pull $(MAIN_IMAGE_NAME):latest
	docker pull $(INPUT_JTI_IMAGE_NAME):latest
	docker pull $(INPUT_SYSLOG_IMAGE_NAME):latest


#restart: restart-main restart-jti restart-syslog restart-snmp restart-internal
restart: restart-main restart-jti restart-syslog restart-internal

restart-main:
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_FILE) restart opennti

restart-jti:
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_FILE) restart input-jti

restart-syslog:
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_FILE) restart input-syslog

restart-snmp:
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_FILE) restart input-snmp

restart-oc:
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_FILE) restart input-oc

restart-internal:
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_FILE) restart input-internal

scale-input-syslog:
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_FILE) scale input-syslog=$(NBR)

scale-input-jti:
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_FILE) scale input-jti=$(NBR)

scale-input-snmp:
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_FILE) scale input-snmp=$(NBR)

cron-show:
	docker exec -it $(MAIN_CONTAINER_NAME) /usr/bin/python3 /opt/open-nti/startcron.py -a show  -c "/usr/bin/python3 /opt/open-nti/open-nti.py -s"

cron-add:
ifeq ($(TAG), all)
	docker exec -it $(MAIN_CONTAINER_NAME) /usr/bin/python3 /opt/open-nti/startcron.py -a add -t "$(TIME)" -c "/usr/bin/python3 /opt/open-nti/open-nti.py -s"
else
	docker exec -it $(MAIN_CONTAINER_NAME) /usr/bin/python3 /opt/open-nti/startcron.py -a add -t "$(TIME)" -c "/usr/bin/python3 /opt/open-nti/open-nti.py -s --tag $(TAG)"
endif

cron-delete:
ifeq ($(TAG), all)
	docker exec -it $(MAIN_CONTAINER_NAME) /usr/bin/python3 /opt/open-nti/startcron.py -a delete -c "/usr/bin/python3 /opt/open-nti/open-nti.py -s"
else
	docker exec -it $(MAIN_CONTAINER_NAME) /usr/bin/python3 /opt/open-nti/startcron.py -a delete -c "/usr/bin/python3 /opt/open-nti/open-nti.py -s --tag $(TAG)"
endif

cron-debug:
ifeq ($(TAG), all)
	docker exec -i -t $(MAIN_CONTAINER_NAME) /usr/bin/python3 /opt/open-nti/open-nti.py -s -c
else
	docker exec -i -t $(MAIN_CONTAINER_NAME) /usr/bin/python3 /opt/open-nti/open-nti.py -s -c --tag $(TAG)
endif
