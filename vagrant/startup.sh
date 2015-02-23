#!/bin/sh

count=$(docker ps -a -q | wc -l)
if [ "$count" -gt 0 ]; then
    echo "Stopping and removing all running containers"
    docker stop $(docker ps -a -q) > /dev/null && echo "\tAll stopped" || echo "\tStopping Failed"
    docker rm $(docker ps -a -q) > /dev/null && echo "\tAll removed" || echo "\tRemoving Failed"
fi

echo "Getting and starting the containers"
#docker pull pblittle/docker-logstash > /dev/null && echo "\tLogstash pull  OK" || echo "\tLogstack Failed"
#docker run -d --net=host --name="elk" pblittle/docker-logstash > /dev/null && echo "\tLogstash run   OK" || echo "\tLogstack Failed"

docker pull djbnjack/mongobase > /dev/null && echo "\tMongobase pull OK" || echo "\tMongobase Failed"
docker run -d --net=host --name="mongodb" djbnjack/mongobase > /dev/null && echo "\tMongobase run  OK" || echo "\tMongobase Failed"

docker pull djbnjack/jmdocker > /dev/null && echo "\tJMDocker pull  OK" || echo "\tJMDocker Failed"
docker run -d --net=host --name="jobmanager" djbnjack/jmdocker python cumulonimbi/job_manager/api.py > /dev/null && echo "\tJMDocker run   OK" || echo "\tJMDocker Failed"

echo "Waiting 15 seconds for the api to start"
sleep 15

echo "Running integration tests"
docker run -i --rm --net=host --name="integrationtests" djbnjack/jmdocker nosetests cumulonimbi/tests/integrationtests