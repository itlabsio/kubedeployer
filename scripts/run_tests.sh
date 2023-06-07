#!/bin/sh

docker stop deployer_runner
docker rm deployer_runner

docker build --progress=plain -t deployer -f tests/containers/Dockerfile .
chmod +x tests/containers/integration_tests/integration_entrypoint.sh
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock --add-host=host.docker.internal:host-gateway --entrypoint=tests/containers/integration_tests/integration_entrypoint.sh --name=deployer_runner deployer:latest