#!/bin/sh

docker stop deployer_runner
docker container rm deployer_runner

docker build --progress=plain -t deployer -f e2e_tests/e2e.tests.Dockerfile .
docker run -v /var/run/docker.sock:/var/run/docker.sock  --name=deployer_runner deployer:latest