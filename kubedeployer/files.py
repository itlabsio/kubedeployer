import glob
from itertools import product
from pathlib import Path
from typing import Iterator

from kubedeployer.types import PathLike


EXTENSION_DELIMITER = "|"

YAML_EXTENSIONS = "*.yml|*.yaml"
YAML_DEFAULT_EXTENSION = "*.yaml"


def get_files(*paths: PathLike, extensions: str = "*") -> Iterator[Path]:
    """
    Returns files from paths matching extensions

    Example:

        >>> get_files("/dir", "/dir/sub/dir/**", extensions="*.yaml|*.json")
        /dir/example.yaml
        /dir/sub/dir/location/example.json
    """

    for path, ext in product(paths, extensions.split(EXTENSION_DELIMITER)):
        pathname = str(Path(path) / ext)
        recursive = "**" in pathname
        for f in glob.iglob(pathname, recursive=recursive):
            yield Path(f)
