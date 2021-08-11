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
import json
import logging
from itertools import groupby

from celery import shared_task

from backend.apps.constants import MetricProjectKind
from backend.components.bcs.mesos import MesosClient
from backend.container_service.observability.metric_mesos.models import Metric
from backend.templatesets.legacy_apps.instance.constants import InsState
from backend.templatesets.legacy_apps.instance.models import MetricConfig

logger = logging.getLogger(__name__)


@shared_task
def set_metric(access_token, project_id, project_kind, metric_id, ns_id_list=[]):
    """后台下发metric任务"""
    active_metric = MetricConfig.get_active_metric(metric_id, ns_id_list=ns_id_list)
    if not active_metric:
        logger.info("set_metric task: not have active metric for %s, %s, just ignore", project_id, metric_id)
        return

    metric = Metric.objects.filter(pk=metric_id).first()
    if not metric:
        logger.info("set_metric task: get metric failed for %s, %s, just ignore", project_id, metric_id)
        return

    _json = metric.to_json()
    if metric.http_method == 'GET':
        parameters = _json['http_body']
        if not isinstance(parameters, dict):
            parameters = {}
    else:
        parameters = {'body': metric.http_body}

    #  判断项目的类型
    cluster_type_dict = dict(MetricProjectKind._choices_labels.get_choices())
    cluster_type = cluster_type_dict.get(int(project_kind))

    active_metric_conf = [json.loads(i.config) for i in active_metric]
    for cluster_id, metrics in groupby(
        sorted(active_metric_conf, key=lambda x: x['clusterID']), key=lambda x: x['clusterID']
    ):
        metrics = [i for i in metrics]
        for m in metrics:
            m['version'] = metric.version
            m['port'] = metric.port
            m['uri'] = metric.uri
            m['method'] = metric.http_method
            m['frequency'] = metric.frequency
            m['head'] = _json['http_headers']
            m["parameters"] = parameters
            # 新增兼容 prometheus 采集的数据
            m["metricType"] = metric.metric_type
            m["constLabels"] = metric.get_const_labels
        client = MesosClient(access_token, project_id, cluster_id, None)
        result = client.set_metrics(metrics, cluster_type)
        logger.info("set_metric task result: %s", result)

    MetricConfig.objects.filter(pk__in=[i.id for i in active_metric]).update(ins_state=InsState.METRIC_UPDATED.value)
    logger.info("set_metric task: %s, %s, done", project_id, metric_id)


@shared_task
def delete_metric(access_token, project_id, project_kind, metric_id, op_type=None, ns_id_list=[]):
    """后台下发删除metric任务"""
    active_metric = MetricConfig.get_active_metric(metric_id, ns_id_list=ns_id_list)
    if not active_metric:
        logger.info("delete_metric task: not have active metric for %s, %s, just ignore", project_id, metric_id)
        return

    #  判断项目的类型
    cluster_type_dict = dict(MetricProjectKind._choices_labels.get_choices())
    cluster_type = cluster_type_dict.get(int(project_kind))

    active_metric_conf = [json.loads(i.config) for i in active_metric]
    for ns_cluster, metrics in groupby(
        sorted(active_metric_conf, key=lambda x: (x['namespace'], x['clusterID'])),
        key=lambda x: (x['namespace'], x['clusterID']),
    ):
        namespace = ns_cluster[0]
        cluster_id = ns_cluster[1]
        client = MesosClient(access_token, project_id, cluster_id, None)
        metric_name = [i['name'] for i in metrics]
        result = client.delete_metrics(namespace, metric_name, cluster_type)
        logger.info("delete_metric task result: %s", result)

    if op_type == 'pause':
        instance_status = InsState.METRIC_UPDATED.value
    else:
        instance_status = InsState.METRIC_DELETED.value

    MetricConfig.objects.filter(pk__in=[i.id for i in active_metric]).update(ins_state=instance_status)
    logger.info("delete_metric task: %s, %s, done", project_id, metric_id)
