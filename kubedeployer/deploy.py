#!/usr/bin/python3

import os
import random
import string
import tempfile
from functools import partial
from pathlib import Path
from typing import List, Callable


from kubedeployer import console, k8s
from kubedeployer.console.wrap import TAB, indent, timestamp, colorize, Color
from kubedeployer.docker import is_docker_login
from kubedeployer.files import get_files, YAML_EXTENSIONS
from kubedeployer.gitlab_ci.annotations import get_annotations
from kubedeployer.gitlab_ci.environment_variables import settings

from kubedeployer.kustomize import get_kustomization, create_kustomization, \
    add_annotations, build_manifests
from kubedeployer.manifests import get_manifests, ROLLOUT_RESOURCES, get_images
from kubedeployer.text import envsubst
from kubedeployer.types import PathLike
from kubedeployer.vault.factory import VaultServiceFactory
from kubedeployer.security.kubesec import create_kube_security_report
from kubedeployer.security.trivy import create_trivy_report

success = partial(colorize, color=Color.GREEN)
warning = partial(colorize, color=Color.YELLOW)
error = partial(colorize, color=Color.RED)


# Formatting output of the stage (ex, Applying changes..)
stage: Callable[[str], str] = \
    lambda text: console.writeln(f"\n{success(timestamp(text))}\n")


def read_kube_token(kube_url):
    vault_service = VaultServiceFactory.create_vault_service()

    path, secret = settings.vault_secret_prefix.value.rsplit("/", maxsplit=1)
    paths = list(vault_service.get_paths(path))
    secrets = list(str(Path(p) / secret) for p in paths)

    kube_tokens = {}
    for s in secrets:
        data = vault_service.read_secret(s)
        kube_tokens[data["url"]] = data["token"]
    return kube_tokens[kube_url]


def get_manifests_paths() -> List[PathLike]:
    project_path = Path(settings.ci_project_dir.value)
    manifests_path = project_path / f"{settings.manifest_folder.value}"

    paths = [manifests_path]

    if settings.environment.value:
        overlay_path = manifests_path / f"{settings.environment.value}"
        if overlay_path.exists():
            paths.append(overlay_path / "**")
    return paths


def config_kubectl():
    kube_url = settings.kube_url.value
    kube_namespace = settings.kube_namespace.value

    try:
        kube_token = read_kube_token(kube_url)
    except Exception as e:
        console.writeln(indent(
            warning(
                f"Problem with reading kube_token from vault. "
                f"Read it from env. Detail:{str(e)}"
            ),
            prefix=TAB
        ))
        kube_token = settings.kube_token.value

    if not kube_token:
        raise ValueError("Token for Kubernetes is not set.")

    k8s.configure(
        server=kube_url,
        token=kube_token,
        namespace=kube_namespace
    )


def print_kubesec_report(filename: PathLike):
    try:
        report = create_kube_security_report()
        data = report.build(filename)
        console.writeln(indent(data, prefix=TAB))
    except Exception as e:
        console.writeln(indent(error(e), prefix=TAB))


def get_trivy_image_pattern() -> str:
    return settings.trivy_image_template.value \
           or settings.ci_registry.value \
           or r".+"


def print_trivy_report(*images: str):
    username = os.getenv("CI_REGISTRY_USER")
    password = os.getenv("CI_REGISTRY_PASSWORD")
    server = os.getenv("CI_REGISTRY")
    if not is_docker_login(server, username, password):
        console.writeln(indent(error(
            f"Docker cannot login to {server or 'registry'}"
        ), prefix=TAB))
        return

    try:
        report = create_trivy_report()
        for i in images:
            data = report.build(i)
            console.writeln(indent(data, prefix=TAB))
    except Exception as e:
        console.writeln(indent(error(e), prefix=TAB))


def run():
    try:
        stage("Let's deploy it!")

        os.environ['DEPLOY'] = ''.join(random.sample(
            string.digits + string.ascii_letters, 32))

        config_kubectl()

        tmp_path = Path(tempfile.mkdtemp())
        need_show_manifests = settings.show_manifests.value

        manifests_paths = get_manifests_paths()

        stage("Searching kustomization..")
        kustomization = get_kustomization(*manifests_paths)
        if not kustomization:
            console.writeln(indent(
                "Kustomization not found, creating..",
                prefix=TAB
            ))

            manifests_files = get_files(
                *manifests_paths, extensions=YAML_EXTENSIONS
            )
            kustomization = create_kustomization(
                Path(settings.ci_project_dir.value) /
                f"{settings.manifest_folder.value}",
                *manifests_files
            )

            console.writeln(indent(
                "Append next resources into kustomization:",
                prefix=TAB
            ))
            console.writeln(indent(
                "\n".join(f"-{str(f)}" for f in manifests_files),
                prefix=TAB * 2
            ))
        console.writeln(indent(
            f"Kustomization location {str(kustomization)}",
            prefix=TAB
        ))

        stage("Configure kustomization..")
        annotations = get_annotations()
        add_annotations(kustomization.parent, annotations=annotations)

        console.writeln(indent("Append next annotations:", prefix=TAB))
        console.writeln(indent(
            "\n".join(f"{k}: {v or ''}" for k, v in annotations.items()),
            prefix=TAB * 2
        ))

        stage("Building manifests..")
        manifests_filename = tmp_path / "manifests.yaml"
        build_manifests(kustomization.parent, manifests_filename)

        manifests_content = envsubst(manifests_filename.read_text())
        manifests_filename.write_text(manifests_content)

        if need_show_manifests:
            console.writeln(indent(manifests_content, prefix=TAB))

        stage("Scanning images..")
        image_pattern = get_trivy_image_pattern()
        images = set(get_images(manifests_content, pattern=image_pattern))
        print_trivy_report(*images)

        stage("Scanning manifests..")
        print_kubesec_report(manifests_filename)

        stage("Apply manifests..")
        applied_manifests = k8s.apply_manifests(manifests_filename)
        console.writeln(indent(applied_manifests, prefix=TAB))

        stage("Waiting for applying changes..")
        resources = "|".join(ROLLOUT_RESOURCES)
        for manifest in get_manifests(manifests_content, kind=resources):
            status = k8s.check_rollout_status(manifest)
            console.writeln(indent(status, prefix=TAB))
    except Exception as e:
        console.writeln(indent(error(e), prefix=TAB))
        console.writeln()
        raise
