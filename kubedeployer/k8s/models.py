from dataclasses import dataclass
from typing import Dict, Optional, List

from kubernetes import client
from kubernetes.client import V1ObjectMeta, V1PodTemplateSpec

from kubedeployer.k8s.deserialize import deserialize_dict_to_kubeobj


@dataclass
class K8sObject:
    _object_as_dict: dict
    _metadata: V1ObjectMeta
    _kind: str

    def __init__(self, object_as_dict: dict):
        self._kube_api = client.ApiClient()
        self._object_as_dict = object_as_dict

    @property
    def object_as_dict(self) -> dict:
        return self._object_as_dict

    @property
    def kind(self) -> str:
        return self.object_as_dict.get('kind')

    @property
    def pod_template_containing_objects(self) -> List[str]:
        return [
            'Deployment',
            'ReplicaSet',
            'StatefulSet',
            'DaemonSet',
            'Job',
            'CronJob',
            'ReplicationController',
        ]

    @property
    def pod_template_object(self) -> Optional[V1PodTemplateSpec]:
        if self.kind in self.pod_template_containing_objects:
            if self.kind == 'CronJob':
                spec_dict = self.object_as_dict.get('spec', {}).get('jobTemplate', {}).get('spec', {})
            else:
                spec_dict = self.object_as_dict.get('spec', {})
            pod_template_dict = spec_dict.get('template')
        else:
            pod_template_dict = {}
        return deserialize_dict_to_kubeobj(pod_template_dict, V1PodTemplateSpec) if pod_template_dict else None

    @pod_template_object.setter
    def pod_template_object(self, pod_template: V1PodTemplateSpec):
        if self.kind in self.pod_template_containing_objects:
            pod_template_dict = self._kube_api.sanitize_for_serialization(pod_template)
            if self.kind == 'CronJob':
                spec_dict = self.object_as_dict.get('spec', {}).get('jobTemplate', {}).get('spec', {})
            else:
                spec_dict = self.object_as_dict.get('spec', {})
            spec_dict['template'] = pod_template_dict

    @property
    def metadata(self) -> V1ObjectMeta:
        metadata_dict = self.object_as_dict.get('metadata')
        return deserialize_dict_to_kubeobj(metadata_dict, V1ObjectMeta)

    @metadata.setter
    def metadata(self, metadata: V1ObjectMeta):
        metadata_dict = self._kube_api.sanitize_for_serialization(metadata)
        self._object_as_dict['metadata'] = metadata_dict

    def add_annotations(self, annotations: Dict[str, str]):
        metadata = self.metadata if self.metadata else V1ObjectMeta()
        obj_annotations = metadata.annotations if metadata.annotations else {}
        obj_annotations.update(annotations)
        metadata.annotations = obj_annotations
        self.metadata = metadata
        if self.pod_template_object:
            metadata = self.pod_template_object.metadata if self.pod_template_object.metadata else V1ObjectMeta()
            pod_annotations = metadata.annotations if metadata.annotations else {}
            pod_annotations.update(annotations)
            metadata.annotations = pod_annotations
            self.pod_template_object.metadata = metadata
