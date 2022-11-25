from typing import List, Dict

import pydantic


class KubeSecurityContent(pydantic.BaseModel):
    __root__: List["KubeObject"]

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]

    def __len__(self):
        return len(self.__root__)


ScoringLevel = str


class ScoringRecord(pydantic.BaseModel):
    id: str
    selector: str
    reason: str


class KubeObject(pydantic.BaseModel):
    object: str
    scoring: Dict[ScoringLevel, List[ScoringRecord]]


KubeSecurityContent.update_forward_refs()
KubeObject.update_forward_refs()
