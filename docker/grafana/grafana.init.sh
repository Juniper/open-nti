#!/bin/bash

function waitAndConfigureGrafana
{
    echo Waiting for Grafana to come up...
    ((attempt=0))
    ((attemptLimit=10))

    sleep 10
    #try 25 times, or roughly 5 second timeout
    until curl -X GET 'http://admin:admin@localhost:80/api/datasources'
    do
        sleep 0.2
        ((attempt++))
        echo "made attempt $attempt of $attemptLimit"
        if (( attempt >= attemptLimit )); then
            echo "Grafana failed to start within the allotted time limit"
            exit 1;
        fi
    done

    echo Grafana is up.  Configuring...

    curl 'http://admin:admin@localhost:80/api/datasources' \
        -X POST -H 'Content-Type: application/json;charset=UTF-8' \
        --data-binary '{"name":"influxdb","type":"influxdb","access":"proxy","url":"http://localhost:8086","password":"juniper","user":"juniper","database":"juniper","basicAuth":false,"isDefault":true}'

    echo Done configuring Grafana
    exit 0
}

waitAndConfigureGrafana >>/var/log/grafana-init.log 2>&1 &

exit 0
