import hvac

from kubedeployer.vault.client import HVACClient


class HVACClientFactoryMocker:
    @staticmethod
    def mock_create_hvac_client(mocker, hvac_client: hvac.Client, mount_point='secret'):
        client = HVACClient(hvac_client=hvac_client, mount_point=mount_point)
        mocker.patch('kubedeployer.vault.factory.HVACClientFactory.create_hvac_client', return_value=client)
