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

docker pull witlox/cumulonimbi
docker run -d --net=host --name="jobmanager" witlox/cumulonimbi python cumulonimbi/job_manager/api.py

echo "Waiting for logstash and the api to start."
until $(curl --output /dev/null --silent --head --fail http://localhost:9200); do
    printf '.'
    sleep 10
done
until $(curl --output /dev/null --silent --head --fail http://localhost:5000/jobs); do
    printf '.'
    sleep 10
done
echo "All up!"

echo "Starting logstash transmitter on the api and running integration tests"
docker exec -d jobmanager beaver -c cumulonimbi/beaver.ini -t http
docker run -i --rm --net=host --name="integrationtests" witlox/cumulonimbi nosetests cumulonimbi/tests/integrationtests