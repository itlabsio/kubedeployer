import os
import tempfile
from pathlib import Path

import pytest
import yaml

from kubedeployer.deployer.kustomize_deployer import KustomizeDeployer
from kubedeployer.deployer.orthodox_deployer import concat_files, OrthodoxDeployer
from kubedeployer.deployer.smart_deployer import SmartDeployer
from tests.unit.mocks import mock_settings


@pytest.fixture
def file_list(tmp_path):
    filename_list = ['1', '2']
    files = [tmp_path / f for f in filename_list]
    for filename in files:
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w") as f:
            f.write(f'name: {str(filename)}')
    return files


def test_concat_files(file_list):
    tmp_path = Path(tempfile.mkdtemp())
    filename = tmp_path / 'res'
    concat_files(filename, read_files=file_list)
    with open(filename) as f:
        res = f.read()
    assert res
    yaml_res = yaml.safe_load_all(res)
    for element in yaml_res:
        assert isinstance(element, dict) if element else element is None


@pytest.mark.parametrize("deployer", [OrthodoxDeployer, SmartDeployer])
class TestOrthodoxSmartDeployer:
    def test_deploy(self, deployer, tmp_data_path):
        env_variables = {
            "CI_PROJECT_DIR": str(tmp_data_path),
            "ENVIRONMENT": "stage",
            "MANIFEST_FOLDER": "manifests/apps/non-kustomize-app",
        }
        tmp_path = Path(tempfile.mkdtemp())
        with mock_settings(variables=env_variables):
            manifests_path = Path(env_variables["CI_PROJECT_DIR"]) / env_variables["MANIFEST_FOLDER"]
            manifest_content, manifests_filename = deployer.deploy(tmp_path, manifests_path)
            assert manifest_content
            assert manifests_filename
            os.remove(manifests_filename)

    def test_deploy_with_unknown_env(self, deployer, tmp_data_path):
        env_variables = {
            "CI_PROJECT_DIR": str(tmp_data_path),
            "ENVIRONMENT": "stage",
            "MANIFEST_FOLDER": "manifests/apps/non-kustomize-app-with-env",
        }
        tmp_path = Path(tempfile.mkdtemp())
        with mock_settings(variables=env_variables):
            manifests_path = Path(env_variables["CI_PROJECT_DIR"]) / env_variables["MANIFEST_FOLDER"]
            manifest_content, manifests_filename = deployer.deploy(tmp_path, manifests_path)
            assert manifest_content
            assert "${SOME_ENV_VAR}" in manifest_content
            assert manifests_filename

    def test_deploy_with_known_env(self, deployer, tmp_path, tmp_data_path):
        env_variables = {
            "CI_PROJECT_DIR": str(tmp_data_path),
            "ENVIRONMENT": "stage",
            "MANIFEST_FOLDER": "manifests/apps/non-kustomize-app-with-env",
            "SOME_ENV_VAR": "known_var"
        }
        with mock_settings(variables=env_variables):
            manifests_path = Path(env_variables["CI_PROJECT_DIR"]) / env_variables["MANIFEST_FOLDER"]
            manifest_content, manifests_filename = deployer.deploy(tmp_path, manifests_path)
            assert manifest_content
            assert "known_var" in manifest_content
            assert "${SOME_ENV_VAR}" not in manifest_content
            assert manifests_filename


class TestKustomizeDeployer:
    def test_deploy_simple(self, tmp_data_path):
        env_variables = {
            "CI_PROJECT_DIR": str(tmp_data_path),
            "ENVIRONMENT": "stage",
            "MANIFEST_FOLDER": "manifests/apps/kustomize-app/overlays/stage",
        }
        tmp_path = Path(tempfile.mkdtemp())
        with mock_settings(variables=env_variables):
            manifests_path = Path(env_variables["CI_PROJECT_DIR"]) / env_variables["MANIFEST_FOLDER"]
            manifest_content, manifests_filename = KustomizeDeployer.deploy(tmp_path, manifests_path)
            assert manifest_content
            assert manifests_filename
            os.remove(manifests_filename)

    def test_deploy_with_env(self, tmp_data_path):
        env_variables = {
            "CI_PROJECT_DIR": str(tmp_data_path),
            "ENVIRONMENT": "stage",
            "MANIFEST_FOLDER": "manifests/apps/kustomize-app-with-env/overlays/stage",
        }
        tmp_path = Path(tempfile.mkdtemp())
        with mock_settings(variables=env_variables):
            manifests_path = Path(env_variables["CI_PROJECT_DIR"]) / env_variables["MANIFEST_FOLDER"]
            manifest_content, manifests_filename = KustomizeDeployer.deploy(tmp_path, manifests_path)
            assert manifest_content
            assert "${SOME_ENV_VAR}" in manifest_content
            assert manifests_filename
            os.remove(manifests_filename)

    def test_deploy_without_kustomize(self, tmp_data_path):
        env_variables = {
            "CI_PROJECT_DIR": str(tmp_data_path),
            "ENVIRONMENT": "stage",
            "MANIFEST_FOLDER": "manifests/apps/non-kustomize-app",
        }
        tmp_path = Path(tempfile.mkdtemp())
        with mock_settings(variables=env_variables):
            manifests_path = Path(env_variables["CI_PROJECT_DIR"]) / env_variables["MANIFEST_FOLDER"]
            with pytest.raises(FileExistsError):
                KustomizeDeployer.deploy(tmp_path, manifests_path)
