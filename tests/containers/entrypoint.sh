#!/bin/sh

prepare_kind() {
  # Prepare kubernetes cluster for tests
  chmod +x tests/containers/kind/prepare-kind.sh
  ./tests/containers/kind/prepare-kind.sh
}

prepare_infrastructure() {
  # Create infrastructure
  kubectl apply -f tests/containers/manifests/rbac.yaml
  token=`kubectl create token deployer`
  touch env_vars
  echo KUBE_TOKEN=$token >> env_vars
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
prepare_infrastructure
