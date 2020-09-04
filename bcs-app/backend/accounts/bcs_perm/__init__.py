# -*- coding: utf-8 -*-
#
# Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
# Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
"""
注: 现阶段只要有项目权限，则拥有所有权限
说明：使用 Namespace的 hook_perms 函数时，需要增加: ns_name_flag 参数

bcs_perm_handler 调用这个函数的地方需要再次确认
"""
import abc

from django.utils.translation import ugettext_lazy as _

from backend.components import paas_cc
from backend.components.enterprise.iam import BKIAMClient
from backend.components.enterprise.iam import get_access_token as get_access_token_by_iam
from backend.utils.error_codes import error_codes, bk_error_codes
from backend.components.enterprise.bk_login import get_all_users

# 与资源无关
NO_RES = "**"
# 任意资源
ANY_RES = "*"
# 用户判断是否集群和命名空间的操作类型的处理
CLUSTER_NAMESPACE_RESOURCE_TYPE = ["cluster", "namespace"]


class PermissionMeta(object):
    """权限元类
    """

    __metaclass__ = abc.ABCMeta

    # 服务类型，常量
    RESOURCE_TYPE = ""
    RES_TYPE_NAME = ""

    # 功能列表
    POLICY_LIST = ["create", "delete", "view", "edit", "use"]

    CMD_NAME = {
        "delete": _("删除"),
        "create": _("创建"),
        "use": _("使用"),
        "edit": _("编辑"),
        "view": _("查看"),
        "list": _("列表"),
    }

    def __init__(self, request, project_id, resource_id, resource_name=None):
        self.access_token = request.user.token.access_token
        self.user_id = request.user.username
        self.project_id = project_id
        self.resource_id = str(resource_id)
        self.resource_name = resource_name
        self.resource_code = str(resource_id)

        self.err_msg = _("请联系管理员添加权限")

        project_code = request.project.english_name
        self.iam_client = BKIAMClient(project_code)
        self.resource_id = self.tansfer_resource_id(resource_id)

    def tansfer_resource_id(self, resource_id):
        """resource_id 需要按照新的格式组装
        """
        # resource_id 需要按照新的格式组装(与资源无关则保持用：**)
        if resource_id != NO_RES:
            resource_id = f"{self.RESOURCE_TYPE}:{resource_id}"
        return resource_id

    def had_perm(self, action_id):
        """判断是否有权限
        """
        # 模板集 和 Metric 都先不做权限限制
        # if self.RESOURCE_TYPE in ['templates', 'metric']:
        #     True
        return True

    def can_create(self, raise_exception):
        """创建权限不做判断
        """
        # 创建权限都默认开放
        return True

    def can_edit(self, raise_exception):
        """是否编辑权限
        """
        return True

    def can_delete(self, raise_exception):
        """是否使用删除
        """
        return True

    def can_view(self, raise_exception):
        return True

    def can_use(self, raise_exception):
        """是否使用权限
        """
        return True

    def get_msg_key(self, cmd):
        return f"{cmd}_msg"

    def get_msg(self, cmd):
        """获取消息
        """
        cmd_name = self.CMD_NAME[cmd]
        if cmd == "create":
            msg = "您没有{res_type_name}的{cmd_name}权限".format(res_type_name=self.RES_TYPE_NAME, cmd_name=cmd_name)
        else:
            if self.resource_name:
                msg_format = _("您没有{}[{}]的{}权限").format(self.RES_TYPE_NAME, self.resource_name, cmd_name)
            else:
                msg_format = _("您没有{}的{}权限").format(self.RES_TYPE_NAME, cmd_name)
            msg = msg_format.format(res_type_name=self.RES_TYPE_NAME, res_name=self.resource_name, cmd_name=cmd_name)
        return msg

    def register(self, resource_id, resource_name):
        """注册资源到权限中心
        """
        resource_id = self.tansfer_resource_id(resource_id)
        ret = self.iam_client.register_res(self.user_id, self.RESOURCE_TYPE, resource_id, resource_name,)
        return ret

    def delete(self):
        """删除资源
        注意: resource_id必须是字符串类型
        """
        ret = self.iam_client.delete_res(self.RESOURCE_TYPE, self.resource_id)
        return ret

    def update_name(self, resource_name, raise_exception=False):
        ret = self.iam_client.update_res(self.RESOURCE_TYPE, self.resource_id, resource_name)
        if ret.get("code") != 0 and raise_exception is True:
            error_message = "%s, %s" % (bk_error_codes.IAMError(_("权限中心更新资源接口调用失败")), ret.get("message", ""))
            raise error_codes.APIError(error_message)
        return ret

    def hook_perms(self, data_list, filter_use=False, id_flag="id"):
        """资源列表，添加permssions dict
        """
        # NOTE: 现阶段有项目权限，那么就有所有权限
        default_perms = {perm: True for perm in self.POLICY_LIST}
        data_list = data_list or []
        for data in data_list:
            data["permissions"] = default_perms
        return data_list

    def get_err_data(self, policy_code):
        """获取返回给前端错误数据，权限申请使用
        """
        if policy_code == "create":
            role = "creator"
        elif policy_code in ["deploy", "download"]:
            role = "manager"
        else:
            role = "bcs_manager"

        data = [
            {
                "resource_type": self.RESOURCE_TYPE,
                "resource_type_name": self.RES_TYPE_NAME,
                "resource_id": self.resource_id,
                "resource_code": self.resource_id,
                "resource_name": self.resource_name,
                "role": role,
                "policy_code": policy_code,
                "policy_name": self.CMD_NAME[policy_code],
            }
        ]

        return data


