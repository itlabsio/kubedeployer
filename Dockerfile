FROM python:3.10.7-alpine3.16 AS base

ARG VAULT_URL
ARG VAULT_APPROLE_ID
ARG VAULT_APPROLE_SECRET
ARG VAULT_SECRETS_PREFIX
ARG LIB_VERSION

ENV VAULT_APPROLE_ID=$VAULT_APPROLE_ID
ENV VAULT_APPROLE_SECRET=$VAULT_APPROLE_SECRET
ENV VAULT_SECRETS_PREFIX=$VAULT_SECRETS_PREFIX
ENV DOCKER_VERSION=20.10.20-r0
ENV KUBE_VERSION=v1.24.14
ENV KUSTOMIZE_VERSION=v4.5.7
ENV KUBESEC_VERSION=v2.11.5
ENV TRIVY_VERSION=v0.30.4
ENV VAULT_URL=$VAULT_URL
ENV LIB_VERSION=$LIB_VERSION

COPY kubedeploy /usr/local/bin/kubedeploy

RUN chmod +x /usr/local/bin/kubedeploy \
 && apk add --no-cache --virtual .build-deps gcc libressl-dev musl-dev libffi-dev \
 && pip install cryptography==37.0.2 \
 && apk del .build-deps \
 && apk add --update ca-certificates openssl curl jq docker=${DOCKER_VERSION} \
 && curl --output /usr/local/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/${KUBE_VERSION}/bin/linux/amd64/kubectl \
 && chmod +x /usr/local/bin/kubectl \
 && curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin ${TRIVY_VERSION} \
 && curl -L --output kubesec_linux_amd64.tar.gz https://github.com/controlplaneio/kubesec/releases/download/${KUBESEC_VERSION}/kubesec_linux_amd64.tar.gz \
 && tar xvf kubesec_linux_amd64.tar.gz kubesec -C /usr/local/bin/ \
 && chmod +x /usr/local/bin/kubesec \
 && rm kubesec_linux_amd64.tar.gz \
 && curl -L --output kustomize_linux_amd64.tar.gz https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2F${KUSTOMIZE_VERSION}/kustomize_${KUSTOMIZE_VERSION}_linux_amd64.tar.gz \
 && tar xvf kustomize_linux_amd64.tar.gz kustomize -C /usr/local/bin/ \
 && chmod +x /usr/local/bin/kustomize \
 && rm kustomize_linux_amd64.tar.gz \
 && rm /var/cache/apk/* 

WORKDIR /app

COPY kubedeployer ./kubedeployer

CMD /usr/local/bin/kubedeploy


FROM base AS tests

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY tests ./tests

FROM base AS release-to-test
RUN pip install --extra-index-url https://test.pypi.org/simple/ kubedeployer==${LIB_VERSION}

FROM release-to-test AS e2e
COPY tests/data/manifests ./manifests

FROM base AS release
RUN pip install kubedeployer==${LIB_VERSION}
