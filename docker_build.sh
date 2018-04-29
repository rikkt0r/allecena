#!/bin/bash

ALLECENA_PATH="`dirname \"$0\"`"

docker build -f $ALLECENA_PATH/docker/Dockerfile_http -t allecena_http:latest $ALLECENA_PATH
docker build -f $ALLECENA_PATH/docker/Dockerfile_celery -t allecena_celery:latest $ALLECENA_PATH
docker build -f $ALLECENA_PATH/docker/Dockerfile_celerybeat -t allecena_celerybeat:latest $ALLECENA_PATH
