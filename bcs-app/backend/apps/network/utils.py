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
import re
import datetime
import copy
import logging
import json

from django.conf import settings
from rest_framework.exceptions import ValidationError

from backend.components.bcs import mesos
from backend.components import paas_cc
from backend.utils.error_codes import error_codes
from backend.utils.errcodes import ErrorCode
from backend.apps.instance.constants import LB_SYS_CONFIG, DEFAUT_LB_JFROG_DOMAIN
from backend.apps.instance.funutils import render_mako_context
from backend.apps.instance.generator import handle_intersection_item, handel_custom_network_mode
from backend.apps.application.constants import UNNORMAL_STATUS
from backend.apps.network.constants import K8S_HELM_VALUES_CONTENT, MESOS_LB_NAMESPACE_NAME
from backend.apps.network.models import MesosLoadBlance
from backend.apps.constants import CONTROLLER_IMAGE_PATH, BACKEND_IMAGE_PATH
from backend.apps.datalog.utils import get_data_id_by_project_id

logger = logging.getLogger(__name__)
DEFAULT_HTTP_PORT = "80"
DEFAULT_HTTPS_PORT = "443"
DEFAULT_LB_ADMIN_PORT = "38080"


def get_namespace_name(access_token, project_id, data_dict):
    """获取命名空间名称
    """
    ns_id = data_dict.get('namespace_id') or data_dict.get('namespace')
    if ns_id != -1:
        ns_resp = paas_cc.get_namespace(access_token, project_id, ns_id)
        namespace = ns_resp.get('data', {}).get('name')
    else:
        namespace = MESOS_LB_NAMESPACE_NAME
    return namespace


def handle_lb(username, access_token, project_id, lb_info, cc_app_id):
    """
    1. 组装 lb 配置文件
    2. 调用 bcs api 创建 Deployment
    """
    cluster_id = lb_info.get('cluster_id')
    # 查询zk的信息
    zk_res = paas_cc.get_zk_config(access_token, project_id, cluster_id)
    if zk_res.get("code") != ErrorCode.NoError:
        logger.err('获取zk信息出错,%s' % zk_res)
        raise error_codes.APIError.f(u"获取zk信息出错")
    try:
        zk_data = zk_res.get("data", [])[0]
    except Exception:
        logger.err('获取zk信息出错,%s' % zk_res)
        raise error_codes.APIError.f(u"获取zk信息出错")
    bcs_zookeeper = zk_data.get('bcs_zookeeper')
    zookeeper = zk_data.get('zookeeper')

    # 查询仓库地址
    jfrog_domain = paas_cc.get_jfrog_domain(
        access_token, project_id, cluster_id)
    if not jfrog_domain:
        jfrog_domain = DEFAUT_LB_JFROG_DOMAIN

    # 调度约束
    try:
        intersection_item = json.loads(lb_info.get("data"))
    except Exception:
        logger.exception("命名空间中的调度约束信息出错")
        raise error_codes.JsonFormatError.f("命名空间中的调度约束信息出错")
    new_intersection_item = handle_intersection_item(intersection_item)
    constraint = {"IntersectionItem": new_intersection_item}

    # vip 组装为labels
    try:
        ip_list = json.loads(lb_info.get('ip_list'))
    except Exception:
        logger.exception("命名空间中的IP集信息出错")
        raise error_codes.JsonFormatError.f("命名空间中的IP集信息出错")
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
    if data_dict.get('image_url'):
        lb_jfrog_url = f'{jfrog_domain}{data_dict["image_url"]}'
    else:
        lb_jfrog_url = f'{jfrog_domain}/paas/public/mesos/bcs-loadbalance'
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
        'SYS_JFROG_DOMAIN_URL': lb_jfrog_url,
        'CPU': str(resource_limit.get('cpu', 1)),
        'MEMORY': str(resource_limit.get('memory', 1024)),
        'IMAGE_VERSION': data_dict.get('image_version') or '1.1.0',
        'FORWARD_MODE': data_dict.get('forward_mode') or 'haproxy',
        'SYS_NAMESPACE': ns_name,
        'ETH_VALUE': data_dict.get('eth_value') or 'eth1',
        'LB_ADMIN_PORT': DEFAULT_LB_ADMIN_PORT
    }

    # 组装 lb 配置文件
    lb_config = copy.deepcopy(LB_SYS_CONFIG)
    lb_config['spec']['instance'] = data_dict.get('instance', 1)
    lb_config['constraint'] = constraint
    lb_config['spec']['template']['metadata']['labels'] = labels
    lb_config['spec']['template']['spec']['containers'][0]['ports'][0]['hostPort'] = \
        data_dict.get('host_port') or 31000
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
        logger.exception(
            u"LoadBalance配置文件变量替换错误\nconfig:%s\ncontext:%s" % (lb_config, context))
        raise ValidationError(u"配置文件中有未替换的变量")

    config_profile = json.loads(config_profile)
    # 调用bcs api 创建
    client = mesos.MesosClient(
        access_token, project_id, cluster_id, env=None)
    result = client.create_deployment(ns_name, config_profile)
    if not result.get('result'):
        error_msg = result.get('message', '')
        logger.error(u"命名空间[%s]下创建LoadBalance[%s]出错:%s" %
                     (ns_name, lb_name, error_msg))
        return False, error_msg
    return True, ''


