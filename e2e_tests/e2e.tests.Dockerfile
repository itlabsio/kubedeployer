FROM docker:20.10.17
WORKDIR /srv
# докерфайл нужен только для локальной разработки, так как он нужен для иммитации раннера в gitlab. И джобы в CI,
# отвечающий за e2e-тесты
COPY . .

RUN apk add --no-cache procps
RUN pwd
RUN ls

ENV KUBECTL v1.23.5
ENV KIND v0.17.0
ENV VM_IP host.docker.internal
ENV DOCKER_IMAGE deployer:0.0.2
ENV KUBE_NAMESPACE default

RUN chmod +x e2e_tests/e2e-tests.sh
CMD ./e2e_tests/e2e-tests.sh
