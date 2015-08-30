#!/bin/sh

count=$(docker ps -a -q | wc -l)
if [ "$count" -gt 0 ]; then
    echo "Stopping and removing all running containers"
    docker stop $(docker ps -a -q) > /dev/null && echo "\tAll stopped" || echo "\tStopping Failed"
    docker rm $(docker ps -a -q) > /dev/null && echo "\tAll removed" || echo "\tRemoving Failed"
fi

echo "Getting and starting the containers"
docker pull pblittle/docker-logstash
docker run -d \
    -e LOGSTASH_CONFIG_URL=https://raw.githubusercontent.com/witlox/cumulonimbi/master/vagrant/logstash.conf \
    -p 9292:9292 -p 9200:9200 -p 9300:9300 \
    --name="elk" \
    pblittle/docker-logstash

docker pull djbnjack/mongobase
docker run -d \
    -p 27017:27017 \
    --name="mongodb" \
    djbnjack/mongobase

docker pull witlox/cumulonimbi
docker run -d \
    -p 5000:5000 \
    --name="jobmanager" \
    -v `pwd`/Config.json:/root/Config.json \
    witlox/cumulonimbi \
    python cumulonimbi.py -a

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
