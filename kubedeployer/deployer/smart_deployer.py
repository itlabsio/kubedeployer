from pathlib import Path
from typing import List, Tuple

from kubedeployer import console, k8s
from kubedeployer import kustomize
from kubedeployer.deployer.abstract_deployer import AbstractDeployer
from kubedeployer.files import YAML_EXTENSIONS, get_files
from kubedeployer.gitlab_ci.environment_variables import settings
from kubedeployer.text import envsubst
from kubedeployer.types import PathLike


def get_manifests_paths(manifests_path: Path) -> List[PathLike]:
    if not manifests_path.exists():
        raise FileExistsError(f"Manifest folder {manifests_path} doesn't exist")

    paths = [manifests_path]

    if settings.environment.value:
        overlay_path = manifests_path / f"{settings.environment.value}"
        if overlay_path.exists():
            paths.append(overlay_path / "**")
    return paths


def get_manifest_files_by_paths(manifests_paths: List[PathLike]) -> List[PathLike]:
    manifests_files = list(
        get_files(*manifests_paths, extensions=YAML_EXTENSIONS)
    )

    if not manifests_files:
        raise FileExistsError(
            f"Manifests files not found in "
            f"{', '.join(str(p) for p in manifests_paths)}"
        )

    console.info("Kustomization not found, creating..", console.TAB)

    for file in manifests_files:
        content = envsubst(file.read_text())
        file.write_text(content)
    return manifests_files


def build_manifests_content(kustomization: Path, is_generated: bool, manifests_filename: Path) -> str:
    console.stage("Configure kustomization..")
    annotations = k8s.get_annotations()
    kustomize.add_annotations(kustomization.parent, annotations=annotations)

    console.info("Append next annotations:", console.TAB)
    console.info("\n".join(f"{k}: {v or ''}" for k, v in annotations.items()), console.TAB * 2)

    console.stage("Building manifests..")
    kustomize.build_manifests(kustomization.parent, manifests_filename)

    if is_generated:
        manifests_content = manifests_filename.read_text()
    else:
        manifests_content = envsubst(manifests_filename.read_text())
        manifests_filename.write_text(manifests_content)
    return manifests_content


class SmartDeployer(AbstractDeployer):

    @staticmethod
    def deploy(tmp_path: Path, manifests_path: Path) -> Tuple[str, Path]:
        manifests_paths = get_manifests_paths(manifests_path)

        console.stage("Searching kustomization..")
        is_generated = False
        kustomization = kustomize.get_kustomization(*manifests_paths)
        if not kustomization:
            manifests_files = get_manifest_files_by_paths(manifests_paths)
            kustomization = kustomize.create_kustomization(manifests_path, *manifests_files)
            is_generated = True
            console.info("Append next resources into kustomization:", console.TAB)
            console.info("\n".join(f"-{str(f)}" for f in manifests_files), console.TAB * 2)
        console.info(f"Kustomization location {str(kustomization)}", console.TAB)
        manifests_filename = tmp_path / "manifests.yaml"
        content = build_manifests_content(
            kustomization=kustomization,
            is_generated=is_generated,
            manifests_filename=manifests_filename
        )
        return content, manifests_filename
