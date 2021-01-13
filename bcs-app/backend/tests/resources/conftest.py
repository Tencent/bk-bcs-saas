# -*- coding: utf-8 -*-
import uuid
from kubernetes import client

from backend.tests.conftest import TESTING_API_SERVER_URL


class FakeBcsKubeConfigurationService:
    """Fake configuration service which return local apiserver as config"""

    def __init__(self, *args, **kwargs):
        pass

    def make_configuration(self):
        configuration = client.Configuration()
        configuration.verify_ssl = False
        configuration.host = TESTING_API_SERVER_URL
        return configuration


def construct_deployment(name, replicas=1):
    """Construct a fake deployment body"""
    return client.V1beta2Deployment(
        api_version='extensions/v1beta1',
        kind='Deployment',
        metadata=client.V1ObjectMeta(name=name),
        spec=client.V1beta2DeploymentSpec(
            selector=client.V1LabelSelector(match_labels={'deployment-name': name}),
            template=client.V1PodTemplateSpec(
                spec=client.V1PodSpec(
                    containers=[client.V1Container(image="busybox", name="main", command=["sleep", "3600"])]
                ),
                metadata=client.V1ObjectMeta(labels={"deployment-name": name}, name=name),
            ),
            replicas=replicas,
        ),
    )


def construct_replica_set(name, owner_deployment=None):
    """Construct a fake ReplicaSet body"""
    if owner_deployment:
        owner_references = [
            client.V1OwnerReference(
                api_version=owner_deployment.api_version,
                uid=uuid.uuid4().hex,
                name=owner_deployment.metadata.name,
                kind='Deployment',
            )
        ]
        match_labels = owner_deployment.spec.selector.match_labels
    else:
        owner_references = []
        match_labels = {'rs-name': name}

    return client.V1ReplicaSet(
        api_version='extensions/v1beta1',
        kind='ReplicaSet',
        metadata=client.V1ObjectMeta(
            name=name,
            # Set owner reference to deployment
            owner_references=owner_references,
        ),
        spec=client.V1ReplicaSetSpec(
            replicas=1,
            selector=client.V1LabelSelector(match_labels=match_labels),
            template=client.V1PodTemplateSpec(
                spec=client.V1PodSpec(
                    containers=[client.V1Container(image="busybox", name="main", command=["sleep", "3600"])]
                ),
                metadata=client.V1ObjectMeta(labels=match_labels, name=name),
            ),
        ),
    )


def construct_pod(name, labels=None, owner_replicaset=None):
    """Construct a fake Pod body"""
    if owner_replicaset:
        owner_references = [
            client.V1OwnerReference(
                api_version=owner_replicaset.api_version,
                uid=uuid.uuid4().hex,
                name=owner_replicaset.metadata.name,
                kind='ReplicaSet',
            )
        ]
        labels = owner_replicaset.spec.selector.match_labels
    else:
        owner_references = []

    return client.V1Pod(
        api_version='v1',
        kind='Pod',
        metadata=client.V1ObjectMeta(name=name, labels=labels, owner_references=owner_references),
        spec=client.V1PodSpec(containers=[client.V1Container(name="main", image="busybox")]),
    )
