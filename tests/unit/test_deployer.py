import tempfile
from pathlib import Path

import pytest
import yaml

from kubedeployer.deployer.kustomize_deployer import KustomizeDeployer
from kubedeployer.deployer.orthodox_deployer import concat_files, OrthodoxDeployer
from kubedeployer.deployer.smart_deployer import SmartDeployer
from kubedeployer.gitlab_ci import specification
from tests.mocks import mock_settings


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


def get_manifests_path(env_variables: dict) -> Path:
    ci_project_dir_path = Path(env_variables[specification.CI_PROJECT_DIR_ENV_VAR])
    return ci_project_dir_path / env_variables[specification.MANIFEST_FOLDER_ENV_VAR]


@pytest.mark.parametrize("deployer", [OrthodoxDeployer, SmartDeployer])
class TestOrthodoxSmartDeployer:
    """Tests for OrthodoxDeployer and SmartDeployer without kustomization.yaml"""

    def test_deploy(self, deployer, data_path):
        """simple test"""
        env_variables = {
            specification.CI_PROJECT_DIR_ENV_VAR: str(data_path),
            specification.ENVIRONMENT_ENV_VAR: "stage",
            specification.MANIFEST_FOLDER_ENV_VAR: "manifests/apps/non-kustomize-app",
        }
        tmp_path = Path(tempfile.mkdtemp())
        with mock_settings(variables=env_variables):
            manifests_path = get_manifests_path(env_variables)
            manifest_content, manifests_filename = deployer.deploy(tmp_path, manifests_path)
            assert manifest_content
            assert manifests_filename

    def test_deploy_with_unknown_env(self, deployer, data_path):
        env_variables = {
            specification.CI_PROJECT_DIR_ENV_VAR: str(data_path),
            specification.ENVIRONMENT_ENV_VAR: "stage",
            specification.MANIFEST_FOLDER_ENV_VAR: "manifests/apps/non-kustomize-app-with-env",
        }
        tmp_path = Path(tempfile.mkdtemp())
        with mock_settings(variables=env_variables):
            manifests_path = get_manifests_path(env_variables)
            manifest_content, manifests_filename = deployer.deploy(tmp_path, manifests_path)
            assert manifest_content
            assert "${SOME_ENV_VAR}" in manifest_content
            assert manifests_filename

    def test_deploy_with_known_env(self, deployer, tmp_path, data_path):
        env_variables = {
            specification.CI_PROJECT_DIR_ENV_VAR: str(data_path),
            specification.ENVIRONMENT_ENV_VAR: "stage",
            specification.MANIFEST_FOLDER_ENV_VAR: "manifests/apps/non-kustomize-app-with-env",
            "SOME_ENV_VAR": "known_var",
            "QUOTED_SOME_ENV_VAR": "123",

        }
        with mock_settings(variables=env_variables):
            manifests_path = get_manifests_path(env_variables)
            manifest_content, manifests_filename = deployer.deploy(tmp_path, manifests_path)
            assert manifest_content
            assert "known_var" in manifest_content
            assert "${SOME_ENV_VAR}" not in manifest_content
            assert "\"123\"" in manifest_content
            assert manifests_filename


class TestKustomizeDeployer:
    def test_deploy_simple(self, data_path):
        env_variables = {
            specification.CI_PROJECT_DIR_ENV_VAR: str(data_path),
            specification.ENVIRONMENT_ENV_VAR: "stage",
            specification.MANIFEST_FOLDER_ENV_VAR: "manifests/apps/kustomize-app/overlays/stage",
        }
        tmp_path = Path(tempfile.mkdtemp())
        with mock_settings(variables=env_variables):
            manifests_path = get_manifests_path(env_variables)
            manifest_content, manifests_filename = KustomizeDeployer.deploy(tmp_path, manifests_path)
            assert manifest_content
            assert manifests_filename

    def test_deploy_with_env(self, data_path):
        env_variables = {
            specification.CI_PROJECT_DIR_ENV_VAR: str(data_path),
            specification.ENVIRONMENT_ENV_VAR: "stage",
            specification.MANIFEST_FOLDER_ENV_VAR: "manifests/apps/kustomize-app-with-env/overlays/stage",
        }
        tmp_path = Path(tempfile.mkdtemp())
        with mock_settings(variables=env_variables):
            manifests_path = get_manifests_path(env_variables)
            manifest_content, manifests_filename = KustomizeDeployer.deploy(tmp_path, manifests_path)
            assert manifest_content
            assert "${SOME_ENV_VAR}" in manifest_content
            assert manifests_filename

    def test_deploy_without_kustomize(self, data_path):
        """
        Test deploying by SmartDeployer where:
        """
        env_variables = {
            specification.CI_PROJECT_DIR_ENV_VAR: str(data_path),
            specification.ENVIRONMENT_ENV_VAR: "stage",
            specification.MANIFEST_FOLDER_ENV_VAR: "manifests/apps/non-kustomize-app",
        }
        tmp_path = Path(tempfile.mkdtemp())
        with mock_settings(variables=env_variables):
            manifests_path = get_manifests_path(env_variables)
            with pytest.raises(FileExistsError):
                KustomizeDeployer.deploy(tmp_path, manifests_path)


class TestSmartDeployer:
    def test_deploy_kustomize_with_env(self, data_path):
        """
        Test deploying by SmartDeployer where:
        - kustomization.yaml in manifest folder
        - container has env with placeholder, which will be replaced by string of digits.
        Tested two cases: quoted and double-quoted placeholder
        """
        env_variables = {
            specification.CI_PROJECT_DIR_ENV_VAR: str(data_path),
            specification.ENVIRONMENT_ENV_VAR: "stage",
            specification.MANIFEST_FOLDER_ENV_VAR: "manifests/apps/kustomize-app-with-env/overlays/stage",
            "SOME_ENV_VAR": "known_var",
            "QUOTED_SOME_ENV_VAR": "123",
            "DOUBLE_QUOTED_SOME_ENV_VAR": "456",
        }
        tmp_path = Path(tempfile.mkdtemp())
        with mock_settings(variables=env_variables):
            manifests_path = get_manifests_path(env_variables)
            manifest_content, manifests_filename = SmartDeployer.deploy(tmp_path, manifests_path)
            assert manifest_content
            assert "known_var" in manifest_content
            assert "\"123\"" not in manifest_content
            assert "123" in manifest_content
            assert "\"456\"" in manifest_content
            assert manifests_filename
