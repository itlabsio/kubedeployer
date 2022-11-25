from kubedeployer.gitlab_ci.environment_variables import settings
from kubedeployer.vault.client import HVACClient
from kubedeployer.vault.service import VaultService


class VaultServiceFactory:
    @classmethod
    def create_vault_service(cls):
        client = HVACClient(
            url=settings.vault_url.value,
            mount_point="secret",
            role_id=settings.vault_approle_id.value,
            secret_id=settings.vault_approle_secret_id.value
        )

        return VaultService(client)
