#!/usr/bin/python3

import os
import random
import string
import tempfile
from pathlib import Path
from typing import Type, List

from hvac.exceptions import InvalidPath as VaultInvalidPath
from dotenv import load_dotenv

from kubedeployer import console, kubectl
from kubedeployer.deployer.abstract_deployer import AbstractDeployer
from kubedeployer.docker import is_docker_login
from kubedeployer.gitlab_ci.environment_variables import settings
from kubedeployer.kubectl import KubectlError
from kubedeployer.manifests import get_manifests, ROLLOUT_RESOURCES, get_images
from kubedeployer.security.kubesec import create_kube_security_report
from kubedeployer.security.trivy import create_trivy_report
from kubedeployer.types import PathLike
from kubedeployer.vault.factory import VaultServiceFactory


def read_kube_token(kube_url):
    vault_service = VaultServiceFactory.create_vault_service()

    path, secret = settings.vault_secret_prefix.value.rsplit("/", maxsplit=1)
    paths = list(vault_service.get_paths(path))
    secrets = list(str(Path(p) / secret) for p in paths)

    kube_tokens = {}
    for s in secrets:
        try:
            data = vault_service.read_secret(s)
        except VaultInvalidPath:
            pass
        else:
            kube_tokens[data["url"]] = data["token"]
    return kube_tokens[kube_url]


def config_kubectl():
    kube_url = settings.kube_url.value
    kube_namespace = settings.kube_namespace.value

    kube_token = settings.kube_token.value
    try:
        kube_token = read_kube_token(kube_url)
    except Exception as e:
        console.warning(
            f"Problem with reading kube_token from vault. "
            f"Read it from env. Detail:{str(e)}"
        )

    if not kube_token:
        raise ValueError("Token for Kubernetes is not set.")

    kubectl.configure(
        server=kube_url,
        token=kube_token,
        namespace=kube_namespace
    )


def load_environment_variables(env_files: List[str] | None = None):
    if not env_files:
        return

    for file in env_files:
        load_dotenv(dotenv_path=file, override=True)


def print_kubesec_report(filename: PathLike):
    try:
        report = create_kube_security_report()
        data = report.build(filename)
        console.info(data, console.TAB)
    except Exception as e:
        console.error(str(e))


def get_trivy_image_pattern() -> str:
    return settings.trivy_image_template.value \
           or settings.ci_registry.value \
           or r".+"


def print_trivy_report(*images: str):
    username = os.getenv("CI_REGISTRY_USER")
    password = os.getenv("CI_REGISTRY_PASSWORD")
    server = os.getenv("CI_REGISTRY")
    if not is_docker_login(server, username, password):
        console.error(f"Docker cannot login to {server or 'registry'}")
        return

    try:
        report = create_trivy_report()
        subprocess_timeout = int(os.getenv("SUBPROCESS_TIMEOUT", "1"))
        for i in images:
            data = report.build(i, subprocess_timeout)
            console.info(data, console.TAB)
    except Exception as e:
        console.error(str(e))


def print_diff_manifests(manifests_dir: PathLike):
    try:
        diffed_manifests = kubectl.diff_manifests(manifests_dir)
        console.info(diffed_manifests, console.TAB)
    except KubectlError as e:
        console.error(str(e))


def run(
        deployer: Type[AbstractDeployer],
        dry_run: bool = False,
        env_files: List[str] | None = None
):
    try:
        console.stage("Let's deploy it!")

        os.environ['DEPLOY'] = ''.join(random.sample(
            string.digits + string.ascii_letters, 32))
        load_environment_variables(env_files)

        tmp_path = Path(tempfile.mkdtemp())
        need_show_manifests = settings.show_manifests.value

        project_path = Path(settings.ci_project_dir.value)
        manifests_path = project_path / settings.manifest_folder.value

        manifests_content, manifests_filename = deployer.deploy(tmp_path, manifests_path)

        console.stage("Manifest files ready")
        if need_show_manifests or dry_run:
            console.info(manifests_content, console.TAB)

        if dry_run:
            return

        console.stage("Scanning images..")
        image_pattern = get_trivy_image_pattern()
        images = set(get_images(manifests_content, pattern=image_pattern))
        print_trivy_report(*images)

        console.stage("Scanning manifests..")
        print_kubesec_report(manifests_filename)

        config_kubectl()

        console.stage("Diff manifests..")
        print_diff_manifests(tmp_path)

        console.stage("Apply manifests..")
        applied_manifests = kubectl.apply_manifests(manifests_filename)
        console.info(applied_manifests, console.TAB)

        console.stage("Waiting for applying changes..")
        resources = "|".join(ROLLOUT_RESOURCES)
        for manifest in get_manifests(manifests_content, kind=resources):
            status = kubectl.check_rollout_status(manifest)
            console.info(status, console.TAB)
    except Exception as e:
        console.error(str(e))
        console.writeln()
        raise
