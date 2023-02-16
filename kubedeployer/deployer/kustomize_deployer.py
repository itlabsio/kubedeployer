from pathlib import Path

from kubedeployer import kustomize, console, k8s
from kubedeployer.deployer.abstract_deployer import AbstractDeployer


class KustomizeDeployer(AbstractDeployer):
    @staticmethod
    def deploy(tmp_path: Path, manifests_path: Path):
        console.stage("Configure kustomization..")
        kustomization = kustomize.get_kustomization(*[manifests_path])
        if not kustomization:
            raise FileExistsError(f"Kustomization file does not exist in manifest folder {manifests_path}")
        annotations = k8s.get_annotations()
        kustomize.add_annotations(kustomization.parent, annotations=annotations)

        console.info("Append next annotations:", console.TAB)
        console.info("\n".join(f"{k}: {v or ''}" for k, v in annotations.items()), console.TAB * 2)

        console.stage("Building manifests..")
        manifests_filename = tmp_path / "manifests.yaml"
        kustomize.build_manifests(kustomization.parent, manifests_filename)

        manifests_content = manifests_filename.read_text()
        manifests_filename.write_text(manifests_content)
        return manifests_content, manifests_filename
