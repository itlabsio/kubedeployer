from datetime import datetime
from enum import Enum
from functools import partial
from typing import Callable, Optional
from textwrap import indent as indent_wrapper

TAB = " " * 4


class Color(Enum):
    RED = "\033[0;31;40m"
    GREEN = "\033[0;32;40m"
    YELLOW = "\033[0;93;40m"
    NO_COLOR = "\033[0m"


class Wrapper:
    ts_fmt = "%d.%m.%Y %H:%M:%S"

    def __init__(self,
                 prefix: str = "",
                 color: Color = Color.NO_COLOR,
                 ts: Optional[Callable[..., datetime]] = None):
        self.prefix = prefix
        self.color = color
        self.ts = ts

    def wrap(self, text: str) -> str:
        return indent_wrapper(
            f"{self.color.value if self.color != Color.NO_COLOR else ''}"
            f"{self.ts().strftime(self.ts_fmt) + ': ' if self.ts else ''}"
            f"{text}"
            f"{Color.NO_COLOR.value if self.color != Color.NO_COLOR else ''}",
            prefix=self.prefix
        )


def colorize(text: str, color: Color) -> str:
    return Wrapper(color=color).wrap(text)


def indent(text: str, prefix: str = "") -> str:
    return Wrapper(prefix=prefix).wrap(text)


def timestamp(text: str, ts: Callable[..., datetime] = datetime.now) -> str:
    return Wrapper(ts=ts).wrap(text)


success = partial(colorize, color=Color.GREEN)
warning = partial(colorize, color=Color.YELLOW)
error = partial(colorize, color=Color.RED)
