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
import re

from rest_framework.exceptions import ValidationError

from backend.apps.configuration import models
from backend.apps.configuration.constants import MesosResourceName
from .constants import CONFIG_SCHEMA_MAP

MESOS_NAME_REGEX = re.compile(r'^[a-z]{1}[a-z0-9-]{0,254}$')
MESOS_NAME_ERROR_MSG = "名称格式错误，只能包含：小写字母、数字、连字符(-)，首字母必须是字母，长度小于256个字符"


def get_config_schema(resource_name):
    return CONFIG_SCHEMA_MAP[resource_name]


def validate_mesos_res_name(name):
    if not MESOS_NAME_REGEX.match(name):
        raise ValidationError(MESOS_NAME_ERROR_MSG)


def validate_res_duplicate(containers, category):
    res_containers_map = {}
    for c in containers:
        container_name = c.get('name')
        res_config = c.get(category)
        for res in res_config:
            res_name = res.get('name')
            if not res_name:
                continue

            # 挂载卷只检查自定义类型的
            if category == 'volumes' and res.get('type') != 'custom':
                continue

            if res_name not in res_containers_map:
                res_containers_map[res_name] = [container_name, ]
            else:
                res_containers_map[res_name].append(container_name)

    err_msg_list = []
    for res_name, container_names in res_containers_map.items():
        if len(res_containers_map[res_name]) > 1:
            err_msg_list.append(f"{res_name}: 在容器 {','.join(container_names)} 中重复")

    if err_msg_list:
        raise ValidationError(';'.join(err_msg_list))


def validate_app_in_ventity(app_id_list, version_id):
    try:
        ventity = models.VersionedEntity.objects.get(id=version_id)
    except models.VersionedEntity.DoesNotExist as e:
        raise ValidationError(f"模板集版本(id:{version_id})不存在")

    app_list = ventity.get_mesos_apps()
    validated_app_list = [app.get('app_id') for app in app_list]
    if not set(app_id_list).issubset(set(validated_app_list)):
        raise ValidationError(f"关联的 Application (app_id: {','.join(app_id_list)}) 不合法")


def get_port_info_from_containers(containers):
    port_info = {}
    for c in containers:
        container_name = c.get('name')
        res_config = c.get('ports')
        for res in res_config:
            res_name = res.get('name')
            if not res_name:
                continue

            if res_name not in port_info:
                port_info[res_name] = [container_name, ]
            else:
                port_info[res_name].append(container_name)

    return port_info


def validate_port_duplicate_in_ventity(containers, application_id, version_id):
    ventity = models.VersionedEntity.objects.get(id=version_id)
    application_id_list = ventity.get_resource_id_list(MesosResourceName.application.value)
    try:
        application_id_list.remove(str(application_id))
    except Exception:
        pass
    applications = models.Application.objects.filter(id__in=application_id_list)

    port_info = get_port_info_from_containers(containers)
    duplicate_port_info = {}
    for app in applications:
        icontainers = app.get_containers()
        iport_info = get_port_info_from_containers(icontainers)
        duplicate_port = port_info.keys() & iport_info.keys()
        for p in duplicate_port:
            info = f"应用[{app.name}容器[{','.join(iport_info[p])}]"
            if p not in duplicate_port_info:
                duplicate_port_info[p] = [info, ]
            else:
                duplicate_port_info[p].append(info)

    if duplicate_port_info:
        show_tips = json.dumps(duplicate_port_info, ensure_ascii=False)
        raise ValidationError(f"以下端口名称已经存在模板集的其他应用中存在:{show_tips[1:-1]}")
