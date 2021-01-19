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
import logging

from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from backend.activity_log import client as activity_client
from backend.apps.application import constants as application_constants
from backend.apps.application.constants import DELETE_INSTANCE
from backend.apps.configuration.constants import K8sResourceName, MesosResourceName
from backend.apps.constants import ProjectKind
from backend.apps.instance import constants as instance_constants
from backend.apps.instance.models import InstanceConfig
from backend.components.bcs import k8s, mesos

logger = logging.getLogger(__name__)


class DeleteHPAError(Exception):
    pass


def get_mesos_current_metrics(instance):
    """获取当前监控值"""
    current_metrics = {}
    for metric in instance["spec"].get("metrics") or []:
        name = metric["Name"]
        target = metric["Target"]["averageUtilization"]
        current_metrics[name] = {"target": target, "current": None}

    _current_metrics = instance["status"]["CurrentMetrics"]
    if not _current_metrics:
        return current_metrics

    for metric in _current_metrics:
        name = metric["Name"]
        current = metric["Current"].get("averageUtilization", None)
        current_metrics[name]["current"] = current

    return current_metrics


def get_metric_name_value(metric, field):
    """获取metrics名称, 值"""
    metric_type = metric["type"]
    # CPU/MEM 等系统类型
    if metric_type == "Resource":
        name = metric["resource"]["name"]
        metric_value = metric["resource"][field]["averageUtilization"]
    else:
        # Pod等自定义类型
        name = metric[metric_type.lower()]["metric"]["name"]
        metric_value = metric[metric_type.lower()][field]["averageValue"]
    return name, metric_value


def get_k8s_current_metrics(instance):
    """获取当前监控值"""
    current_metrics = {}
    for metric in instance["spec"].get("metrics") or []:
        name, target = get_metric_name_value(metric, field="target")
        current_metrics[name] = {"target": target, "current": None}

    for metric in instance["status"].get("currentMetrics") or []:
        name, current = get_metric_name_value(metric, field="current")
        current_metrics[name]["current"] = current

    return current_metrics


def get_current_metrics_display(_current_metrics):
    """当前监控值前端显示"""
    current_metrics = []

    for name, value in _current_metrics.items():
        value["name"] = name.upper()
        # None 现在为-
        if value["current"] is None:
            value["current"] = "-"
        current_metrics.append(value)
    # 按CPU, Memory显示
    current_metrics = sorted(current_metrics, key=lambda x: x["name"])
    display = ", ".join(f'{metric["name"]}({metric["current"]}/{metric["target"]})' for metric in current_metrics)

    return display


def slz_mesos_hpa_info(hpa, project_code, cluster_name, cluster_env, cluster_id):
    hpa_list = []
    for _config in hpa:
        labels = _config.get("metadata", {}).get("labels") or {}
        # 获取模板集信息
        template_id = labels.get(instance_constants.LABLE_TEMPLATE_ID)
        # 资源来源
        source_type = labels.get(instance_constants.SOURCE_TYPE_LABEL_KEY)
        if not source_type:
            source_type = "template" if template_id else "other"

        annotations = _config.get("metadata", {}).get("annotations") or {}
        namespace = _config["metadata"]["namespace"]

        deployment_name = _config["spec"].get("ScaleTargetRef", {}).get("name")
        if not deployment_name:
            continue

        deployment_link = f"{settings.DEVOPS_HOST}/console/bcs/{project_code}/app/mesos/{deployment_name}/{namespace}/deployment?cluster_id={cluster_id}"  # noqa

        current_metrics = get_mesos_current_metrics(_config)
        data = {
            "cluster_name": cluster_name,
            "environment": cluster_env,
            "cluster_id": cluster_id,
            "name": _config["metadata"]["name"],
            "namespace": namespace,
            "max_replicas": _config["spec"]["MaxInstance"],
            "min_replicas": _config["spec"]["MinInstance"],
            "current_replicas": _config["status"].get("CurrentInstance", "-"),
            "current_metrics_display": get_current_metrics_display(current_metrics),
            "current_metrics": current_metrics,
            "source_type": application_constants.SOURCE_TYPE_MAP.get(source_type),
            "creator": annotations.get(instance_constants.ANNOTATIONS_CREATOR, ""),
            "create_time": annotations.get(instance_constants.ANNOTATIONS_CREATE_TIME, ""),
            "deployment_name": deployment_name,
            "deployment_link": deployment_link,
        }

        data["update_time"] = annotations.get(instance_constants.ANNOTATIONS_UPDATE_TIME, data["create_time"])
        data["updator"] = annotations.get(instance_constants.ANNOTATIONS_UPDATOR, data["creator"])
        hpa_list.append(data)
    return hpa_list


