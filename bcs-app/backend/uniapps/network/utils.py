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
import copy
import datetime
import json
import logging
import re

from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError

from backend.apps.constants import BACKEND_IMAGE_PATH, CONTROLLER_IMAGE_PATH
from backend.components import paas_cc
from backend.components.bcs import mesos
from backend.templatesets.legacy_apps.instance import constants as inst_constants
from backend.templatesets.legacy_apps.instance.funutils import render_mako_context
from backend.templatesets.legacy_apps.instance.generator import handel_custom_network_mode, handle_intersection_item
from backend.uniapps.application.constants import UNNORMAL_STATUS
from backend.uniapps.network.constants import K8S_NGINX_INGRESS_CONTROLLER_CHART_VALUES, MESOS_LB_NAMESPACE
from backend.uniapps.network.models import MesosLoadBlance
from backend.utils.basic import getitems
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes

try:
    from backend.container_service.observability.datalog.utils import get_data_id_by_project_id
except ImportError:
    from backend.container_service.observability.datalog_ce.utils import get_data_id_by_project_id

logger = logging.getLogger(__name__)
DEFAULT_HTTP_PORT = "80"
DEFAULT_HTTPS_PORT = "443"
DEFAULT_LB_ADMIN_PORT = "38080"


def get_namespace_name(access_token, project_id, data_dict):
    """获取命名空间名称"""
    ns_id = data_dict.get('namespace_id') or data_dict.get('namespace')
    if ns_id != -1:
        ns_resp = paas_cc.get_namespace(access_token, project_id, ns_id)
        namespace = ns_resp.get('data', {}).get('name')
    else:
        namespace = MESOS_LB_NAMESPACE
    return namespace


def get_image_url(image_url, use_custom_image_url, access_token, project_id, cluster_id):
    if use_custom_image_url:
        return image_url
    # 查询仓库地址
    repo_domain = paas_cc.get_jfrog_domain(access_token, project_id, cluster_id)
    if not repo_domain:
        repo_domain = inst_constants.DEFAULT_LB_REPO_DOMAIN
    if image_url:
        return f"{repo_domain}{image_url}"
    return f"{repo_domain}{inst_constants.DEFAULT_MESOS_LB_IMAGE_PATH}"


