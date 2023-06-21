# kubedeployer <sup>[RU](./docs/ru.md)</sup>

Deploy application on Kubernetes.

## Key Features

* Deploy application using manifests.
* Deploy application using kustomize.
* Manifests can contain environment variables.
* Contain security scanner for Kubernetes resources.
* Contain security scanner for docker images.
* Contain dry-run mode, where only the manifest is built without applying it.

## Installation
- [using pip](#using-pip)
- [using docker](#using-docker)

### Using pip
```shell
pip install kubedeployer
```
### Using docker
```shell
docker run itlabsio/kubedeployer
```

#### How to build

```shell
docker build \
  --build-arg VAULT_URL=<host-to-vault> \
  --build-arg VAULT_APPROLE_ID=<vault-approle-id> \ 
  --build-arg VAULT_APPROLE_SECRET=<vault-approle-secret> \ 
  --build-arg VAULT_SECRETS_PREFIX=<vault-secret-prefix> \
  -t kubedeployer \
  -f Dockerfile .
```

* ***VAULT_URL*** - Vault URL.
* ***VAULT_APPROLE_ID*** - the approle id allows machines or apps to 
authenticate with Vault-defined roles.
* ***VAULT_APPROLE_SECRET*** - approle secret. 
* ***VAULT_SECRETS_PREFIX*** - template of vault-path to secret where store
connection settings to Kubernetes (ex.: template/to/cluster/*/secret).

## Usage

```shell
kubedeploy options
```

Example

```shell
kubedeploy -d orthodox --dry-run --env-file ./base.txt ./production.txt
```

### Options

* __-d__, __-deployer__=smart: structure maintenance types
(see Supported structure maintenance types);
* __--dry-run__: only show built manifest without apply it;
* __--env-file__ list: read in a file of environment variables. If environment
variable does contain in several files, then it will be has value from last file.
* __--project-dir \<path\>__: full path to folder with project, if it is not setted,
used value from environment variable `CI_PROJECT_DIR`, if variable is not setted, as 
default value used current working directory
* __--environment \<env_name\>__: environment for builder, if it is not setted, used
value from environment variable `ENVIRONMENT`
* __--manifest-folder \<path\>__: path to folder with manifest, path is relative to project_dir. If it is not set, will get value from environment variable `MANIFEST_FOLDER`

## Supported structure maintenance types

Kubedeployer supports three structure maintenance types of manifests to deploy:
- orthodox
- smart - this one is default
- kustomize

Each deployer is responding for collecting and processing manifest files

### Orthodox
#### Collecting files
- Find yaml-files in `MANIFEST_FOLDER`;
- Append files from subdirectory with name `ENVIRONMENT`.
#### Processing files
- Replace placeholder like `${VAR_NAME}` by corresponding environment variables `VAR_NAME` in found files 
from previous step;
- Concatenate all files in one.

### Smart
Smart deployer has different behavior depending on presence of the `kustomization.yaml` file 
in `MANIFEST_FOLDER` xor `MANIFEST_FOLDER`/`ENVIRONMENT`:
- it has not been found
- it has been found

#### Kustomization.yaml has NOT been found
##### Collecting files
- Work like orthodox deployer 
##### Processing files
- Create `kustomization.yaml` with all collected yaml-files;
- Replace placeholder like orthodox deployer
- Create resulting manifest by `kustomize build`

#### Kustomization.yaml has been found
##### Collecting files
- It does not collect files because they all are listed in `kustomization.yaml`
##### Processing files
- Create resulting manifest by `kustomize build`
- Replace placeholder like orthodox deployer in resulting manifest

> If you want to have quoted values after replacing placeholders like `"123"` not `123`, you should to make double quotes around the placeholder
> like `'"${PLACEHOLDER}"'` because of specific of working kustomize
### Kustomize
If in `MANIFEST_FOLDER` were found `kustomization.yaml` file then deployer will collect files by kustomize.
Deploy happens by applying `kustomization.yaml`

> Unlike previous deployers this one does not replace placeholders and do not try to guess what can be deployed.


## How to launch in gitlab-ci.yml

```yaml
deploy:
  stage: deploy
  image: kubedeployer
  environment:
    name: development
  variables:
    KUBE_URL: $KUBERNETES_URL
    KUBE_TOKEN: $KUBERNETES_TOKEN
    KUBE_NAMESPACE: $KUBERNETES_NAMESPACE
    ENVIRONMENT: $APPLICATION_ENVIRONMENT
    MANIFEST_FOLDER: ./manifests
  script:
    - kubedeploy
```

script has options to choose deployer type (orthodox, smart and kustomize). Default value is orthodox.
Example:
```yaml
deploy:
  script:
    - kubedeploy -d smart
```

### Environments

#### Required

```yaml
# Kubernetes URL where need to deploy application.
KUBE_URL: "https://kube.local"
# Directory inside project where manifests are located.
MANIFEST_FOLDER: "./manifests"
```

#### Additional

```yaml
# If the KUBECONFIG environment variable does exist, kubectl uses an effective
# configuration that is the result of merging the files listed in the KUBECONFIG
# environment variable.
KUBECONFIG: "${HOME}/.kube/config"
# Kubernetes access token.
KUBE_TOKEN: "ey3423423423dfeg34gr34..."
# Kubernetes namespace where application will be deployed by default if
# namespace not set in manifests.
KUBE_NAMESPACE: "default"
# Environments describe where code is deployed (ex.: stage, production, ..).
ENVIRONMENT: "development"
# Show manifests that will be applied.
SHOW_MANIFESTS: "False"
# Template that allows filtering docker image names for Trivy report.
TRIVY_IMAGE_TEMPLATE: "registry\.example\.com"
```

## How it works

Kubedeployer collect directories inside which manifests will be found. Root
directory are set with variable `MANIFEST_FOLDER`, also to use extended
searching need to set value in variable `ENVIRONMENT`. For example:

```text
└── applications
    └── manifests
        ├── development
        │   ├── configurations
        │   │   └── cm.yaml
        │   └── ingress.yaml
        ├── deployment.yaml
        └── svc.yaml
        
I. Found directories if MANIFEST_FOLDER set only:

    MANIFEST_FOLDER = ./manifests
    
    ./manifests

II. Found directories if MANIFEST_FOLDER and ENVIRONMENT are set
    (in current case subdirectory `production` does not  exist):

    MANIFEST_FOLDER = ./manifests
    ENVIRONMENT = production
    
    ./manifests

III. Found directories if MANIFEST_FOLDER and ENVIRONMENT are set:

    MANIFEST_FOLDER = ./manifests
    ENVIRONMENT = development

    ./manifests
    ./manifests/development
    ./manifests/development/configurations
```

There are next variants when Kubedeployer was found `kustomization.yaml` in
getting directories:

1. `kustomization.yaml` successfully found.
2. If Kubedeployer found multiple `kustomization.yaml` files then will throw
exception. To fix it you are need set path to directory in `MANIFEST_FOLDER`
that contain required `kustomization.yaml`. 
3. Kubedeployer auto create `kustomization.yaml` in `MANIFEST_FOLER` if it 
can't find it.

Examples:

* Project without kustomization.yaml

    ```text
    └── applications
        └── manifests
            ├── development
            │   ├── cm.yaml
            │   └── ingress.yaml
            ├── production
            │   ├── cm.yaml
            │   └── ingress.yaml
            ├── deployment.yaml
            └── svc.yaml
    
    MANIFEST_FOLDER = ./manifests
    ENVIRONMENT = development
    
    Kubedeployer will create kustomization.yaml with content:
    
    ./manifests/kustomization.yaml
        resources:
        - ./manifests/deployment.yaml
        - ./manifests/svc.yaml
        - ./manifests/development/cm.yaml
        - ./manifests/development/ingress.yaml
    ```

* Project with kustomization.yaml

    ```text
    
    └── applications
        └── manifests
            ├── base
            │   ├── kustomization.yaml
            │   ├── development.yaml
            │   └── svc.yaml
            └── overlays
                ├── development
                │   ├── kustomization.yaml
                │   ├── cm.yaml
                │   └── ingress.yaml
                └── production
                    ├── kustomization.yaml
                    ├── cm.yaml
                    └── ingress.yaml
    
    MANIFEST_FOLDER = ./manifests/overlays/development
    
    In our case, Kubedeployer will use the following file:
        ./manifests/overlays/development/kustomization.yaml
    ```

* Project contains error

    ```text
    └── applications
        └── manifests
            ├── development
            │   ├── kustomization.yaml
            │   ├── ingress.yaml
            │   └── configurations
            │       ├── kustomization.yaml
            │       └── cm.yaml
            ├── kustomization.yaml
            ├── deployment.yaml
            └── svc.yaml
    
    MANIFEST_FOLDER = ./manifests
    ENVIRONMENT = development
  
    Kubedeployer will throw an exception after found multiple files:
        - ./manifests/kustomization.yaml
        - ./manifests/development/kustomization.yaml
        - ./manifests/development/configurations/kustomization.yaml
    ```