def delete_lb_by_bcs(access_token, project_id, cluster_id, namespace, lb_name, lb_id):
    client = mesos.MesosClient(
        access_token, project_id, cluster_id, env=None)
    resp = client.delete_deployment(namespace, lb_name)
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
    client = mesos.MesosClient(
        access_token, project_id, cluster_id, env=None)

    resp = client.get_deployment(
        name=lb_name, field=field or "data", namespace=ns_name)
    if resp.get("code") != ErrorCode.NoError:
        status_dict = {
            'deployment_status': '',
            'deployment_status_message': resp.get("message")
        }
        return False, status_dict
    try:
        resp_datas = resp.get("data", [])[0].get('data', {})
    except Exception:
        status_dict = {
            'deployment_status': "",
            'deployment_status_message': u"查询不到deployment[%s]的状态" % lb_name
        }
        return False, status_dict

    status_dict = {
        'deployment_status': resp_datas.get('status'),
        'deployment_status_message': resp_datas.get('message')
    }
    if resp_datas.get('application_ext'):
        app_name = resp_datas.get('application_ext').get('name')
    else:
        app_name = resp_datas.get('application').get('name')

    # 需要 deployment 需要查询 Application 的状态
    resp = client.get_mesos_app_instances(
        app_name=app_name, field=field or "data", namespace=ns_name)

    if resp.get("code") != ErrorCode.NoError:
        status_dict['application_status'] = ''
        status_dict['application_status_message'] = resp.get("message")
        return False, status_dict
    resp_data = resp.get("data", [])
    if not resp_data:
        logger.error(u"查询不到loadbalance[%s]的状态:%s" % (lb_name, resp_data))
        status_dict['application_status'] = ''
        status_dict['application_status_message'] = u"查询不到application[%s]的状态" % app_name
        return False, status_dict

    status = resp_data[0].get('data', {}).get('status')
    status_dict['application_status'] = status
    status_dict['application_status_message'] = resp_data[0].get(
        'data', {}).get('message')
    if status in UNNORMAL_STATUS:
        logger.error(u"loadbalance[%s]的状态不正常:%s" % (lb_name, resp_data))
        return False, status_dict
    return True, status_dict


def render_helm_values(access_token, project_id, cluster_id, protocol_type, replica_count, namespace):
    """渲染helm values配置文件
    """
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
    jfrog_domain = paas_cc.get_jfrog_domain(
        access_token=access_token, project_id=project_id, cluster_id=cluster_id
    )
    # render
    template = K8S_HELM_VALUES_CONTENT
    template = template.replace("__REPO_ADDR__", jfrog_domain)
    template = template.replace("__CONTROLLER_IMAGE_PATH__", CONTROLLER_IMAGE_PATH)
    template = template.replace("__TAG__", "0.12.0")
    template = template.replace("__CONTROLLER_REPLICA_COUNT__", str(replica_count))
    template = template.replace("__BACKEND_IMAGE_PATH__", BACKEND_IMAGE_PATH)
    template = template.replace("__HTTP_ENABLED__", http_enabled)
    template = template.replace("__HTTP_PORT__", http_port)
    template = template.replace("__HTTPS_ENABLED__", https_enabled)
    template = template.replace("__HTTPS_PORT__", https_port)
    template = template.replace("__NAMESPACE__", namespace)

    return template
