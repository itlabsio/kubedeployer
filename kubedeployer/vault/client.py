import abc
from typing import Any, Dict

import hvac


class VaultClient(abc.ABC):

    def read_secret(self, path: str) -> Dict[str, Any]:
        raise NotImplementedError

    def list_secrets(self, path: str) -> Dict[str, Any]:
        raise NotImplementedError


class HVACClient(VaultClient):

    def __init__(self, url: str, mount_point: str,
                 role_id: str, secret_id: str):
        self._mount_point = mount_point

        self._client = hvac.Client(url=url)
        self._client.token = self.__get_token(role_id, secret_id)

    def __get_token(self, role_id: str, secret_id: str) -> str:
        response = self._client.auth_approle(role_id, secret_id)
        return response["auth"]["client_token"]

    def read_secret(self, path: str) -> Dict[str, Any]:
        return self._client.secrets.kv.v2.read_secret_version(
            path=path, mount_point=self._mount_point
        )

    def list_secrets(self, path: str) -> Dict[str, Any]:
        return self._client.secrets.kv.v2.list_secrets(
            path=path, mount_point=self._mount_point
        )
