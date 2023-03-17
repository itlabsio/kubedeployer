import subprocess

import pytest

from kubedeployer import kubectl
from kubedeployer.manifests import get_manifests, InvalidRolloutResource


@pytest.fixture
def manifests(data_path):
    with open(data_path / "manifests/manifests.yaml", "r") as f:
        content = f.read()
        return list(get_manifests(content, kind="Service"))


def test_configure_kubectl(kube_config):
    kubectl.configure(
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


def test_apply_manifests(data_path):
    path = data_path / "manifests/apps/kustomize-app"
    result = kubectl.apply_manifests(
        path / "base/deployment.yaml",
        path / "base/service.yaml",
        path / "overlays/stage/configmap.yaml",
        dry_run=True
    )

    assert "service/kustomize-app created" in result
    assert "deployment.apps/kustomize-app created" in result
    assert "configmap/kustomize-app created" in result


def test_raises_applying_with_empty_manifests():
    with pytest.raises(kubectl.KubectlError, match="manifests not found"):
        kubectl.apply_manifests(dry_run=True)


def test_raises_applying_with_unsupported_yaml(data_path):
    unsupported_yaml = data_path / "manifests/apps/kustomize-app/base/kustomization.yaml"
    with pytest.raises(kubectl.KubectlError, match="no matches for kind"):
        kubectl.apply_manifests(unsupported_yaml, dry_run=True)


def test_raises_rollout_status_for_invalid_resource(manifests):
    with pytest.raises(InvalidRolloutResource):
        kubectl.check_rollout_status(manifests.pop())


def test_diff_manifests(data_path):
    result = kubectl.diff_manifests(
        data_path / "manifests/manifests.yaml"
    )

    assert "+kind: Service" in result
    assert "+kind: Deployment" in result


def test_diff_manifests_manifest_does_not_exist(data_path):
    with pytest.raises(kubectl.KubectlError, match="does not exist"):
        kubectl.diff_manifests(data_path / "manifests/non-existent-manifest.yaml")
