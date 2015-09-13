#!/bin/sh
echo "Startup script, version 2.3"

count=$(docker ps -a -q | wc -l)
if [ "$count" -gt 0 ]; then
    echo "Stopping and removing all running containers"
    docker stop $(docker ps -a -q) > /dev/null && echo "\tAll stopped" || echo "\tStopping Failed"
    docker rm $(docker ps -a -q) > /dev/null && echo "\tAll removed" || echo "\tRemoving Failed"
fi

echo "Getting and starting the containers"
docker pull mongo
docker run -d \
    --net=host \
    --name="mongodb" \
    mongo

docker pull pblittle/docker-logstash
docker run -d \
    -e LOGSTASH_CONFIG_URL=https://raw.githubusercontent.com/witlox/cumulonimbi/master/vagrant/logstash.conf \
    --net=host \
    --name="elk" \
    pblittle/docker-logstash

docker pull witlox/cumulonimbi

echo "Waiting for logstash to start."
until $(curl --output /dev/null --silent --head --fail http://localhost:9200); do
    printf '.'
    sleep 10
done
echo ""

echo "Waiting for mongo to start."
until $(curl --output /dev/null --silent --head --fail http://localhost:27017); do
    printf '.'
    sleep 10
done
echo ""

echo "They are up! Starting the JobManager API"
docker run -d \
    --net=host \
    --name="jobmanager" \
    -v `pwd`/Config.json:/root/Config.json \
    witlox/cumulonimbi \
    python cumulonimbi.py -a
until $(curl --output /dev/null --silent --head --fail http://localhost:5000/jobs); do
    printf '.'
    sleep 10
done
echo "All up!"