def handle_lb(username, access_token, project_id, lb_info, cc_app_id, **params):
    """
    1. 组装 lb 配置文件
    2. 调用 bcs api 创建 Deployment
    """
    cluster_id = lb_info.get('cluster_id')
    # 查询zk的信息
    zk_res = paas_cc.get_zk_config(access_token, project_id, cluster_id)
    if zk_res.get("code") != ErrorCode.NoError:
        logger.error('获取zk信息出错,%s', zk_res)
        raise error_codes.APIError(_("获取zk信息出错"))
    try:
        zk_data = zk_res.get("data", [])[0]
    except Exception:
        logger.error('获取zk信息出错,%s', zk_res)
        raise error_codes.APIError(_("获取zk信息出错"))
    bcs_zookeeper = zk_data.get('bcs_zookeeper')
    zookeeper = zk_data.get('zookeeper')
    # 调度约束
    try:
        intersection_item = json.loads(lb_info.get("data"))
    except Exception:
        logger.exception("命名空间中的调度约束信息出错")
        raise error_codes.JsonFormatError(_("命名空间中的调度约束信息出错"))
    new_intersection_item = handle_intersection_item(intersection_item)
    constraint = {"IntersectionItem": new_intersection_item}

    # vip 组装为labels
    try:
        ip_list = json.loads(lb_info.get('ip_list'))
    except Exception:
        logger.exception("命名空间中的IP集信息出错")
        raise error_codes.JsonFormatError(_("命名空间中的IP集信息出错"))
    labels = {}
    for i, ip in enumerate(ip_list):
        _key = "io.tencent.bcs.netsvc.requestip.%s" % i
        labels[_key] = ip

    lb_name = lb_info.get('name')
    # 配置文件中的变量赋值
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 获取 namespace
    data_dict = lb_info['data_dict']
    if data_dict:
        data_dict = json.loads(data_dict)
    else:
        data_dict = {}
    lb_image_url = get_image_url(
        data_dict.get("image_url"), params["use_custom_image_url"], access_token, project_id, cluster_id
    )
    resource_limit = data_dict.get('resources', {}).get('limits', {})
    ns_name = get_namespace_name(access_token, project_id, data_dict)
    # 获取data标准日志输出
    data_info = get_data_id_by_project_id(project_id)
    data_id = str(data_info.get('standard_data_id'))

    context = {
        'SYS_PROJECT_KIND': 2,  # 固定为mesos
        'SYS_STANDARD_DATA_ID': data_id,
        'SYS_CC_APP_ID': cc_app_id,
        'SYS_PROJECT_ID': project_id,
        'SYS_OPERATOR': username,
        'SYS_CLUSTER_ID': cluster_id,
        'SYS_BCSGROUP': lb_name,
        'SYS_CC_ZK': zookeeper,
        'SYS_BCS_ZK': bcs_zookeeper,
        'SYS_CREATOR': username,
        'SYS_UPDATOR': username,
        'SYS_CREATE_TIME': now_time,
        'SYS_UPDATE_TIME': now_time,
        'LB_IMAGE_URL': lb_image_url,
        'CPU': str(resource_limit.get('cpu', 1)),
        'MEMORY': str(resource_limit.get('memory', 1024)),
        'IMAGE_VERSION': data_dict.get('image_version') or '1.1.0',
        'FORWARD_MODE': data_dict.get('forward_mode') or 'haproxy',
        'SYS_NAMESPACE': ns_name,
        'ETH_VALUE': data_dict.get('eth_value') or 'eth1',
        'LB_ADMIN_PORT': DEFAULT_LB_ADMIN_PORT,
    }

    # 组装 lb 配置文件
    lb_config = copy.deepcopy(inst_constants.LB_SYS_CONFIG)
    lb_config['spec']['instance'] = data_dict.get('instance', 1)
    lb_config['constraint'] = constraint
    lb_config['spec']['template']['metadata']['labels'] = labels
    lb_config['spec']['template']['spec']['containers'][0]['ports'][0]['hostPort'] = (
        data_dict.get('host_port') or 31000
    )
    # 处理网络模式
    spec = lb_config.get('spec', {}).get('template', {}).get('spec', {})
    spec['networkMode'] = data_dict.get('networkMode')
    spec['networkType'] = data_dict.get('networkType')
    spec['custom_value'] = data_dict.get('custom_value')
    lb_config = handel_custom_network_mode(lb_config)

    lb_config = json.dumps(lb_config)
    try:
        config_profile = render_mako_context(lb_config, context)
    except Exception:
        logger.exception(u"LoadBalance配置文件变量替换错误\nconfig:%s\ncontext:%s" % (lb_config, context))
        raise ValidationError(_("配置文件中有未替换的变量"))

    config_profile = json.loads(config_profile)
    # 调用bcs api 创建
    client = mesos.MesosClient(access_token, project_id, cluster_id, env=None)
    result = client.create_deployment(ns_name, config_profile)
    if not result.get('result'):
        error_msg = result.get('message', '')
        logger.error(f"命名空间[{ns_name}]下创建LoadBalance[{lb_name}]出错:{error_msg}")
        return False, error_msg
    return True, ''


def delete_lb_by_bcs(access_token, project_id, cluster_id, namespace, lb_name, lb_id, enforce=False):
    client = mesos.MesosClient(access_token, project_id, cluster_id, env=None)
    resp = client.delete_deployment(namespace, lb_name, enforce=enforce)
    if resp.get("code") == ErrorCode.NoError:
        lb_info = MesosLoadBlance.objects.filter(id=lb_id)
        lb_info.update(
            # is_deleted=True,
            # deleted_time=datetime.datetime.now(),
            # name="%s:deleted:%s" % (lb_id, lb_info[0].name),
            status="deleted"
        )
    return resp


def get_lb_status(access_token, project_id, lb_name, cluster_id, ns_name, field=None, lb_id=None):
    client = mesos.MesosClient(access_token, project_id, cluster_id, env=None)

    resp = client.get_deployment(name=lb_name, field=field or "data", namespace=ns_name)
    if resp.get("code") != ErrorCode.NoError:
        status_dict = {'deployment_status': '', 'deployment_status_message': resp.get("message")}
        return False, status_dict
    try:
        resp_datas = resp.get("data", [])[0].get('data', {})
    except Exception:
        status_dict = {
            'deployment_status': "",
            'deployment_status_message': '{}[{}]{}'.format(_("查询不到deployment"), lb_name, _("的状态")),
        }
        return False, status_dict

    status_dict = {
        'deployment_status': resp_datas.get('status'),
        'deployment_status_message': resp_datas.get('message'),
    }
    if resp_datas.get('application_ext'):
        app_name = resp_datas.get('application_ext').get('name')
    else:
        app_name = resp_datas.get('application').get('name')

    # 需要 deployment 需要查询 Application 的状态
    resp = client.get_mesos_app_instances(app_name=app_name, field=field or "data", namespace=ns_name)

    if resp.get("code") != ErrorCode.NoError:
        status_dict['application_status'] = ''
        status_dict['application_status_message'] = resp.get("message")
        return False, status_dict
    resp_data = resp.get("data", [])
    if not resp_data:
        logger.error("查询不到loadbalance[%s]的状态:%s" % (lb_name, resp_data))
        status_dict['application_status'] = ''
        status_dict['application_status_message'] = '{}application[{}]{}'.format(_("查询不到"), app_name, _("的状态"))
        return False, status_dict

    status = resp_data[0].get('data', {}).get('status')
    status_dict['application_status'] = status
    status_dict['application_status_message'] = resp_data[0].get('data', {}).get('message')
    if status in UNNORMAL_STATUS:
        logger.error(f"loadbalance[{lb_name}]的状态不正常:{resp_data}")
        return False, status_dict
    return True, status_dict


