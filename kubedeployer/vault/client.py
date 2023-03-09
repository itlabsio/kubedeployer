import abc
from typing import Any, Dict

import hvac


class VaultClient(abc.ABC):
    """abstract class for working with vault"""
    def read_secret(self, path: str) -> Dict[str, Any]:
        raise NotImplementedError

    def list_secrets(self, path: str) -> Dict[str, Any]:
        raise NotImplementedError


class HvacClient(VaultClient):
    """implementation of VaultClient which work via hvac"""
    def __init__(self, hvac_client: hvac.Client, mount_point: str):
        self._client = hvac_client
        self._mount_point = mount_point

    def read_secret(self, path: str) -> Dict[str, Any]:
        return self._client.secrets.kv.v2.read_secret_version(
            path=path, mount_point=self._mount_point
        )

    def list_secrets(self, path: str) -> Dict[str, Any]:
        return self._client.secrets.kv.v2.list_secrets(
            path=path, mount_point=self._mount_point
        )
