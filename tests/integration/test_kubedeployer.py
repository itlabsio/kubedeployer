import os
import subprocess
from typing import Dict

import pytest

from contextlib import contextmanager
from unittest.mock import patch

from kubedeployer import deploy


@contextmanager
def deployer(override_variables: Dict[str, str]):
    variables = {
        "CI_PROJECT_ID": "fake-project",
        "CI_COMMIT_REF_NAME": "fake-commit",

        "KUBE_NAMESPACE": "default",

        "ENVIRONMENT": "stage",
        "SHOW_MANIFESTS": "True",
        "MANIFEST_FOLDER": "devops/manifests",

        "VAULT_URL": "fake-vault-url",
    }

    variables.update(override_variables)
    with patch.dict(os.environ, variables):
        yield deploy


def test_apply_only_manifests(capsys, kube_config, data_path):
    variables = {
        "CI_PROJECT_DIR": str(data_path),

        "ENVIRONMENT": "stage",
        "MANIFEST_FOLDER": "manifests/apps/non-kustomize-app",
    }

    with deployer(variables) as d:
        d.run()

        result = subprocess.run(
            "kubectl get deployment non-kustomize-app",
            capture_output=True, shell=True
        )
        assert result.returncode == 0

    captured = capsys.readouterr()
    assert "Kustomization not found, creating.." in captured.out
    assert "Configure kustomization" in captured.out
    assert "Building manifests.." in captured.out
    assert "Apply manifests.." in captured.out
    assert "Waiting for applying changes.." in captured.out


def test_apply_manifests_using_kustomization(capsys, kube_config, data_path):
    variables = {
        "CI_PROJECT_DIR": str(data_path),

        "MANIFEST_FOLDER": "manifests/apps/kustomize-app/overlays/stage",
    }

    with deployer(variables) as d:
        d.run()

        result = subprocess.run(
            "kubectl get deployment kustomize-app",
            capture_output=True, shell=True
        )
        assert result.returncode == 0

    captured = capsys.readouterr()
    assert "Configure kustomization" in captured.out
    assert "Building manifests.." in captured.out
    assert "Apply manifests.." in captured.out
    assert "Waiting for applying changes.." in captured.out


def test_raises_on_applying_if_manifest_folder_not_exist(tmp_path, kube_config):
    with pytest.raises(FileExistsError, match="folder .* doesn't exist"):
        variables = {
            "CI_PROJECT_DIR": str(tmp_path),
            "MANIFEST_FOLDER": "non-existent-path",
        }

        with deployer(variables) as d:
            d.run()


def test_raises_on_applying_if_manifests_files_not_found(tmp_path, kube_config):
    with pytest.raises(FileExistsError, match="Manifests files not found"):
        (tmp_path / "empty-project").mkdir()

        variables = {
            "CI_PROJECT_DIR": str(tmp_path),
            "MANIFEST_FOLDER": "empty-project",
        }
        with deployer(variables) as d:
            d.run()
