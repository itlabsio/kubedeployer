import subprocess

import pytest

from kubedeployer.files import get_files, YAML_EXTENSIONS
from kubedeployer.kustomize import KustomizationError, \
    get_kustomization, create_kustomization, add_annotations, build_manifests


def is_kustomize_not_found() -> bool:
    cmd = "kustomize help"
    result = subprocess.run(cmd, shell=True)
    return result.returncode != 0


def test_get_kustomization_file(data_path):
    path = data_path / "manifests/apps/kustomize-app/overlays/stage"

    filename = str(get_kustomization(path))
    assert "kustomize-app/overlays/stage/kustomization.yaml" in filename


def test_get_kustomization_file_in_multiple_locations(data_path):
    paths = (
        data_path / "manifests/apps/kustomize-app",
        data_path / "manifests/apps/kustomize-app/overlays/stage",
    )

    filename = str(get_kustomization(*paths))
    assert "kustomize-app/overlays/stage/kustomization.yaml" in filename


def test_raises_to_many_kustomization_files(data_path):
    with pytest.raises(KustomizationError, match="There are to many files"):
        get_kustomization(data_path / "manifests/apps/kustomize-app/**/")


@pytest.mark.skipif(is_kustomize_not_found(), reason="kustomize not found")
def test_create_kustomization_file(tmp_path, data_path):
    manifests_path = data_path / "manifests/apps/env-app/**"
    manifests_files = get_files(manifests_path, extensions=YAML_EXTENSIONS)

    kustomization = create_kustomization(tmp_path, *manifests_files)
    assert tmp_path / "kustomization.yaml" == kustomization

    with open(kustomization, "r") as f:
        content = f.read()

        assert "resources:" in content
        assert "data/manifests/apps/env-app/manifest.yaml" in content
        assert "data/manifests/apps/env-app/production/ingress.yaml" in content


@pytest.mark.skipif(is_kustomize_not_found(), reason="kustomize not found")
def test_add_annotations_into_kustomization_file(tmp_path):
    kustomization = create_kustomization(tmp_path)

    annotations = {
        "commit-ref": "a228d15c7",
        "commit-branch": "development",
        "digit-annotation": "123",

        "empty-annotation": None,
        "empty-string-annotation": "",
    }
    add_annotations(kustomization.parent, annotations)

    with open(kustomization, "r") as f:
        content = f.read()
        assert "commonAnnotations:" in content

        assert "commit-ref: a228d15c7" in content
        assert "commit-branch: development" in content
        assert "digit-annotation: \"123\"" in content

        assert "empty-annotation: \"\"" in content
        assert "empty-string-annotation: \"\"" in content


@pytest.mark.skipif(is_kustomize_not_found(), reason="kustomize not found")
def test_raises_on_add_empty_annotations_into_kustomization_file(tmp_path):
    kustomization = create_kustomization(tmp_path)

    with pytest.raises(KustomizationError, match="must specify annotation"):
        add_annotations(kustomization.parent, annotations={})


@pytest.mark.skipif(is_kustomize_not_found(), reason="kustomize not found")
def test_build_manifests_by_kustomization_file(tmp_path, data_path):
    path = data_path / "manifests/apps/kustomize-app/overlays/stage"

    build_manifests(path, tmp_path / "manifests.yaml")

    with open(tmp_path / "manifests.yaml", "r") as f:
        content = f.read()

        assert "kind: Deployment" in content
        assert "kind: Service" in content
        assert "kind: ConfigMap" in content
