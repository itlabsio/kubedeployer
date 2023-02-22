import ujson
from kubernetes import client


class WrappedObj:
    def __init__(self, data):
        self.data = data


def deserialize_dict_to_kubeobj(d: dict, kubeobjclass):
    kube_api = client.ApiClient()
    wrapped_obj = WrappedObj(data=ujson.dumps(d))
    return kube_api.deserialize(wrapped_obj, kubeobjclass)
