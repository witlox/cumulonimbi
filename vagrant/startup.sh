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

# To get all the /dev/* devices needed for sshd and alike:
export DEV_MOUNTS="-v /dev/null:/dev/null -v /dev/urandom:/dev/urandom -v /dev/random:/dev/random -v /dev/full:/dev/full -v /dev/zero:/dev/zero"
docker pull qnib/elk
docker run -d --net=host --name="elk" --privileged ${DEV_MOUNTS} qnib/elk:latest

docker pull djbnjack/mongobase && echo "\tMongobase pull OK" || echo "\tMongobase Failed"
docker run -d --net=host --name="mongodb" djbnjack/mongobase && echo "\tMongobase run  OK" || echo "\tMongobase Failed"

docker pull witlox/cumulonimbi && echo "\tJMDocker pull  OK" || echo "\tJMDocker Failed"
docker run -d --net=host --name="jobmanager" witlox/cumulonimbi python cumulonimbi/job_manager/api.py && echo "\tJMDocker run   OK" || echo "\tJMDocker Failed"

#echo "Images in system:"
#docker images

echo "Waiting 15 seconds for the api to start"
sleep 15

echo "Running integration tests"
docker run -i --rm --net=host --name="integrationtests" witlox/cumulonimbi nosetests cumulonimbi/tests/integrationtests