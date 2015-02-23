#!/bin/sh

count=$(docker ps -a -q | wc -l)
if [ "$count" -gt 0 ]; then
    echo "Stopping and removing all running containers"
    docker stop $(docker ps -a -q) > /dev/null && echo "\tAll stopped" || echo "\tStopping Failed"
    docker rm $(docker ps -a -q) > /dev/null && echo "\tAll removed" || echo "\tRemoving Failed"
fi

echo "Getting latest versions"
docker pull pblittle/docker-logstash > /dev/null && echo "\tLogstash  OK" || echo "\tLogstack Failed"
docker pull djbnjack/mongobase > /dev/null && echo "\tMongobase OK" || echo "\tMongobase Failed"
docker pull djbnjack/jmdocker > /dev/null && echo "\tJMDocker  OK" || echo "\tJMDocker Failed"

echo "Starting the containers"
docker run -d --net=host --name="elk" pblittle/docker-logstash > /dev/null && echo "\tLogstash  OK" || echo "\tLogstack Failed"
docker run -d --net=host --name="mongodb" djbnjack/mongobase > /dev/null && echo "\tMongobase OK" || echo "\tMongobase Failed"
docker run -d --net=host --name="jobmanager" djbnjack/jmdocker python cumulonimbi/job_manager/api.py > /dev/null && echo "\tJMDocker  OK" || echo "\tJMDocker Failed"

echo "Running integration tests"
docker run -i --rm --net=host --name="integrationtests" djbnjack/jmdocker nosetests cumulonimbi/tests/integrationtests