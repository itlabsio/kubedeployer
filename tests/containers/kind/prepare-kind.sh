#!/bin/sh

prepare_kind() {
  apk add -U wget
  apk add -U gettext

  # Install kind
  wget -O /usr/local/bin/kind https://github.com/kubernetes-sigs/kind/releases/download/${KIND}/kind-linux-amd64
  chmod +x /usr/local/bin/kind

  # Install kubectl
  wget -O /usr/local/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/${KUBECTL}/bin/linux/amd64/kubectl
  chmod +x /usr/local/bin/kubectl
}

prepare_cluster() {
  kind get clusters
  clusters="$(kind get clusters)"
  if [[ "$clusters" != "No kind clusters found." ]]; then
    kind delete cluster
  fi
  if [[ $VM_IP ]]; then
    export REAL_IP=$VM_IP
  else
    export REAL_IP=$(ip route|awk '/default/ { print $3 }')
  fi
  echo "REAL_IP", $REAL_IP
  sed -i -E -e "s/here_should_be_real_ip/$REAL_IP/g" "tests/containers/kind/config.yaml"
  kind create cluster --config=./tests/containers/kind/config.yaml
  sed -i -E -e "s/localhost|0\.0\.0\.0/$REAL_IP/g" "$HOME/.kube/config"
}

prepare_kind
prepare_cluster
