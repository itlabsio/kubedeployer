import os
from pathlib import Path
from unittest import mock

import pytest


@pytest.fixture
def data_path() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture
def kube_config(tmp_path):
    config = tmp_path / "config"
    config.touch()

    variables = {"KUBECONFIG": str(config)}
    with mock.patch.dict(os.environ, variables):
        yield
