# This Dockerfile used for imitation Gitlab runner and tests on local machine

FROM docker:20.10.17

WORKDIR /srv

COPY . .
COPY ./tests/containers/integration_tests/integration_entrypoint.sh /usr/local/bin
COPY ./tests/containers/e2e_tests/e2e_entrypoint.sh /usr/local/bin
COPY ./tests/containers/entrypoint.sh /usr/local/bin

RUN apk add --no-cache procps

ARG LIB_VERSION

ENV KUBECTL v1.24.15
ENV KIND v0.20.0
ENV VM_IP host.docker.internal
ENV DOCKER_IMAGE deployer:0.0.2
ENV KUBE_NAMESPACE default
ENV LIB_VERSION=$LIB_VERSION

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
