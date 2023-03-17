import pytest

from kubedeployer import kubectl
from kubedeployer.gitlab_ci.environment_variables import settings


@pytest.fixture(autouse=True, scope="module")
def kube_context():
    kubectl.configure(
        server=settings.kube_url.value,
        token=settings.kube_token.value,
        namespace="default",
        context="default-context",
    )
