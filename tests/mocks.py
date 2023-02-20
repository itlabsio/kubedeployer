import os
from contextlib import contextmanager
from unittest.mock import patch


@contextmanager
def mock_settings(variables: dict):
    env_variables = {
        "CI_PROJECT_ID": "fake-project",
        "CI_COMMIT_REF_NAME": "fake-commit",
        "KUBE_NAMESPACE": "default",
        "ENVIRONMENT": "stage",
        "SHOW_MANIFESTS": "True",
        "MANIFEST_FOLDER": "devops/manifests",
        "VAULT_URL": "fake-vault-url",
    }

    env_variables.update(variables)
    with patch.dict(os.environ, env_variables):
        yield