class Cluster(PermissionMeta):
    """集群权限
    """

    # 资源类型
    RESOURCE_TYPE = "cluster"
    RES_TYPE_NAME = "集群"

    POLICY_LIST = ["create", "edit", "cluster-readonly", "cluster-manager"]

    def __init__(self, request, project_id, resource_id, resource_type=None):
        super(Cluster, self).__init__(request, project_id, resource_id)
        if resource_id != NO_RES:
            cluster = paas_cc.get_cluster(self.access_token, self.project_id, resource_id)
            if cluster.get("code") != 0:
                raise error_codes.ResNotFoundError(cluster.get("message", ""))
            # 通过接口判断资源类型
            self.res = cluster["data"]
            self.resource_name = cluster["data"]["name"]
        else:
            self.res = None

    @classmethod
    def hook_perms(cls, request, project_id, cluster_list, filter_use=False):
        default_perms = {perm: True for perm in cls.POLICY_LIST}
        default_perms.update({"view": True, "use": True, "delete": True})
        cluster_list = cluster_list or []
        for data in cluster_list:
            data["permissions"] = default_perms
        return cluster_list

    def register(self, cluster_id, cluster_name, environment=None):
        """注册集群
        """
        return super(Cluster, self).register(cluster_id, cluster_name)

    def delete_cluster(self, cluster_id, environment=None):
        """删除集群
        """
        resource_id = f"cluster:{cluster_id}"
        ret = self.iam_client.delete_res(self.RESOURCE_TYPE, resource_id)
        return ret

    def update_cluster(self, cluster_id, cluster_name):
        """更新注册集群的名称
        """
        resource_id = f"cluster:{cluster_id}"
        ret = self.iam_client.update_res(self.RESOURCE_TYPE, resource_id, cluster_name)
        return ret


