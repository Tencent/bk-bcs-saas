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
from backend.apps.configuration.constants import RESOURCE_NAMES, K8sResourceName, MesosResourceName
from .base import POD_RES_LIST, logger
from .k8s import K8sDeployment, K8sConfigMap, K8sSecret, K8sDaemonSet, K8sJob, K8sService, K8sStatefulSet, K8sIngress
from .mesos import Application, Deplpyment, Service, ConfigMap, Secret

MODEL_CLASS_LIST = [K8sDeployment, K8sDaemonSet, K8sJob, K8sStatefulSet, K8sService, K8sConfigMap, K8sSecret,
                    K8sIngress, Application, Deplpyment, Service, ConfigMap, Secret]

RESOURCE_MODEL_MAP = dict(zip(RESOURCE_NAMES, MODEL_CLASS_LIST))

MODULE_DICT = {
    "application": Application,
    "deployment": Deplpyment,
    "service": Service,
    "configmap": ConfigMap,
    "secret": Secret,
    # k8s 相关资源
    "K8sDeployment": K8sDeployment,
    "K8sService": K8sService,
    "K8sConfigMap": K8sConfigMap,
    "K8sSecret": K8sSecret,
    "K8sDaemonSet": K8sDaemonSet,
    "K8sJob": K8sJob,
    "K8sStatefulSet": K8sStatefulSet,
    "K8sIngress": K8sIngress,
}


def get_model_class_by_resource_name(resource_name):
    return RESOURCE_MODEL_MAP[resource_name]


def get_pod_related_service(ventity, resource_name, resource_id):
    """检查包含 pod 的资源是否被模板内的 Service 关联
    """
    model_class = get_model_class_by_resource_name(resource_name)
    pod_res = model_class.objects.get(id=resource_id)

    deploy_tag = pod_res.deploy_tag
    pod_res_tag = '%s|%s' % (deploy_tag, resource_name)

    # 获取模板中 Service 的 关联的 pod tag
    service_id_list = ventity.get_resource_id_list(K8sResourceName.K8sService.value)

    if not service_id_list:
        return pod_res.name, []

    related_svc_names = []
    service_qsets = K8sService.objects.filter(id__in=service_id_list)
    for svc in service_qsets:
        if pod_res_tag in svc.get_deploy_tag_list():
            related_svc_names.append(svc.name)

    return pod_res.name, related_svc_names


def get_service_related_statefulset(ventity, service_id):
    """获取 关联 Service 的 statefulset 列表
    """
    svc = K8sService.objects.get(id=service_id)
    svc_tag = svc.service_tag

    # 获取模板中 statefulset 中的 Service tag
    ss_id_list = ventity.get_resource_id_list(K8sResourceName.K8sStatefulSet.value)

    if not ss_id_list:
        return svc.name, []

    related_ss_names = []
    ss_qsets = K8sStatefulSet.objects.filter(id__in=ss_id_list)
    for ss in ss_qsets:
        if svc_tag in ss.service_tag:
            related_ss_names.append(ss.name)

    return svc.name, related_ss_names


def get_application_related_resource(ventity, app_id):
    application = Application.objects.get(id=app_id)

    related_deploy_names = []
    deployment_id_list = ventity.get_resource_id_list(MesosResourceName.deployment.value)
    if deployment_id_list:
        deploy_qsets = Deplpyment.objects.filter(id__in=deployment_id_list, app_id=app_id)
        related_deploy_names = [f'Deplpyment[{deploy.name}]' for deploy in deploy_qsets]

    service_id_list = ventity.get_resource_id_list(MesosResourceName.application.value)
    if not service_id_list:
        return application.name, related_deploy_names

    related_svc_names = []
    service_qsets = Service.objects.filter(id__in=service_id_list)
    for svc in service_qsets:
        if app_id in svc.get_app_id_list():
            related_svc_names.append(f'Service[{svc.name}')

    return application.name, related_deploy_names + related_svc_names


def get_secret_name_by_certid(cert_id, ingress_name):
    """由tls证书的名称组装secret的名称
    certId: "perrier.ffm"
    tls: 证书名称不能为空，只支持英文大小写、数字、下划线和英文句号
    secret名称: 以小写字母或数字开头和结尾，只能包含：小写字母、数字、连字符(-)、点(.)
    """
    cert_id = str(cert_id).replace('_', '-')
    return '%s-%s-srt' % (ingress_name, cert_id)


def _to_resource_tags_map(tag_list):
    """处理前端传的 deploy_tag ，需要判断 deploy_tag 是属于 Deployment/StatefulSet/job/DaemonSet
    """
    resource_tag_map = {}
    for tag in tag_list:
        if not tag:
            continue

        deploy_tag, res_name = tag.split('|')
        if res_name not in POD_RES_LIST:
            res_name = K8sResourceName.K8sDeployment.value

        if res_name in resource_tag_map:
            deploy_tag_list = resource_tag_map[res_name]
            deploy_tag_list.append(deploy_tag)
            resource_tag_map[res_name] = deploy_tag_list
        else:
            resource_tag_map[res_name] = [deploy_tag, ]
    return resource_tag_map


# TODO mark refactor 由get_pod_qsets_by_tag替代
def get_pod_list_by_tag(tag_list, entity):
    pod_list = []
    tag_dict = _to_resource_tags_map(tag_list)
    for res_name in tag_dict:
        if res_name in POD_RES_LIST:
            res_tag_list = tag_dict[res_name]
            # 需要查询所有包含 pod 的资源
            _des = entity.get(res_name) if entity else None
            des_id_list = _des.split(',') if _des else []

            des_list = MODULE_DICT.get(
                res_name).objects.filter(id__in=des_id_list)
            des_list = des_list.filter(deploy_tag__in=res_tag_list)
            pod_list.extend(des_list)
    return pod_list


def get_pod_qsets_by_tag(tag_list, ventity):
    pod_qsets = []
    tag_map = _to_resource_tags_map(tag_list)
    for res_name in tag_map:
        model_class = get_model_class_by_resource_name(res_name)
        res_id_list = ventity.get_resource_id_list(res_name)
        res_qsets = model_class.objects.filter(id__in=res_id_list).filter(deploy_tag__in=tag_map[res_name])
        pod_qsets.extend(res_qsets)
    return pod_qsets


# TODO mark refactor 由get_k8s_container_ports替代
def get_k8s_port_list(pod_list):
    ports = []
    for pod in pod_list:
        containers = pod.get_containers()
        for _con in containers:
            _port_list = _con.get('ports')
            for _port in _port_list:
                ports.append({
                    'name': _port.get('name'),
                    'containerPort': _port.get('containerPort'),
                    'id': _port.get('id')
                })
    return ports


def get_k8s_container_ports(pod_qsets):
    ports = []
    for pod_res in pod_qsets:
        ports.extend(pod_res.get_ports())
    return ports
