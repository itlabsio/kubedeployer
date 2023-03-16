from functools import partial
from typing import Callable

from kubedeployer.console.wrap import colorize, Color, timestamp, success, TAB, indent
from kubedeployer.console.wrap import error as error_colorize
from kubedeployer.console.wrap import warning as warning_colorize

write = partial(print, end="", flush=True)
writeln = partial(write, end="\n")

info: Callable[[str, str], str] = lambda text, prefix: writeln(indent(text, prefix))

# Formatting output of the stage (ex, Applying changes..)
stage: Callable[[str], str] = lambda text: writeln(f"\n{success(timestamp(text))}\n")


def error(text: str, prefix: str = TAB):
    writeln(indent(error_colorize(text), prefix=prefix))


def warning(text: str, prefix: str = TAB):
    writeln(indent(warning_colorize(text), prefix=prefix))
