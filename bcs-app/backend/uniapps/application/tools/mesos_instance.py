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
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from django.utils.translation import ugettext_lazy as _

from backend.container_service.clusters.base import CtxCluster
from backend.resources.namespace.utils import get_namespace_id
from backend.templatesets.legacy_apps.configuration.models import get_model_class_by_resource_name
from backend.templatesets.legacy_apps.configuration.models.template import ShowVersion, VersionedEntity
from backend.templatesets.legacy_apps.instance.models import InstanceConfig, VersionInstance
from backend.templatesets.legacy_apps.instance.utils import generate_namespace_config
from backend.utils.error_codes import error_codes

from .mesos_controller import InstanceController, InstanceData

logger = logging.getLogger(__name__)


def get_instance(ns_id: str, name: str, kind: str) -> Optional[InstanceConfig]:
    """获取实例
    注意: 这里ns_id包含了集群id+命名空间名称
    """
    try:
        return InstanceConfig.objects.get(namespace=ns_id, name=name, category=kind, is_deleted=False)
    except InstanceConfig.DoesNotExist:
        logger.error("资源: %s 不存在", f"{kind}:{ns_id}:{name}")
        return


def get_template_id_list(id: int, kind: str) -> List:
    """根据实例类型获取版本下模板ID列表"""
    try:
        version_entity = VersionedEntity.objects.get(id=id)
    except VersionedEntity.DoesNotExist:
        logger.error("版本%s下的模板不存在", id)
        return []
    entity = json.loads(version_entity.entity)
    return entity.get(kind, "").split(",")


@dataclass
class VersionInstanceData:
    """版本实例数据，用于组装配置信息
    instance_id: 资源ID
    name: 资源名称
    kind: 资源类型
    templateset_id: 模板集ID
    namespace_id: 命名空间ID
    version_id: 版本标识，对应real_version_id
    show_version_id: 版本ID
    username: 当前用户名称
    variables: 需要的变量信息
    """

    instance_id: int
    name: str
    kind: str
    templateset_id: int  # 模板集的ID
    namespace_id: int
    version_id: int  # 对应的是real_version_id
    show_version_id: int
    username: str
    variables: dict = field(default_factory=dict)

    def get_template_id(self) -> int:
        """获取资源模板ID"""
        id_list = get_template_id_list(self.version_id, self.kind)
        if not id_list:
            raise error_codes.RecordNotFound(_("版本{}下的模板不存在").format(self.version_id))
        res_model_cls = get_model_class_by_resource_name(self.kind)
        qs = res_model_cls.objects.filter(name=self.name, id__in=id_list)
        if not qs.exists():
            raise error_codes.RecordNotFound(_("模板{}不存在").format(self.name))
        return qs.first().id


def generate_manifest(ctx_cluster: CtxCluster, data: VersionInstanceData) -> Dict:
    params = {
        "instance_id": data.instance_id,
        "version_id": data.version_id,
        "show_version_id": data.show_version_id,
        "template_id": data.templateset_id,
        "project_id": ctx_cluster.project_id,
        "access_token": ctx_cluster.context.auth.access_token,
        "username": data.username,
        "lb_info": {},
        "variable_dict": data.variables,
        "is_preview": False,
    }

    configs = generate_namespace_config(
        data.namespace_id, {data.kind: [data.get_template_id()]}, is_save=False, **params
    )
    return configs[data.kind][0]["config"]


def scale_instance_resource(
    username: str, inst_data: InstanceData, ctx_cluster: CtxCluster, show_version: Optional[ShowVersion]
):
    # 针对没有版本控制或者通过非模板集创建的资源进行操作
    if not show_version:
        inst_controller = InstanceController(ctx_cluster, inst_data)
        inst_controller.scale_resource()
        return
    # 通过版本获取资源配置
    ns_id = get_namespace_id(ctx_cluster, inst_data.namespace)
    if not ns_id:
        raise error_codes.ResNotFoundError(_("集群:{}下命名空间:{}不存在").format(ctx_cluster.id, inst_data.namespace))
    instance = get_instance(ns_id, inst_data.name, inst_data.kind)
    if not instance:
        raise error_codes.RecordNotFound(
            _("资源{kind}:{ns_id}:{name}不存在").format(kind=inst_data.kind, ns_id=ns_id, name=inst_data.name)
        )
    render_data = VersionInstanceData(
        instance_id=instance.id,
        name=inst_data.name,
        username=username,
        templateset_id=show_version.template_id,
        namespace_id=ns_id,
        version_id=show_version.real_version_id,
        show_version_id=show_version.id,
        kind=inst_data.kind,
        variables=inst_data.variables,
    )
    inst_data.manifest = generate_manifest(ctx_cluster, render_data)
    inst_controller = InstanceController(ctx_cluster, inst_data)
    inst_controller.scale_resource()
    # 更新db中记录
    VersionInstance.objects.update_versions(
        instance_id=instance.instance_id,
        show_version_name=show_version.name,
        version_id=show_version.real_version_id,
        show_version_id=show_version.id,
    )
    InstanceConfig.objects.update_vars_and_configs(instance.id, inst_data.variables, inst_data.manifest)
