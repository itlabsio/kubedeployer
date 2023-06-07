#!/bin/sh

chmod +x tests/containers/entrypoint.sh
./tests/containers/entrypoint.sh

prepare_env_vars(){
  echo SHOW_MANIFESTS="True" >> env_vars
  echo MANIFEST_FOLDER=/app/manifests/apps/non-kustomize-app-with-env >> env_vars
  echo CI_PROJECT_DIR="." >> env_vars
  echo CI_COMMIT_REF_NAME="local" >> env_vars
  echo CI_PROJECT_ID="0" >> env_vars
  echo ENVIRONMENT="stage" >> env_vars

  echo HOST_NAME="host.local" >> env_vars
  echo NAMESPACE="default" >> env_vars
  echo SERVICE_NAME="example" >> env_vars

  echo VARIABLE="test" >> env_vars
  echo IGNORED_VARIABLE="ignore" >> env_vars
  echo DIGIT_VARIABLE="123" >> env_vars

  cat env_vars
}
echo RUNNING E2E TESTS

# Check configmap is created with credentials for vault
prepare_env_vars
docker-compose --env-file env_vars -f tests/containers/docker-compose.yaml up -d

docker build --build-arg LIB_VERSION=${LIB_VERSION} -t $DOCKER_IMAGE --target e2e -f Dockerfile .
docker run --env-file env_vars --add-host host.docker.internal:host-gateway --network=kind $DOCKER_IMAGE kubedeploy
configmap_output=`kubectl get configmap non-kustomize-app --ignore-not-found`
pod_output=`kubectl get pods | grep non-kustomize-app-with-env`
if [[ -z "$configmap_output" ]]; then
  echo Configmap non-kustomize-app was not created
  exit 1
fi
if [[ -z "$pod_output" ]]; then
  echo Pod non-kustomize-app-with-env was not created
  exit 1
fi
