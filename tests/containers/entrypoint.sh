#!/bin/sh

prepare_kind() {
  # Prepare kubernetes cluster for tests
  chmod +x tests/containers/kind/prepare-kind.sh
  ./tests/containers/kind/prepare-kind.sh
}

prepare_image() {
  # Build images of deployer and fixture for preparing environment for tests
  docker build -t $DOCKER_IMAGE -f Dockerfile .
}

prepare_infrastructure() {
  # Create infrastructure
  kubectl apply -f tests/containers/manifests/rbac.yaml
  secretname=`kubectl get serviceaccounts deployer -o=jsonpath='{.secrets[0].name}'`
  secret=`kubectl get secret $secretname -o=jsonpath='{.data.token}' | base64 -d`
  touch env_vars
  echo KUBE_TOKEN=$secret >> env_vars
  echo KUBE_URL="https://${REAL_IP}:6443" >> env_vars
  cat env_vars
}

if [[ $VM_IP ]]; then
  export REAL_IP=$VM_IP
else
  export REAL_IP=$(ip route|awk '/default/ { print $3 }')
fi
echo REAL_IP $REAL_IP

prepare_kind
prepare_image
prepare_infrastructure
