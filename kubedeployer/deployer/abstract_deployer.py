from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Tuple


class AbstractDeployer:
    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def deploy(tmp_path: Path, manifests_path: Path) -> Tuple[str, Path]:
        raise NotImplementedError
