import pytest

from kubedeployer.files import get_files


@pytest.fixture(autouse=True)
def application_directory(tmp_path):
    files = (
        tmp_path / "base/namespace.yml",
        tmp_path / "base/README.md",
        tmp_path / "base/versions/VERSIONS.txt",
        tmp_path / "base/versions/v1.0.0/deployment.yaml",
        tmp_path / "base/versions/v1.0.0/service.yaml"
    )
    for filename in files:
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w") as f:
            f.write("")
    yield


def test_get_files(tmp_path):
    retrieved_files = set(
        get_files(
            tmp_path / "base", tmp_path / "base/versions/**",
            extensions="*.yml|*.yaml|*.txt"
        )
    )
    assert retrieved_files == {
        tmp_path / "base/namespace.yml",
        tmp_path / "base/versions/VERSIONS.txt",
        tmp_path / "base/versions/v1.0.0/deployment.yaml",
        tmp_path / "base/versions/v1.0.0/service.yaml",
    }
