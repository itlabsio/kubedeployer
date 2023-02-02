#!/bin/sh

docker stop deployer_runner
docker rm deployer_runner

docker build --progress=plain -t deployer -f tests/containers/Dockerfile .
docker run -v /var/run/docker.sock:/var/run/docker.sock --name=deployer_runner deployer:latest