class Namespace(PermissionMeta):
    """命名空间权限
    命名空间的 resource_id格式为：cluster:cluster1/namespace:namespace2
    """

    # 资源类型
    RESOURCE_TYPE = "namespace"
    RES_TYPE_NAME = "命名空间"

    # 功能列表
    POLICY_LIST = ["edit", "cluster-readonly", "cluster-manager"]

    def __init__(self, request, project_id, namespace_id, cluster_id=None, namespace_name=None):
        # 企业版权限中心resource_id为命名空间名称
        self.namespace_id = namespace_id
        self.namespace_name = namespace_name
        self.cluster = None
        super(Namespace, self).__init__(request, project_id, namespace_id)

        # 查询命名空间对应的集群信息
        if self.namespace_id and self.namespace_id != NO_RES:
            cluster_id, namespace_name = self.get_namespace_info(self.namespace_id)
            self.cluster = Cluster(request, project_id, cluster_id)
        elif cluster_id:
            self.cluster = Cluster(request, project_id, cluster_id)
        else:
            self.cluster = None

        self.namespace_name = namespace_name
        self.resource_name = namespace_name

        # 与资源无关
        if self.namespace_id == NO_RES:
            self.resource_id = NO_RES
        else:
            # 命名空间的 resource_id格式为：cluster:cluster1/namespace:namespace2
            self.resource_id = f"cluster:{cluster_id}/namespace:{self.namespace_name}"

    def get_namespace_info(self, namespace_id):
        namespace = paas_cc.get_namespace(self.access_token, self.project_id, namespace_id)
        cluster_id = namespace["data"]["cluster_id"]
        namespace_name = namespace["data"]["name"]
        return cluster_id, namespace_name

    def register(self, resource_id, resource_name):
        """注册资源到权限中心
        注册命名空间权限的时候，需要添加集群信息
        """
        # 获取集群信息
        cluster_id, namespace_name = self.get_namespace_info(resource_id)

        # 命名空间的 resource_id格式为：cluster:cluster1/namespace:namespace2
        resource_id = f"cluster:{cluster_id}/namespace:{resource_name}"
        ret = self.iam_client.register_res(
            self.user_id,
            self.RESOURCE_TYPE,
            resource_id,
            # 删除集群
            resource_name,
        )
        return ret

    def delete(self):
        ret = self.iam_client.delete_res(self.RESOURCE_TYPE, self.resource_id)
        return ret

    def can_create(self, raise_exception=True):
        """是否编辑命名空间权限
        """
        return True

    def can_use(self, raise_exception=True):
        """命名空间的使用权限，需要先判断集群的使用权限
        """
        return True

    def can_edit(self, raise_exception=True):
        """命名空间的编辑权限，需要先判断集群的使用权限
        """
        return True

    def hook_base_perms(
        self, ns_list, ns_id_flag="id", cluster_id_flag="cluster_id", ns_name_flag="name", **filter_parms
    ):  # noqa
        default_perms = {perm: True for perm in self.POLICY_LIST}
        default_perms.update({"create": True, "view": True, "use": True, "delete": True})
        ns_list = ns_list or []
        for data in ns_list:
            data["permissions"] = default_perms
        return ns_list

    def hook_perms(
        self, ns_list, filter_use=False, ns_id_flag="id", cluster_id_flag="cluster_id", ns_name_flag="name"
    ):  # noqa
        """批量添加权限
        """
        filter_parms = {}
        if filter_use:
            filter_parms["is_filter"] = True
            filter_parms["filter_type"] = "cluster-manager"
        return self.hook_base_perms(
            ns_list, ns_id_flag=ns_id_flag, cluster_id_flag=cluster_id_flag, ns_name_flag=ns_name_flag, **filter_parms
        )


class Templates(PermissionMeta):
    """模板集权限
    """

    # 资源类型
    RESOURCE_TYPE = "templates"
    RES_TYPE_NAME = _("模板集")

    # 功能列表
    POLICY_LIST = ["create", "delete", "view", "edit", "use"]


class Metric(PermissionMeta):
    """metric权限
    """

    # 资源类型
    RESOURCE_TYPE = "metric"
    RES_TYPE_NAME = "Metric"

    # 功能列表
    POLICY_LIST = ["edit", "create", "delete", "use"]


PERMS_DICT = {
    "cluster_prod": Cluster,
    "cluster_test": Cluster,
    "namespace": Namespace,
    "metric": Metric,
    "templates": Templates,
}


def get_perm_cls(resource_type, request, project_id, resource_id, resource_name):
    """获取权限实例
    给前端API校验使用
    """
    perm_cls = PERMS_DICT[resource_type]
    if perm_cls in (Namespace, Cluster):
        return perm_cls(request, project_id, resource_id)
    else:
        return perm_cls(request, project_id, resource_id, resource_name)


def get_access_token():
    return get_access_token_by_iam()


def verify_project_by_user(access_token, project_id, project_code, user_id):
    """
    验证用户是否有项目权限
    """
    iam_client = BKIAMClient(project_code)
    return iam_client.verify_project(user_id, project_code)


def get_all_user():
    resp = get_all_users()
    data = resp.get("data") or []
    users = []
    for _d in data:
        users.append({"id": _d.get("bk_username", ""), "name": _d.get("chname", "")})
    return users
