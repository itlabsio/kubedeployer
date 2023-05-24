# kubedeployer

Развертывает приложения в Kubernetes.

## Особенности

* Развертывание приложений при помощи манифестов.
* Развертывание приложений при помощи kustomize.
* Манифесты могут содержать переменные окружения.
* Содержит проверку безопасности объектов Kubernetes.
* Содержит проверку безопасности docker-образов.
* Наличие режима пробного запуска в котором выполняется сборка манифестов
без их применения.

## Сборка

```shell
docker build \
  --build-arg VAULT_URL=<host-to-vault> \
  --build-arg VAULT_APPROLE_ID=<vault-approle-id> \ 
  --build-arg VAULT_APPROLE_SECRET=<vault-approle-secret> \ 
  --build-arg VAULT_SECRETS_PREFIX=<vault-secret-prefix> \
  -t kubedeployer \
  -f Dockerfile .
```

* ***VAULT_URL*** - URL по которому доступен Vault.
* ***VAULT_APPROLE_ID*** - идентификатор approle позволяющий проходить 
аутентификацию с ролью, определенной в Vault.
* ***VAULT_APPROLE_SECRET*** - секрет approle. 
* ***VAULT_SECRETS_PREFIX*** - шаблон пути к секретам с настройками подключения
к Kubernetes. По заданному шаблону Kubedeployer находит секреты и из них
выбирает тот у котого URL кластера совпадает 
(пример шаблона: template/to/cluster/*/secret).

## Команда запуска

```shell
kubedeploy options
```

Пример

```shell
kubedeploy -d orthodox --dry-run --env-file ./base.txt ./production.txt
```

### Опции

* __-d__, __--deployer__=smart: вариант деплоера:
  * orthodox - совместимость со старым вариантом деплоя, когда в проекте
    присутствуют только _yaml_ манифесты, внутри которых могут быть заданы
    переменные окружения;
  * kustomize - в проекте предполагается наличие _kustomization.yaml_;
  * smart - совмещает в себе вышеперечисленные варианты.
* __--dry-run__: включает режим сборки мафестов в один общий без применения
его на стороне кластера;
* __--env-file__ list: считывает переменные окружения из перечисленных файлов.
Если переменная окружения задана в нескольких файлах, то её итоговое значение
будет взято из последнего файла в том порядке, в котором они перечислены.

## Подключение в gitlab-ci.yml

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

### Переменные окружения

#### Обязательные

```yaml
# Адрес Kubernetes кластера в котором необходимо развернуть приложение.
KUBE_URL: "https://kube.local"
# Путь к каталогу внутри проета содержащего манифесты.
MANIFEST_FOLDER: "./manifests"
```

#### Опциональные

```yaml
# По умолчанию kubectl сохраняет настройки подключения в
# файле ${HOME}/.kube/config. В случае, если необходимо
# сохранять настройки в другой файл, то неоходимо указать
# к нему путь в данной переменной окружения.
KUBECONFIG: "${HOME}/.kube/config"
# Токен доступа к API Kubernetes.
KUBE_TOKEN: "ey3423423423dfeg34gr34..."
# В каком пространстве Kubernetes необходимо развернуть
# по умолчанию приложение, если пространство явно не
# указано в манифестах.
KUBE_NAMESPACE: "default"
# Название среды окружения, например, dev, stage, prod 
# (пустое значение по умолчанию). Указывает на каталог,
# находящийся внутри MANIFEST_FOLDER и содержит манифесты,
# которые необходимо применить для той или иной среды
# окружения (см. примеры).
ENVIRONMENT: "development"
# Скрыть или отобразить в консоли манифесты, которые  
# будут применены.
SHOW_MANIFESTS: "False"
# Сканировать docker-образы соответствующие заданному
# регулярному выражению. По умолчанию значение будет
# взято из переменной окружения CI_REGISTRY.
TRIVY_IMAGE_TEMPLATE: "registry\.example\.com"
```

## Схема работы

В момент запуска Kubedeployer определяет каталоги внутри которых будет
выполняться поиск манифестов. Основной каталог задается при помощи переменной
окружения `MANIFEST_FOLDER`, так же можно задать расширенный поиск относительно
основного каталога при помощи переменной окружения `ENVIRONMENT`, например:

```text
└── applications
    └── manifests
        ├── development
        │   ├── configurations
        │   │   └── cm.yaml
        │   └── ingress.yaml
        ├── deployment.yaml
        └── svc.yaml
        
I. Каталоги для поиска при заданной переменной окружения MANIFEST_FOLDER:

    MANIFEST_FOLDER = ./manifests
    
    ./manifests

II. Каталоги для поиска при заданных переменных MANIFEST_FOLDER и ENVIRONMENT
    (в данном случае подкаталога production внутри manifests не существует):

    MANIFEST_FOLDER = ./manifests
    ENVIRONMENT = production
    
    ./manifests

III. Каталоги для поиска при заданных переменных MANIFEST_FOLDER и ENVIRONMENT:

    MANIFEST_FOLDER = ./manifests
    ENVIRONMENT = development

    ./manifests
    ./manifests/development
    ./manifests/development/configurations
```

Внутри полученного перечня каталогов будет осуществляться поиск файла с именем
`kustomization.yaml`. В результате поиска возможны следующие сценарии:

1. `kustomization.yaml` успешно обнаружен.
2. В случае, если Kubedeployer обнаружит несколько `kustomization.yaml`, то
будет вызвана ошибка, в которой будут перечислены все найденные
`kustomization.yaml`.
Для решения проблемы необходимо в `MANIFEST_FOLDER` указать путь до каталога,
где находится нужный `kustomization.yaml`.  
3. Если `kustomization.yaml` не удается обнаружить, то Kubedeployer создаст его
в `MANIFEST_FOLDER` в секции `resources` которого будут указаны ссылки на все
`yaml` файлы, найденные в полученном перечне каталогов.

Примеры:

* Пример проекта без kustomization.yaml

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
    
    В результате работы Kubedeployer создаст kustomization.yaml:
    
    ./manifests/kustomization.yaml
        resources:
        - ./manifests/deployment.yaml
        - ./manifests/svc.yaml
        - ./manifests/development/cm.yaml
        - ./manifests/development/ingress.yaml
    ```

* Пример проекта с kustomization.yaml

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
    
    В данном случае Kubedeployer будет ссылаться на:
        ./manifests/overlays/development/kustomization.yaml
    ```

* Пример проекта с ошибкой

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
  
    В результате работы Kubedeployer будет вызвана ошибка, так как будет 
    обнаружено несколько kustomization.yaml:
        - ./manifests/kustomization.yaml
        - ./manifests/development/kustomization.yaml
        - ./manifests/development/configurations/kustomization.yaml
    ```
