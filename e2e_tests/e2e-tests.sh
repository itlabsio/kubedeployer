#!/bin/sh

prepare_image() {
  # build images of deployer and fixture for preparing environment for tests
  docker build -t $DOCKER_IMAGE -f Dockerfile .
}

prepare_infrastructure() {
  # create infrastructure
  kubectl apply -f e2e_tests/kind/e2e-rbac.yaml
  secretname=`kubectl get serviceaccounts deployer -o=jsonpath='{.secrets[0].name}'`
  echo "SECRETNAME ", secretname
  secret=`kubectl get secret $secretname -o=jsonpath='{.data.token}' | base64 -d`
  echo "SECRET ", secret
  touch env_vars
  echo KUBE_TOKEN=$secret >> env_vars
  cat env_vars
}

e2e_tests() {
  # check configmap is created with credentials for vault
  docker-compose --env-file env_vars -f e2e_tests/docker-compose-integration-test.yaml up --abort-on-container-exit --exit-code-from tester --build
  exit_code=$?
  echo "EXITCODE e2e-tests ", $exit_code
  exit $exit_code
}

if [[ $VM_IP ]]; then
  export REAL_IP=$VM_IP
else
  export REAL_IP=$(ip route|awk '/default/ { print $3 }')
fi
echo REAL_IP $REAL_IP
# prepare kubernetes cluster for tests
chmod +x e2e_tests/kind/prepare-kind.sh
./e2e_tests/kind/prepare-kind.sh
prepare_image
prepare_infrastructure
e2e_tests