def slz_k8s_hpa_info(hpa, project_code, cluster_name, cluster_env, cluster_id):
    hpa_list = []
    for _config in hpa:
        labels = _config.get("metadata", {}).get("labels") or {}
        # 获取模板集信息
        template_id = labels.get(instance_constants.LABLE_TEMPLATE_ID)
        # 资源来源
        source_type = labels.get(instance_constants.SOURCE_TYPE_LABEL_KEY)
        if not source_type:
            source_type = "template" if template_id else "other"

        annotations = _config.get("metadata", {}).get("annotations") or {}
        namespace = _config["metadata"]["namespace"]
        deployment_name = _config["spec"]["scaleTargetRef"]["name"]

        deployment_link = f"{settings.DEVOPS_HOST}/console/bcs/{project_code}/app/deployments/{deployment_name}/{namespace}/deployment?cluster_id={cluster_id}"  # noqa
        current_metrics = get_k8s_current_metrics(_config)
        data = {
            "cluster_name": cluster_name,
            "environment": cluster_env,
            "cluster_id": cluster_id,
            "name": _config["metadata"]["name"],
            "namespace": namespace,
            "max_replicas": _config["spec"]["maxReplicas"],
            "min_replicas": _config["spec"]["minReplicas"],
            "current_replicas": _config["status"]["currentReplicas"],
            "current_metrics_display": get_current_metrics_display(current_metrics),
            "current_metrics": current_metrics,
            "source_type": application_constants.SOURCE_TYPE_MAP.get(source_type),
            "creator": annotations.get(instance_constants.ANNOTATIONS_CREATOR, ""),
            "create_time": annotations.get(instance_constants.ANNOTATIONS_CREATE_TIME, ""),
            "deployment_name": deployment_name,
            "deployment_link": deployment_link,
        }

        data["update_time"] = annotations.get(instance_constants.ANNOTATIONS_UPDATE_TIME, data["create_time"])
        data["updator"] = annotations.get(instance_constants.ANNOTATIONS_UPDATOR, data["creator"])
        hpa_list.append(data)
    return hpa_list


def get_cluster_hpa_list(request, project_id, cluster_id, cluster_env, cluster_name, namespace=None):
    """获取基础hpa列表"""
    access_token = request.user.token.access_token
    project_code = request.project.english_name
    hpa_list = []

    try:
        if request.project.kind == ProjectKind.MESOS.value:
            client = mesos.MesosClient(access_token, project_id, cluster_id, env=cluster_env)
            hpa = client.list_hpa(namespace).get("data") or []
            hpa_list = slz_mesos_hpa_info(hpa, project_code, cluster_name, cluster_env, cluster_id)
        else:
            client = k8s.K8SClient(access_token, project_id, cluster_id, env=cluster_env)
            hpa = client.list_hpa(namespace).get("items") or []
            hpa_list = slz_k8s_hpa_info(hpa, project_code, cluster_name, cluster_env, cluster_id)
    except Exception as error:
        logger.error("get hpa list error, %s", error)

    return hpa_list


def delete_mesos_hpa(request, project_id, cluster_id, namespace, namespace_id, name):
    username = request.user.username
    access_token = request.user.token.access_token

    client = mesos.MesosClient(access_token, project_id, cluster_id, env=None)

    result = client.delete_hpa(namespace, name)

    if result.get("code") != 0:
        raise DeleteHPAError(_("删除HPA资源失败"))

    # 删除成功则更新状态
    InstanceConfig.objects.filter(namespace=namespace_id, category=MesosResourceName.hpa.value, name=name).update(
        updator=username, oper_type=DELETE_INSTANCE, deleted_time=timezone.now(), is_deleted=True, is_bcs_success=True
    )


def delete_k8s_hpa(request, project_id, cluster_id, namespace, namespace_id, name):
    username = request.user.username
    access_token = request.user.token.access_token

    client = k8s.K8SClient(access_token, project_id, cluster_id, env=None)
    try:
        client.delete_hpa(namespace, name)
    except client.rest.ApiException as error:
        if error.status == 404:
            # 404 错误忽略
            pass
        else:
            logger.info("delete hpa error, %s", error)
            raise DeleteHPAError(_("删除HPA资源失败"))
    except Exception as error:
        logger.error("delete hpa error, %s", error)
        raise DeleteHPAError(_("删除HPA资源失败"))

    # 删除成功则更新状态
    InstanceConfig.objects.filter(namespace=namespace_id, category=K8sResourceName.K8sHPA.value, name=name).update(
        updator=username, oper_type=DELETE_INSTANCE, deleted_time=timezone.now(), is_deleted=True, is_bcs_success=True
    )


def delete_hpa(request, project_id, cluster_id, ns_name, namespace_id, name):
    if request.project.kind == ProjectKind.K8S.value:
        delete_k8s_hpa(request, project_id, cluster_id, ns_name, namespace_id, name)
    else:
        delete_mesos_hpa(request, project_id, cluster_id, ns_name, namespace_id, name)


def get_mesos_deployment_hpa(request, project_id, cluster_id, ns_name):
    hpa_list = get_cluster_hpa_list(
        request, project_id, cluster_id, cluster_env=None, cluster_name=None, namespace=ns_name
    )
    hpa_deployment_list = [(ns_name, i["deployment_name"]) for i in hpa_list]
    return hpa_deployment_list


def get_deployment_hpa(request, project_id, cluster_id, ns_name, deployments):
    """通过deployment查询HPA关联信息"""
    hpa_list = get_cluster_hpa_list(
        request, project_id, cluster_id, cluster_env=None, cluster_name=None, namespace=ns_name
    )

    hpa_deployment_list = [i["deployment_name"] for i in hpa_list]

    for deployment in deployments:
        if deployment["resourceName"] in hpa_deployment_list:
            deployment["hpa"] = True
        else:
            deployment["hpa"] = False

    return deployments


def activity_log(project_id, username, resource_name, description, status):
    """操作记录"""
    client = activity_client.ContextActivityLogClient(
        project_id=project_id, user=username, resource_type="hpa", resource=resource_name
    )
    if status is True:
        client.log_delete(activity_status="succeed", description=description)
    else:
        client.log_delete(activity_status="failed", description=description)
