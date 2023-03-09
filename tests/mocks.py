import os
from contextlib import contextmanager
from unittest.mock import patch

from kubedeployer.gitlab_ci import specification


@contextmanager
def mock_settings(variables: dict):
    env_variables = {
        specification.CI_PROJECT_ID_ENV_VAR: "fake-project",
        specification.CI_COMMIT_REF_NAME_ENV_VAR: "fake-commit",
        specification.KUBE_NAMESPACE_ENV_VAR: "default",
        specification.ENVIRONMENT_ENV_VAR: "stage",
        specification.SHOW_MANIFESTS_ENV_VAR: "True",
        specification.MANIFEST_FOLDER_ENV_VAR: "devops/manifests",
        specification.VAULT_URL_ENV_VAR: "fake-vault-url",
    }

    env_variables.update(variables)
    with patch.dict(os.environ, env_variables):
        yield
