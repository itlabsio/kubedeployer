#!/bin/sh

docker stop deployer_runner
docker rm deployer_runner

while getopts "v:" opt; do
  case "$opt" in
    v) version=$OPTARG;;
  esac
done

docker build --build-arg LIB_VERSION=$version --progress=plain -t deployer -f tests/containers/Dockerfile .
chmod +x tests/containers/e2e_tests/e2e_entrypoint.sh
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock --add-host=host.docker.internal:host-gateway --entrypoint=tests/containers/e2e_tests/e2e_entrypoint.sh --name=deployer_runner deployer:latest