# -*- coding: utf-8 -*-
from backend.resources.client import K8SClient

from . import utils


class Namespace(K8SClient):
    def get_namespace(self, name):
        # 假定cc中有，集群中也存在
        cc_namespaces = utils.get_namespaces_by_cluster_id(self.access_token, self.project_id, self.cluster_id)
        if not cc_namespaces:
            return {}

        for ns in cc_namespaces:
            if ns["name"] == name:
                return {"name": name, "namespace_id": ns["id"]}
        return {}

    def _create_namespace(self, name):
        return self.client.create_namespace({"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": name}})

    def create_namespace(self, creator, name):
        # TODO 补充imagepullsecrets和命名空间变量的创建?
        # TODO 操作审计
        self._create_namespace(name)
        ns = utils.create_cc_namespace(self.access_token, self.project_id, self.cluster_id, name, creator)
        return {"name": name, "namespace_id": ns["id"]}
