# This Dockerfile used for imitation Gitlab runner and tests on local machine

FROM docker:20.10.17

WORKDIR /srv

COPY . .
COPY ./tests/containers/entrypoint.sh /usr/local/bin

RUN apk add --no-cache procps

ENV KUBECTL v1.23.5
ENV KIND v0.17.0
ENV VM_IP host.docker.internal
ENV DOCKER_IMAGE deployer:0.0.2
ENV KUBE_NAMESPACE default

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
