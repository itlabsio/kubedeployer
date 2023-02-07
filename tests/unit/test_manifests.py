import pytest

from kubedeployer.manifests import get_images, get_manifests


@pytest.fixture
def content(data_path) -> str:
    with open(data_path / "manifests/manifests.yaml", "r") as f:
        yield f.read()


def test_get_images(content):
    images = list(get_images(content))
    assert len(images) == 6

    unique_images = set(images)
    assert unique_images == {
        "registry.local/application:latest",
        "nginx:1.15",
    }


def test_get_images_by_pattern(content):
    retrieved = set(get_images(content, pattern=r"registry\.local"))
    assert retrieved == {"registry.local/application:latest"}


def test_get_unique_images(content):
    retrieved = list(get_images(content, unique=True))
    assert retrieved == [
        "registry.local/application:latest",
        "nginx:1.15"
    ]


def test_get_unique_images_by_pattern(content):
    retrieved = list(get_images(
        content, pattern=r"registry\.local", unique=True
    ))
    assert retrieved == ["registry.local/application:latest"]


def test_get_manifests(content):
    manifests = list(get_manifests(content))
    assert len(manifests) == 5


def test_get_manifests_by_kind(content):
    manifests = list(get_manifests(content, kind="Deployment|CronJob"))
    assert len(manifests) == 3

    unique_names = {m.name for m in manifests}
    assert unique_names == {
        "application",
        "application-worker",
        "application-sync",
    }
