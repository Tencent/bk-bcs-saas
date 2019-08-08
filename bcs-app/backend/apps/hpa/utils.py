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
