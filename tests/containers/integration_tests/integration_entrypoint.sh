#!/bin/sh

chmod +x tests/containers/entrypoint.sh
./tests/containers/entrypoint.sh

echo RUNNING TESTS
# Check configmap is created with credentials for vault
docker-compose --env-file env_vars -f tests/containers/docker-compose.yaml -f tests/containers/integration_tests/docker-compose.yaml up --abort-on-container-exit --exit-code-from tester --build
exit_code=$?
echo "EXITCODE tests", $exit_code
exit $exit_code
