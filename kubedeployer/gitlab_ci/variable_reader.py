import os
from abc import ABCMeta, abstractmethod
from typing import Optional

from kubedeployer.gitlab_ci.exceptions import GitlabCiBaseException
from kubedeployer.gitlab_ci.variable_types import BaseVariable, BoolVariable, IntVariable, StrVariable


class AbstractVariableReader:
    __metaclass__ = ABCMeta

    @abstractmethod
    def read_str(self, env_name, is_required=False, default_value=None) -> StrVariable:
        raise NotImplementedError

    @abstractmethod
    def read_int(self, env_name, is_required=False, default_value=None) -> IntVariable:
        raise NotImplementedError

    @abstractmethod
    def read_bool(self, env_name, is_required=False, default_value=None) -> BoolVariable:
        raise NotImplementedError


class EnvironmentVariableReader(AbstractVariableReader):
    @staticmethod
    def _read_env(env_name: str, is_required: bool = False, default_value: object = None) -> BaseVariable:
        if env_name in os.environ and os.environ[env_name] != '':
            value = os.getenv(env_name, default_value)
        elif not is_required:
            value = default_value
        else:
            raise GitlabCiBaseException(f'Environment variable "{env_name}" is required')
        return BaseVariable(name=env_name, value=value)

    def read_str(self, env_name: str, is_required: bool = False, default_value: Optional[str] = None) -> StrVariable:
        base_var = self._read_env(env_name, is_required, default_value)
        return base_var.to_str()

    def read_int(self, env_name, is_required=False, default_value: Optional[int] = None) -> IntVariable:
        base_var = self._read_env(env_name, is_required, default_value)
        return base_var.to_int()

    def read_bool(self, env_name, is_required=False, default_value: Optional[bool] = None) -> BoolVariable:
        base_var = self._read_env(env_name, is_required, default_value)
        return base_var.to_bool()
