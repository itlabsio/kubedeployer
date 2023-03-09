from pathlib import Path
from typing import List, Iterator

from kubedeployer.vault.client import VaultClient


class VaultService:
    DELIMITER = "/"
    WILDCARD = "*"

    def __init__(self, client: VaultClient):
        self._client = client

    def read_secret(self, path: str):
        result = self._client.read_secret(path)
        return result.get('data', {}).get('data')

    def list_secrets(self, path: str) -> List[str]:
        """
        Returns full paths to secrets

        Example:

            secret/
                common/
                    production/
                        default
                        alpha/
                            default
                            system
                        gamma/
                            default
                            system

            >>> service = VaultService(client=VaultClient())
            >>> service.list_secrets("secret/common/production/default")
            ['secret/common/production/default']

            >>> service.list_secrets("secret/common/*/*/default")
            ['secret/common/production/alpha/default',
             'secret/common/production/gamma/default']

            >>> service.list_secrets("secret/common/production/*/*")
            ['secret/common/production/alpha/default',
             'secret/common/production/alpha/system',
             'secret/common/production/gamma/default',
             'secret/common/production/gamma/system']
        """

        if path.startswith(self.WILDCARD):
            return []

        path = path.rstrip(self.DELIMITER)
        if self.DELIMITER not in path:
            return []

        path, secret = path.rsplit(self.DELIMITER, maxsplit=1)

        paths = self.get_paths(path)
        return [
            str(Path(p) / i)
            for p in paths
            for i in self.__get_items(p)
            if self.is_secret(i) and secret in (i, self.WILDCARD)
        ]

    @classmethod
    def is_path(cls, path: str) -> bool:
        return path.endswith(cls.DELIMITER)

    @classmethod
    def is_secret(cls, path: str) -> bool:
        return not cls.is_path(path)

    def get_paths(self, path: str) -> Iterator:
        path = path.rstrip(self.DELIMITER)
        if path and self.WILDCARD in path:
            location, path = path.split(self.WILDCARD, maxsplit=1)
            path = path.lstrip(self.DELIMITER)

            paths = [i for i in self.__get_items(location) if self.is_path(i)]
            for p in paths:
                if self.is_path(p):
                    yield from self.get_paths(str(Path(location) / p / path))
        if path:
            yield path

    def __get_items(self, path: str) -> List[str]:
        path = path.rstrip(self.DELIMITER)
        result = self._client.list_secrets(path)
        return result.get("data", {}).get("keys") or []
