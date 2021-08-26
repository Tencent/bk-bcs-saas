# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import logging

from django.conf import settings

from backend.components.bcs.mesos import MesosClient
from backend.templatesets.legacy_apps.configuration.models import CATE_SHOW_NAME
from backend.templatesets.legacy_apps.instance.constants import LABLE_METRIC_SELECTOR_LABEL

logger = logging.getLogger(__name__)


def get_metric_instances(
    access_token: str, project_id: str, metric_name: str, env: str, cluster_id_list: list, ns_dict: dict, instance_info
) -> list:
    metric_instance_list = []

    stag = settings.BCS_API_ENV[env]
    client = MesosClient(access_token=access_token, project_id=project_id, cluster_id=None, env=stag)
    try:
        metric_data = client.get_metrics(metric_name, cluster_id_list).get('data') or []
    except Exception as e:
        logger.exception("get_metrics error: %s", e)
        metric_data = []

    for _m in metric_data:
        namespace = _m.get('namespace')
        selector = _m.get('selector')

        s_key = f'{LABLE_METRIC_SELECTOR_LABEL}.{metric_name}'
        if s_key not in selector:
            continue

        selector_str = f'"{s_key}": "{metric_name}"'
        # 查询跟metric相关的应用
        ns_id = ns_dict.get(namespace)
        ins_list = instance_info.filter(namespace=ns_id, config__contains=selector_str).values_list('name', 'category')
        for _ins in ins_list:

            metric_instance_list.append(
                {
                    'ns_id': ns_id,
                    'namespace': namespace,
                    'name': _ins[0],
                    'category': CATE_SHOW_NAME.get(_ins[1], _ins[1]),
                }
            )

    return metric_instance_list