def render_helm_values(access_token, project_id, cluster_id, protocol_type, replica_count, namespace):
    """渲染helm values配置文件"""
    # check protocol exist
    http_enabled = "false"
    https_enabled = "false"
    http_port = DEFAULT_HTTP_PORT
    https_port = DEFAULT_HTTPS_PORT
    protocol_type_list = re.findall(r"[^,; ]+", protocol_type)
    for info in protocol_type_list:
        protocol_port = info.split(":")
        if "http" in protocol_port:
            http_enabled = "true"
            http_port = protocol_port[-1] if len(protocol_port) == 2 and protocol_port[-1] else DEFAULT_HTTP_PORT
        if "https" in protocol_port:
            https_enabled = "true"
            https_port = protocol_port[-1] if len(protocol_port) == 2 and protocol_port[-1] else DEFAULT_HTTPS_PORT
    jfrog_domain = paas_cc.get_jfrog_domain(access_token=access_token, project_id=project_id, cluster_id=cluster_id)
    # render
    template = K8S_NGINX_INGRESS_CONTROLLER_CHART_VALUES
    template = template.replace("__REPO_ADDR__", jfrog_domain)
    template = template.replace("__CONTROLLER_IMAGE_PATH__", CONTROLLER_IMAGE_PATH)
    # TODO: 先调整为固定版本，后续允许用户在前端选择相应的版本
    template = template.replace("__TAG__", "0.35.0")
    template = template.replace("__CONTROLLER_REPLICA_COUNT__", str(replica_count))
    template = template.replace("__BACKEND_IMAGE_PATH__", BACKEND_IMAGE_PATH)
    template = template.replace("__HTTP_ENABLED__", http_enabled)
    template = template.replace("__HTTP_PORT__", http_port)
    template = template.replace("__HTTPS_ENABLED__", https_enabled)
    template = template.replace("__HTTPS_PORT__", https_port)
    template = template.replace("__NAMESPACE__", namespace)

    return template


def get_project_clusters(access_token, project_id):
    resp = paas_cc.get_all_clusters(access_token, project_id, desire_all_data=1)
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(_("获取项目下集群信息异常，{}").format(resp.get('message')))
    return resp['data'].get('results') or []


def get_cluster_ingresses(access_token, project_id, cluster_id):
    client = mesos.MesosClient(access_token, project_id, cluster_id, env=None)
    result = client.get_custom_resource_by_cluster()
    return result['items']


def get_project_namespaces(access_token, project_id):
    resp = paas_cc.get_namespace_list(access_token, project_id, desire_all_data=1)
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(_("获取项目下命名空间信息异常，{}").format(resp.get('message')))
    return resp['data'].get('results') or []


def get_cluster_namespaces(access_token, project_id, cluster_id):
    resp = paas_cc.get_cluster_namespace_list(access_token, project_id, cluster_id, desire_all_data=1)
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(_("获取集群下命名空间信息异常，{}").format(resp.get('message')))
    return resp['data'].get('results') or []


def get_svc_access_info(manifest, cluster_id, extended_routes):
    """
    {
        'external': {
            'NodePort': ['node_ip:{node_port}'],
        },
        'internal': {
            'ClusterIP': [':{port} {Protocol}']
        }
    }
    """
    access_info = {'external': {}, 'internal': {}}
    svc_type = getitems(manifest, ['spec', 'type'])
    ports = getitems(manifest, ['spec', 'ports'])

    if not ports:
        return access_info

    if svc_type == 'ClusterIP':
        cluster_ip = getitems(manifest, ['spec', 'clusterIP'])
        if not cluster_ip or cluster_ip == 'None':
            cluster_ip = '--'
        access_info['internal'] = {'ClusterIP': [f"{cluster_ip}:{p['port']} {p['protocol']}" for p in ports]}
    elif svc_type == 'NodePort':
        access_info['external'] = {'NodePort': [f":{p['nodePort']}" for p in ports]}

    return access_info


try:
    from .utils_ext import get_svc_access_info  # noqa
except ImportError as e:
    logger.debug('Load extension failed: %s', e)
