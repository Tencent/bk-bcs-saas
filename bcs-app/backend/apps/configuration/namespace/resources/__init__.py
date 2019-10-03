# -*- coding: utf-8 -*-
from . import k8s, mesos
from backend.apps.constants import ProjectKind


class Namespace:

    def __init__(self, access_token, project_id, project_kind, cluster_id):
        self.access_token = access_token
        self.project_id = project_id
        self.cluster_id = cluster_id
        self.client = k8s if project_kind == ProjectKind.K8S.value else mesos

    def delete(self, ns_name):
        return self.client.Namespace.delete(self.access_token, self.project_id, self.cluster_id, ns_name)