import os
import pytest

from contextlib import contextmanager
from unittest.mock import patch

from kubedeployer import deploy


@contextmanager
def deployer(**override_variables):
    variables = {
        "CI_PROJECT_ID": "fake-project",
        "CI_COMMIT_REF_NAME": "fake-commit",

        "KUBE_URL": "fake-kube-url",
        "KUBE_TOKEN": "fake-kube-token",
        "KUBE_NAMESPACE": "default",

        "ENVIRONMENT": "stage",
        "SHOW_MANIFESTS": "True",
        "MANIFEST_FOLDER": "devops/manifests",

        "VAULT_URL": "fake-vault-url",
    }

    variables.update(**override_variables)
    with patch.dict(os.environ, **variables):
        yield deploy


@pytest.mark.skip
def test_apply_only_manifests(kubeconfig):
    pass


@pytest.mark.skip
def test_apply_manifests_using_kustomization(kubeconfig):
    pass


def test_raises_on_applying_if_manifest_folder_not_exist(tmp_path, kubeconfig):
    with pytest.raises(FileExistsError, match="folder .* doesn't exist"):
        variables = {
            "CI_PROJECT_DIR": str(tmp_path),
            "MANIFEST_FOLDER": "non-existent-path",
        }

        with deployer(**variables) as d:
            d.run()


def test_raises_on_applying_if_manifests_files_not_found(tmp_path, kubeconfig):
    with pytest.raises(FileExistsError, match="Manifests files not found"):
        (tmp_path / "empty-project").mkdir()

        variables = {
            "CI_PROJECT_DIR": str(tmp_path),
            "MANIFEST_FOLDER": "empty-project",
        }
        with deployer(**variables) as d:
            d.run()
