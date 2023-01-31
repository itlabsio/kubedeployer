import os
import subprocess
from unittest import mock

import pytest

from kubedeployer.k8s import configure, apply_manifests, KubectlError, \
    check_rollout_status, diff_manifests
from kubedeployer.manifests import get_manifests, InvalidRolloutResource


def is_kubectl_not_found() -> bool:
    cmd = "kubectl get deployments"
    result = subprocess.run(cmd, shell=True)
    return result.returncode != 0


@pytest.fixture
def kubeconfig(tmp_path):
    config = tmp_path / "config"
    config.touch()

    variables = {"KUBECONFIG": str(config)}
    with mock.patch.dict(os.environ, variables):
        yield


@pytest.fixture
def manifests(data_path):
    with open(data_path / "manifests/manifests.yaml", "r") as f:
        content = f.read()
        return list(get_manifests(content, kind="Service"))


@pytest.mark.skipif(is_kubectl_not_found(), reason="kubectl not found")
def test_configure_kubectl(kubeconfig):
    configure(
        server="https://kube.local",
        token="token-example",
        namespace="namespace-example",
        context="context-example",
    )

    result = subprocess.run(
        ["kubectl config view"],
        capture_output=True, shell=True
    )
    config = result.stdout.decode("utf-8")
    assert "current-context: context-example" in config
    assert "server: https://kube.local" in config


@pytest.mark.skipif(is_kubectl_not_found(), reason="kubectl not found")
def test_apply_manifests(data_path):
    path = data_path / "apps/kustomize-app"
    result = apply_manifests(
        path / "base/deployment.yaml",
        path / "base/service.yaml",
        path / "overlays/stage/configmap.yaml",
        dry_run=True
    )

    assert "service/kustomize-app created" in result
    assert "deployment.apps/kustomize-app created" in result
    assert "configmap/kustomize-app created" in result


@pytest.mark.skipif(is_kubectl_not_found(), reason="kubectl not found")
def test_raises_applying_with_empty_manifests():
    with pytest.raises(KubectlError, match="manifests not found"):
        apply_manifests(dry_run=True)


@pytest.mark.skipif(is_kubectl_not_found(), reason="kubectl not found")
def test_raises_applying_with_unsupported_yaml(data_path):
    unsupported_yaml = data_path / "apps/kustomize-app/base/kustomization.yaml"
    with pytest.raises(KubectlError, match="no matches for kind"):
        apply_manifests(unsupported_yaml, dry_run=True)


@pytest.mark.skipif(is_kubectl_not_found(), reason="kubectl not found")
def test_raises_rollout_status_for_invalid_resource(manifests):
    with pytest.raises(InvalidRolloutResource):
        check_rollout_status(manifests.pop())


@pytest.mark.skipif(is_kubectl_not_found(), reason="kubectl not found")
def test_diff_manifests(data_path):
    result = diff_manifests(
        data_path / "apps/kustomize-app/base/deployment.yaml"
    )

    assert "diff -u -N" in result
    assert "+kind: Deployment" in result


@pytest.mark.skipif(is_kubectl_not_found(), reason="kubectl not found")
def test_diff_manifests_manifest_does_not_exist(data_path):
    with pytest.raises(KubectlError, match="does not exist"):
        diff_manifests(data_path / "apps/kustomize-app/base/no_manifest.yaml")
