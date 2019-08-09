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
from backend.components.bcs import k8s
from backend.apps.instance import constants as instance_constants
from backend.apps.application import constants as application_constants

def get_current_metrics(instance):
    """获取当前监控值
    """
    current_metrics = {}
    for metric in instance['spec'].get('metrics') or []:
        name = metric['resource']['name']
        target = metric['resource']['target']['average_utilization']
        current_metrics[name] = {'target': target, 'current': None}

        _current_metrics = instance['status']['current_metrics']
        if not _current_metrics:
            return current_metrics

        for metric in _current_metrics:
            name = metric['resource']['name']
            current = metric['resource']['current']['average_utilization']
            current_metrics[name]['current'] = current

    return current_metrics

def get_current_metrics_display(instance):
    """当前监控值前端显示
    """
    current_metrics = []

    for name, value in get_current_metrics(instance).items():
        value['name'] = name.upper()
        # None 现在为-
        value['current'] = value['current'] or '-'
        current_metrics.append(value)

    display = ', '.join(f'{metric["name"]}({metric["current"]}/{metric["target"]})' for metric in current_metrics)

    return display

def get_cluster_hpa_list(access_token, project_id, cluster_id, cluster_env, cluster_name):
    """获取基础hpa列表
    """
    hpa_list = []
    client = k8s.K8SClient(access_token, project_id, cluster_id, env=cluster_env)
    hpa = client.list_hpa().to_dict()['items']

    for _config in hpa:
        labels = _config.get('metadata', {}).get('labels') or {}
        # 获取模板集信息
        template_id = labels.get(instance_constants.LABLE_TEMPLATE_ID)
        # 资源来源
        source_type = labels.get(instance_constants.SOURCE_TYPE_LABEL_KEY)
        if not source_type:
            source_type = "template" if template_id else "other"

        annotations = _config.get('metadata', {}).get('annotations') or {}

        data = {
            'cluster_name': cluster_name,
            'cluster_id': cluster_id,
            'name': _config['metadata']['name'],
            'namespace': _config['metadata']['namespace'],
            'max_replicas': _config['spec']['max_replicas'],
            'min_replicas': _config['spec']['min_replicas'],
            'current_replicas': _config['status']['current_replicas'],
            'current_metrics_display': get_current_metrics_display(_config),
            'current_metrics': get_current_metrics(_config),
            'source_type': application_constants.SOURCE_TYPE_MAP.get(source_type),
            'creator': annotations.get(instance_constants.ANNOTATIONS_CREATOR, ''),
            'create_time': annotations.get(instance_constants.ANNOTATIONS_CREATE_TIME, ''),
        }

        data['update_time'] = annotations.get(instance_constants.ANNOTATIONS_UPDATE_TIME, data['create_time'])
        data['updator'] = annotations.get(instance_constants.ANNOTATIONS_UPDATOR, data['creator'])
        hpa_list.append(data)

    return hpa_list
