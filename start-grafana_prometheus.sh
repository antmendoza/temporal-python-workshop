#!/bin/sh


cd ./grafana

docker compose down --remove-orphans

docker compose up --remove-orphans



