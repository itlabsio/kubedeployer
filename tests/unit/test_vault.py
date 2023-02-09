from typing import Any, Dict, Optional

import pytest

from kubedeployer.vault.client import VaultClient
from kubedeployer.vault.service import VaultService


class FakeVaultClient(VaultClient):

    def __init__(self, secret_store: Dict[str, Any]):
        self._secret_store = secret_store

    def __find_item(self, obj: dict, path: str) -> Optional[Dict[str, Any]]:
        if obj and "/" in path:
            item, loc = path.split("/", maxsplit=1)
            return self.__find_item(obj.get(f"{item}/"), loc)
        return obj and (obj.get(path) or obj.get(f"{path}/")) or None

        pass

    def read_secret(self, path: str) -> Dict[str, Any]:
        if path.endswith("/"):
            return {}

        data = self.__find_item(self._secret_store, path)
        if not data:
            return {}

        return {"data": data}

    def list_secrets(self, path: str) -> Dict[str, Any]:
        data = self.__find_item(self._secret_store, path)
        if not data:
            return {}

        return {"data": {"keys": list(data.keys())}}


@pytest.fixture
def vault_client() -> FakeVaultClient:
    return FakeVaultClient({
        "secret/": {
            "common/": {
                "development/": {
                    "alpha/": {
                        "default": {"url": "localhost"},
                        "system": {"url": "localhost"},
                    },
                    "gamma/": {
                        "default": {"url": "localhost"},
                        "system": {"url": "localhost"},
                    }
                },
                "production/": {
                    "default": {"url": "localhost"},
                    "alpha/": {
                        "default": {"url": "localhost"},
                        "system": {"url": "localhost"},
                    }
                }
            }
        }
    })


def test_list_secrets_by_path(vault_client):
    service = VaultService(vault_client)
    secrets = service.list_secrets("secret/common/production/default")
    assert secrets == [
        "secret/common/production/default",
    ]


def test_list_secrets_by_path_ended_by_template(vault_client):
    service = VaultService(vault_client)
    secrets = service.list_secrets("secret/common/production/*")
    assert secrets == ["secret/common/production/default"]


def test_list_secrets_by_complex_template_path(vault_client):
    service = VaultService(vault_client)
    secrets = service.list_secrets("secret/common/*/*/default")
    assert secrets == [
        "secret/common/development/alpha/default",
        "secret/common/development/gamma/default",
        "secret/common/production/alpha/default",
    ]
