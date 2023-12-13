import subprocess

from kubedeployer.manifests import Manifest, ROLLOUT_RESOURCES, \
    InvalidRolloutResource
from kubedeployer.types import PathLike
from kubedeployer.gitlab_ci.environment_variables import settings


DEFAULT_CONTEXT = "kubedeployer-context"
DEFAULT_NAMESPACE = "default"


class KubectlError(Exception):
    pass


def configure(
        server: str,
        token: str,
        namespace: str,
        context: str = DEFAULT_CONTEXT
):
    """Configure connection to cluster"""
    set_cluster = (
        f"kubectl config set-cluster cluster"
        f" --server={server}"
        f" --insecure-skip-tls-verify=true"
    )
    set_credentials = f"kubectl config set-credentials admin --token={token}"
    set_context = (
        f"kubectl config set-context {context}"
        f" --cluster=cluster"
        f" --user=admin"
        f" --namespace={namespace}"
    )
    use_context = f"kubectl config use-context {context}"

    cmd = " && ".join([set_cluster, set_credentials, set_context, use_context])
    result = subprocess.run(cmd, capture_output=True, shell=True)
    if result.returncode != 0:
        raise KubectlError(result.stderr.decode("utf-8"))


def apply_manifests(*paths: PathLike, dry_run: bool = False) -> str:
    """
    Apply manifests

    Option `dry_run` allow printing objects that would be sent,
    without sending it.

    Example:

        >>> apply_manifests("/proj/deployment.yaml", "/proj/svc.yaml")
    """
    if not paths:
        raise KubectlError("manifests not found")

    cmd = (
        f"kubectl apply"
        f" --v={settings.kube_verbosity.value}"
        f" --dry-run={dry_run and 'client' or 'none'}"
        f" {' '.join(f'-f {str(p)}' for p in paths)}"
    )
    result = subprocess.run(cmd, capture_output=True, shell=True)
    if result.returncode != 0:
        raise KubectlError(result.stderr.decode("utf-8"))
    return result.stdout.decode("utf-8")


def check_rollout_status(manifest: Manifest) -> str:
    """
    Return rollout status

    Checking status supporting only for types: DaemonSet, Deployment, StatefulSet
    (https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#rollout).

    Example:

        >>> check_rollout_status(manifest)
    """
    if manifest.kind not in ROLLOUT_RESOURCES:
        raise InvalidRolloutResource(
            f"{manifest.kind} not in ({', '.join(ROLLOUT_RESOURCES)})"
        )

    manifest_namespace = (
            manifest.namespace
            or settings.kube_namespace.value
            or DEFAULT_NAMESPACE
    )

    cmd = (
        f"kubectl rollout"
        f" --v={settings.kube_verbosity.value}"
        f" status {manifest.kind.lower()}/{manifest.name}"
        f" --namespace={manifest_namespace}"
    )
    result = subprocess.run(cmd, capture_output=True, shell=True)
    if result.returncode != 0:
        raise KubectlError(result.stderr.decode("utf-8"))
    return result.stdout.decode("utf-8")


def diff_manifests(manifests_dir: PathLike):
    """
    Diff manifests

    Example:

        >>> diff_manifests("/proj/manifests/")
    """
    if not manifests_dir:
        raise KubectlError("manifests directory not found")

    cmd = (
        f"kubectl diff"
        f" --v={settings.kube_verbosity.value}"
        f" -f {manifests_dir}"
    )
    result = subprocess.run(cmd, capture_output=True, shell=True)
    if result.returncode != 1:
        error = (
            f"return code == "
            f"{result.returncode}, "
            f"{result.stderr.decode('utf-8')}"
        )
        raise KubectlError(error)
    return result.stdout.decode("utf-8")
