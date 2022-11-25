import subprocess
from typing import Optional, Dict, Tuple
from pathlib import Path

from kubedeployer.files import get_files, YAML_EXTENSIONS
from kubedeployer.types import PathLike


KUSTOMIZATION_FILENAME = "kustomization"


class KustomizationError(Exception):
    pass


def get_kustomization(*paths: PathLike) -> Optional[Path]:
    """
    Searching kustomization.yaml by selected paths

    For recursion searching use `**` template in path.

    KustomizationError would by rising if was finded more than one
    kustomization.yaml.

    Example:

        >>> get_kustomization("/project", "/project/overlays/**")
    """

    extensions = YAML_EXTENSIONS.replace("*", KUSTOMIZATION_FILENAME)
    files = set(get_files(*paths, extensions=extensions))
    if len(files) > 1:
        raise KustomizationError(
            f"There are to many files:"
            f" {', '.join(str(f) for f in files)}"
        )
    return files.pop() if files else None


def create_kustomization(path: PathLike, *resources: PathLike) -> Path:
    """
    Create kustomization.yaml by selected path

    Example:

        >>> create_kustomization("/proj", "/proj/svc.yaml", "/proj/cm.yaml")
    """
    cmd = (
        f"(mkdir -p {str(path)}"
        f" && cd {str(path)}"
        f" && kustomize create"
        f" --resources={','.join(str(r) for r in resources)})"
    )
    result = subprocess.run(cmd, capture_output=True, shell=True)
    if result.returncode != 0:
        raise KustomizationError(result.stderr.decode("utf-8"))
    return get_kustomization(path)


def add_annotations(path: PathLike, annotations: Dict[str, str]):
    """
    Add annotations into kustomization.yaml

    Example:

        >>> add_annotations("/proj", {"environment": "stage"})
    """

    def convert(key: str, value: str) -> Tuple[str, str]:
        return key, value or ""

    cmd = (
        f"(cd {str(path)}"
        f" && kustomize edit set annotation"
        f" {' '.join(':'.join(convert(*i)) for i in annotations.items())})"
    )
    result = subprocess.run(cmd, capture_output=True, shell=True)
    if result.returncode != 0:
        raise KustomizationError(result.stderr.decode("utf-8"))


def build_manifests(path: PathLike, output: PathLike):
    """
    Collect all manifests into single file using kustomization.yaml

    Example:

        >>> build_manifests("/proj", "/tmp/manifests.yaml")
    """
    cmd = f"(cd {str(path)} && kustomize build . > {str(output)})"
    result = subprocess.run(cmd, capture_output=True, shell=True)
    if result.returncode != 0:
        raise KustomizationError(result.stderr.decode("utf-8"))
