import os
import shutil
from pathlib import Path
from unittest import mock

import hvac
import pytest

from kubedeployer.gitlab_ci.environment_variables import settings


@pytest.fixture
def data_path(tmp_path) -> Path:
    source = Path(__file__).parent / "data"
    destination = tmp_path / "data"
    shutil.copytree(source, destination)
    return destination


@pytest.fixture
def kube_config(tmp_path):
    config = tmp_path / "config"
    config.touch()

    variables = {"KUBECONFIG": str(config)}
    with mock.patch.dict(os.environ, variables):
        yield


@pytest.fixture
def hvac_client():
    return hvac.Client(url=settings.vault_url.value, token=os.getenv('VAULT_DEV_ROOT_TOKEN_ID'))
