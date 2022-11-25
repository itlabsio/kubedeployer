import re
from typing import Iterable, Tuple, Optional, Any

import yaml


WORKLOAD_RESOURCES = (
    "CronJob",
    "DaemonSet",
    "Deployment",
    "Job",
    "ReplicaSet",
    "ReplicationController",
    "StatefulSet",
)

ROLLOUT_RESOURCES = (
    "DaemonSet",
    "Deployment",
    "StatefulSet",
)


class ManifestError(Exception):
    pass


class InvalidRolloutResource(ManifestError):
    pass


class Manifest(dict):

    @property
    def kind(self) -> str:
        return self.get_item("kind")

    @property
    def name(self) -> str:
        return self.get_item("metadata.name")

    @property
    def namespace(self) -> Optional[str]:
        return self.get_item("metadata.namespace")

    def get_item(self, path: str) -> Optional[Any]:

        def get(obj: dict, location: str) -> Optional[Any]:
            if obj and "." in location:
                item, loc = location.split(".", maxsplit=1)
                return get(obj.get(item), loc)
            return obj and obj.get(location) or None

        return get(self, path)


def get_manifests(content: str, kind=r".+") -> Iterable[Manifest]:
    """
    Returns manifests from yaml file

    Structure of the manifest contains next attributes: apiVersion, kind, spec.

    Example:

        # Returns all manifests
        >>> manifests = list(get_manifests(content))

        # Returns only manifests with kind `Deployment` or 'Service`
        >>> manifests = list(get_manifests(content, kind="Deployment|Service"))
    """

    def validate(obj: dict) -> bool:
        return obj \
               and obj.get("apiVersion") \
               and obj.get("kind") \
               and obj.get("spec")

    for manifest in yaml.safe_load_all(content):
        if not (validate(manifest) and re.match(kind, manifest.get("kind"))):
            continue
        yield Manifest(manifest)


def get_images(content: str, pattern: str = r".+", unique: bool = False) -> \
        Iterable[str]:
    """
    Returns docker image names from yaml file

    Manifests not owned by WorkloadResources will be ignored
    (https://kubernetes.io/docs/concepts/workloads/).

    Example:

        # Returns all images
        >>> get_images(content)

        # Returns only images that match by template
        >>> get_images(content, r".*:latest")
    """

    def get_containers_path(kind: str) -> str:
        if kind == "CronJob":
            return "spec.jobTemplate.spec.template.spec"
        return "spec.template.spec"

    def get_containers(obj: Manifest, path: str) -> Iterable[Tuple[str, str]]:
        containers = obj.get_item(path) or []
        for container in containers:
            yield container["name"], container["image"]

    unique_images = set()

    for manifest in get_manifests(content, kind="|".join(WORKLOAD_RESOURCES)):
        path = get_containers_path(manifest.kind)

        for _, image in get_containers(manifest, f"{path}.initContainers"):
            if re.match(pattern, image) and image not in unique_images:
                unique and unique_images.add(image)
                yield image

        for _, image in get_containers(manifest, f"{path}.containers"):
            if re.match(pattern, image) and image not in unique_images:
                unique and unique_images.add(image)
                yield image
