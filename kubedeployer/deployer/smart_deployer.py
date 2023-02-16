from pathlib import Path
from typing import List, Tuple

from kubedeployer import console, k8s
from kubedeployer.deployer.abstract_deployer import AbstractDeployer
from kubedeployer.files import YAML_EXTENSIONS, get_files
from kubedeployer.gitlab_ci.environment_variables import settings
from kubedeployer import kustomize
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


class SmartDeployer(AbstractDeployer):
    @staticmethod
    def deploy(tmp_path: Path, manifests_path: Path) -> Tuple[str, Path]:
        manifests_paths = get_manifests_paths(manifests_path)

        console.stage("Searching kustomization..")
        kustomization = kustomize.get_kustomization(*manifests_paths)
        if not kustomization:
            manifests_files = list(
                get_files(*manifests_paths, extensions=YAML_EXTENSIONS)
            )

            if not manifests_files:
                raise FileExistsError(
                    f"Manifests files not found in "
                    f"{', '.join(str(p) for p in manifests_paths)}"
                )

            console.info("Kustomization not found, creating..", console.TAB)

            manifests_files = get_files(
                *manifests_paths, extensions=YAML_EXTENSIONS
            )
            kustomization = kustomize.create_kustomization(manifests_path, *manifests_files)

            console.info("Append next resources into kustomization:", console.TAB)
            console.info("\n".join(f"-{str(f)}" for f in manifests_files), console.TAB * 2)
        console.info(f"Kustomization location {str(kustomization)}", console.TAB)

        console.stage("Configure kustomization..")
        annotations = k8s.get_annotations()
        kustomize.add_annotations(kustomization.parent, annotations=annotations)

        console.info("Append next annotations:", console.TAB)
        console.info("\n".join(f"{k}: {v or ''}" for k, v in annotations.items()), console.TAB * 2)

        console.stage("Building manifests..")
        manifests_filename = tmp_path / "manifests.yaml"
        kustomize.build_manifests(kustomization.parent, manifests_filename)

        manifests_content = envsubst(manifests_filename.read_text())
        manifests_filename.write_text(manifests_content)
        return manifests_content, manifests_filename
