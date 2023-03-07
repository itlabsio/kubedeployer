import hvac

from kubedeployer.gitlab_ci.environment_variables import settings
from kubedeployer.vault.client import HVACClient
from kubedeployer.vault.service import VaultService


class HVACClientFactory:
    @classmethod
    def create_hvac_client(cls) -> HVACClient:
        hvac_client = hvac.Client(url=settings.vault_url.value)
        role_id = settings.vault_approle_id.value
        secret_id = settings.vault_approle_secret_id.value
        response = hvac_client.auth_approle(role_id, secret_id)
        token = response["auth"]["client_token"]
        hvac_client.token = token
        return HVACClient(hvac_client=hvac_client, mount_point="secret")


class VaultServiceFactory:
    @classmethod
    def create_vault_service(cls):
        client = HVACClientFactory.create_hvac_client()
        return VaultService(client)
