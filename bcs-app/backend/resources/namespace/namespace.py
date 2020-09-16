# -*- coding: utf-8 -*-
from backend.resources.permissions import get_res_policy_data
from backend.resources.client import K8SClient
from backend.utils.error_codes import error_codes
from .permissions import get_namespace_policy_list, POLICY_CODE_LIST
from . import utils


def _add_permissions_fields(namespaces, ns_policy_data, policy_code_list):
    for ns in namespaces:
        permissions = {p_code: False for p_code in policy_code_list}
        # ns_policy_data like {('namespace', 'view'): ['namespaceA', 'namespaceB']}
        for res_policy_key in ns_policy_data:
            if str(ns["id"]) in ns_policy_data[res_policy_key]:
                p_code = res_policy_key[1]
                permissions[p_code] = True
        ns["permissions"] = permissions


def get_namespaces_by_cluster_id(user, project_id, cluster_id, policy_code_list=None):
    namespaces = utils.get_namespaces_by_cluster_id(user.access_token, project_id, cluster_id)
    if not namespaces:
        return []

    policy_code_list = policy_code_list or POLICY_CODE_LIST
    ns_policy_data = get_res_policy_data(user, project_id, get_namespace_policy_list(policy_code_list))
    if not ns_policy_data:
        raise error_codes.IAMCheckFailed(
            f"{user.username} have no permissions for namespaces in cluster_id {cluster_id}"
        )

    _add_permissions_fields(namespaces, ns_policy_data, policy_code_list)
    return namespaces


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
