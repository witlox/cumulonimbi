#!/bin/sh

count=$(docker ps -a -q | wc -l)
if [ "$count" -gt 0 ]; then
    echo "Stopping and removing all running containers"
    docker stop $(docker ps -a -q) > /dev/null && echo "\tAll stopped" || echo "\tStopping Failed"
    docker rm $(docker ps -a -q) > /dev/null && echo "\tAll removed" || echo "\tRemoving Failed"
fi

echo "Getting and starting the containers"
docker pull pblittle/docker-logstash
docker run -d --net=host --name="elk" pblittle/docker-logstash

docker pull djbnjack/mongobase
docker run -d --net=host --name="mongodb" djbnjack/mongobase

echo "Waiting 60 seconds for logstash to start"
sleep 60

docker pull witlox/cumulonimbi
docker run -d --net=host --name="jobmanager" witlox/cumulonimbi python cumulonimbi/job_manager/api.py

#echo "Images in system:"
#docker images

echo "Waiting 15 seconds for the api to start"
sleep 15

echo "Running integration tests"
docker run -i --rm --net=host --name="integrationtests" witlox/cumulonimbi nosetests cumulonimbi/tests/integrationtests