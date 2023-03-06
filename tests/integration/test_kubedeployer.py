import subprocess

import pytest

from kubedeployer import deploy
from kubedeployer.deployer.orthodox_deployer import OrthodoxDeployer
from kubedeployer.deployer.smart_deployer import SmartDeployer
from kubedeployer.gitlab_ci import specification
from tests.mocks import mock_settings


def test_smart_apply_only_manifests(capsys, kube_config, data_path):
    variables = {
        specification.CI_PROJECT_DIR_ENV_VAR: str(data_path),
        specification.ENVIRONMENT_ENV_VAR: "stage",
        specification.MANIFEST_FOLDER_ENV_VAR: "manifests/apps/non-kustomize-app",
    }

    with mock_settings(variables):
        deploy.run(deployer=SmartDeployer)

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
    subprocess.run("kubectl delete deployment non-kustomize-app", shell=True)


def test_smart_apply_only_manifests_with_envs(capsys, kube_config, data_path):
    variables = {
        specification.CI_PROJECT_DIR_ENV_VAR: str(data_path),
        specification.ENVIRONMENT_ENV_VAR: "stage",
        specification.MANIFEST_FOLDER_ENV_VAR: "manifests/apps/non-kustomize-app-with-env",
    }

    with mock_settings(variables):
        deploy.run(deployer=SmartDeployer)

        result = subprocess.run(
            "kubectl get deployment non-kustomize-app-with-env",
            capture_output=True, shell=True
        )
        assert result.returncode == 0

    captured = capsys.readouterr()
    assert "Kustomization not found, creating.." in captured.out
    assert "Configure kustomization" in captured.out
    assert "Building manifests.." in captured.out
    assert "Apply manifests.." in captured.out
    assert "Waiting for applying changes.." in captured.out
    subprocess.run("kubectl delete deployment non-kustomize-app-wth-env", shell=True)


def test_smart_apply_manifests_using_kustomization(capsys, kube_config, data_path):
    variables = {
        specification.CI_PROJECT_DIR_ENV_VAR: str(data_path),
        specification.MANIFEST_FOLDER_ENV_VAR: "manifests/apps/kustomize-app/overlays/stage",
    }

    with mock_settings(variables):
        deploy.run(deployer=SmartDeployer)

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
    subprocess.run("kubectl delete deployment kustomize", shell=True)


def test_raises_on_applying_if_manifest_folder_not_exist(tmp_path, kube_config):
    with pytest.raises(FileExistsError, match="folder .* doesn't exist"):
        variables = {
            specification.CI_PROJECT_DIR_ENV_VAR: str(tmp_path),
            specification.MANIFEST_FOLDER_ENV_VAR: "non-existent-path",
        }

        with mock_settings(variables):
            deploy.run(deployer=SmartDeployer)


def test_raises_on_applying_if_manifests_files_not_found(tmp_path, kube_config):
    with pytest.raises(FileExistsError, match="Manifests files not found"):
        (tmp_path / "empty-project").mkdir()

        variables = {
            specification.CI_PROJECT_DIR_ENV_VAR: str(tmp_path),
            specification.MANIFEST_FOLDER_ENV_VAR: "empty-project",
        }
        with mock_settings(variables) as d:
            deploy.run(deployer=SmartDeployer)


def test_orthodox_apply_only_manifests(capsys, kube_config, data_path):
    variables = {
        specification.CI_PROJECT_DIR_ENV_VAR: str(data_path),
        specification.ENVIRONMENT_ENV_VAR: "stage",
        specification.MANIFEST_FOLDER_ENV_VAR: "manifests/apps/non-kustomize-app",
    }

    with mock_settings(variables):
        deploy.run(deployer=OrthodoxDeployer)

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
    subprocess.run("kubectl delete deployment non-kustomize-apptest_smart_apply_only_manifests", shell=True)


def test_orthodox_apply_only_manifests_with_envs(capsys, kube_config, data_path):
    variables = {
        specification.CI_PROJECT_DIR_ENV_VAR: str(data_path),
        specification.ENVIRONMENT_ENV_VAR: "stage",
        specification.MANIFEST_FOLDER_ENV_VAR: "manifests/apps/non-kustomize-app-with-env",
    }

    with mock_settings(variables):
        deploy.run(deployer=OrthodoxDeployer)

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
        specification.CI_PROJECT_DIR_ENV_VAR: str(data_path),
        specification.ENVIRONMENT_ENV_VAR: "stage",
        specification.MANIFEST_FOLDER_ENV_VAR: "manifests/apps/non-kustomize-app-with-env",
    }

    with mock_settings(variables):
        result = subprocess.check_output(
            "kubedeploy -d orthodox",
            stderr=subprocess.STDOUT,
            shell=True
        )
        assert "Searching yaml files..." in str(result)
        assert "Processing found yaml files..." in str(result)
        assert "Manifest files ready" in str(result)


def test_kube_smart_apply_manifests_using_kustomization(capsys, kube_config, data_path):
    variables = {
        specification.CI_PROJECT_DIR_ENV_VAR: str(data_path),
        specification.MANIFEST_FOLDER_ENV_VAR: "manifests/apps/kustomize-app/overlays/stage",
    }

    with mock_settings(variables):
        result = subprocess.check_output(
            "kubedeploy",
            stderr=subprocess.STDOUT,
            shell=True
        )
        assert "Configure kustomization" in str(result)
        assert "Building manifests.." in str(result)
        assert "Apply manifests.." in str(result)
        assert "Waiting for applying changes.." in str(result)
