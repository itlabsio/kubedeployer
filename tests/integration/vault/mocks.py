import hvac

from kubedeployer.vault.client import HvacClient


class HvacClientFactoryMocker:
    @staticmethod
    def mock_create_hvac_client(mocker, hvac_client: hvac.Client, mount_point='secret'):
        client = HvacClient(hvac_client=hvac_client, mount_point=mount_point)
        mocker.patch('kubedeployer.vault.factory.HvacClientFactory.create_hvac_client', return_value=client)
