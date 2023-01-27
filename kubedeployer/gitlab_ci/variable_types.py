from dataclasses import dataclass
from typing import Union, Optional

from kubedeployer.utils.convert import str_to_bool


@dataclass
class BaseVariable:
    name: str
    value: Union[str, int, bool, None]

    def __repr__(self):
        return self.value

    def to_str(self) -> 'StrVariable':
        if self.value is not None:
            value = str(self.value)
        else:
            value = self.value
        return StrVariable(name=self.name, value=value)

    def to_int(self) -> 'IntVariable':
        if self.value is not None:
            value = int(self.value)
        else:
            value = self.value
        return IntVariable(name=self.name, value=value)

    def to_bool(self) -> 'BoolVariable':
        if isinstance(self.value, str):
            value = bool(str_to_bool(self.value))
        elif isinstance(self.value, int):
            value = bool(self.value)
        else:
            value = self.value
        return BoolVariable(name=self.name, value=value)


@dataclass
class StrVariable(BaseVariable):
    value: Optional[str]


@dataclass
class BoolVariable(BaseVariable):
    value: Optional[bool]


@dataclass
class IntVariable(BaseVariable):
    value: Optional[int]
