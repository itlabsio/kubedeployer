import os
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Dict
from unittest.mock import patch

import pytest

from kubedeployer import deploy
from kubedeployer.deployer.orthodox_deployer import OrthodoxDeployer
from kubedeployer.deployer.smart_deployer import SmartDeployer


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


def delete_kustomize(path: Path):
    with os.scandir(path) as files:
        for f in files:
            f: os.DirEntry
            if f.name in ['kustomization.yaml', 'kustomization.yml']:
                os.remove(f)
            elif f.is_dir():
                delete_kustomize(path / Path(f.name))


def test_smart_apply_only_manifests(capsys, kube_config, data_path):
    variables = {
        "CI_PROJECT_DIR": str(data_path),
        "ENVIRONMENT": "stage",
        "MANIFEST_FOLDER": "manifests/apps/non-kustomize-app",
    }

    with deployer(variables) as d:
        d.run(deployer=SmartDeployer)

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
    manifests_path = Path(variables["CI_PROJECT_DIR"]) / variables["MANIFEST_FOLDER"]
    delete_kustomize(manifests_path)


def test_smart_apply_manifests_using_kustomization(capsys, kube_config, data_path):
    variables = {
        "CI_PROJECT_DIR": str(data_path),
        "MANIFEST_FOLDER": "manifests/apps/kustomize-app/overlays/stage",
    }

    with deployer(variables) as d:
        d.run(deployer=SmartDeployer)

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
            d.run(deployer=SmartDeployer)


def test_raises_on_applying_if_manifests_files_not_found(tmp_path, kube_config):
    with pytest.raises(FileExistsError, match="Manifests files not found"):
        (tmp_path / "empty-project").mkdir()

        variables = {
            "CI_PROJECT_DIR": str(tmp_path),
            "MANIFEST_FOLDER": "empty-project",
        }
        with deployer(variables) as d:
            d.run(deployer=SmartDeployer)


def test_orthodox_apply_only_manifests(capsys, kube_config, data_path):
    variables = {
        "CI_PROJECT_DIR": str(data_path),
        "ENVIRONMENT": "stage",
        "MANIFEST_FOLDER": "manifests/apps/non-kustomize-app",
    }

    with deployer(variables) as d:
        d.run(deployer=OrthodoxDeployer)

        result = subprocess.run(
            "kubectl get deployment non-kustomize-app",
            capture_output=True, shell=True
        )
        assert result.returncode == 0

    captured = capsys.readouterr()
    print(captured.out)
    assert "Searching yaml files..." in captured.out
    assert "Processing found yaml files..." in captured.out
    assert "Manifest files ready" in captured.out


def test_orthodox_apply_only_manifests_with_envs(capsys, kube_config, data_path):
    variables = {
        "CI_PROJECT_DIR": str(data_path),
        "ENVIRONMENT": "stage",
        "MANIFEST_FOLDER": "manifests/apps/non-kustomize-app-with-env",
    }

    with deployer(variables) as d:
        d.run(deployer=OrthodoxDeployer)

        result = subprocess.run(
            "kubectl get deployment non-kustomize-app-with-env",
            capture_output=True, shell=True
        )
        assert result.returncode == 0

    captured = capsys.readouterr()
    assert "Searching yaml files..." in captured.out
    assert "Processing found yaml files..." in captured.out
    assert "Manifest files ready" in captured.out


def test_commandline_help(capsys):
    result = subprocess.check_output(
        "kubedeploy --help",
        stderr=subprocess.STDOUT,
        shell=True
    )
    assert "deploy by available choices: orthodox, kustomize" in str(result)


def test_kube_orthodox_apply_only_manifests_with_envs(capsys, kube_config, data_path):
    variables = {
        "CI_PROJECT_DIR": str(data_path),
        "ENVIRONMENT": "stage",
        "MANIFEST_FOLDER": "manifests/apps/non-kustomize-app-with-env",
    }

    with deployer(variables):
        result = subprocess.check_output(
            "kubedeploy",
            stderr=subprocess.STDOUT,
            shell=True
        )
        assert "Searching yaml files..." in str(result)
        assert "Processing found yaml files..." in str(result)
        assert "Manifest files ready" in str(result)


def test_kube_smart_apply_manifests_using_kustomization(capsys, kube_config, data_path):
    variables = {
        "CI_PROJECT_DIR": str(data_path),
        "MANIFEST_FOLDER": "manifests/apps/kustomize-app/overlays/stage",
    }

    with deployer(variables) as d:
        result = subprocess.check_output(
            "kubedeploy -d smart",
            stderr=subprocess.STDOUT,
            shell=True
        )
        assert "Configure kustomization" in str(result)
        assert "Building manifests.." in str(result)
        assert "Apply manifests.." in str(result)
        assert "Waiting for applying changes.." in str(result)
