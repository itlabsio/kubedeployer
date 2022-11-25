from pathlib import Path
from typing import TypeVar

import pydantic

PathLike = TypeVar("PathLike", str, Path)


class BaseModel(pydantic.BaseModel):

    class Config:
        allow_population_by_field_name = True
