#!/bin/sh
sudo docker pull pblittle/docker-logstash
sudo docker pull djbnjack/mongobase
sudo docker pull djbnjack/jmdocker
sudo docker run -d --net=host --name="elk" pblittle/docker-logstash
sudo docker run -d --net=host --name="mongodb" djbnjack/mongobase
sudo docker run -d --net=host --name="jobmanager" djbnjack/jmdocker