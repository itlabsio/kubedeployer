#!/bin/sh

docker stop deployer_runner
docker rm deployer_runner

docker build --progress=plain -t deployer -f tests/containers/Dockerfile .
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock --add-host=host.docker.internal:host-gateway --name=deployer_runner deployer:latest