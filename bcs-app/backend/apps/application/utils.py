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
import base64
import functools

from rest_framework.response import Response
from django.conf import settings

from backend.components.bcs.mesos import MesosClient
from backend.apps.application import constants
from backend.utils.basic import getitems
from backend.utils.errcodes import ErrorCode
from backend.components import paas_cc
from backend.utils.error_codes import error_codes

STAG_ENV = 2
PROD_ENV = 1


class APIResponse(Response):

    def __init__(self, data, *args, **kwargs):
        data.setdefault('code', 0)
        data.setdefault('message', '')
        return super(APIResponse, self).__init__(data, *args, **kwargs)


def image_handler(image):
    """处理镜像，只展示用户填写的一部分
    """
    for env in constants.SPLIT_IMAGE:
        info_split = image.split("/")
        if env in info_split:
            image = "/" + "/".join(info_split[info_split.index(env):])
            break
    return image


def get_k8s_desired_ready_instance_count(info, resource_name):
    """获取应用期望/正常的实例数量
    """
    filter_keys = constants.RESOURCE_REPLICAS_KEYS[resource_name]
    # 针对不同的模板获取不同key对应的值
    ready_replicas = getitems(info, filter_keys['ready_replicas_keys'], default=0)
    desired_replicas = getitems(info, filter_keys['desired_replicas_keys'], default=0)
    return desired_replicas, ready_replicas


def cluster_env(env, ret_num_flag=True):
    """集群环境匹配
    """
    all_env = settings.CLUSTER_ENV_FOR_FRONT
    front_env = all_env.get(env)
    if ret_num_flag:
        if front_env == "stag":
            return STAG_ENV
        else:
            return PROD_ENV
    else:
        return front_env


def get_project_namespaces(access_token, project_id):
    ns_resp = paas_cc.get_namespace_list(access_token, project_id, desire_all_data=True)
    if ns_resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(ns_resp.get('message'))
    data = ns_resp.get('data') or {}
    return data.get('results') or []


def get_namespace_name_map(access_token, project_id):
    project_ns_info = get_project_namespaces(access_token, project_id)
    return {ns['name']: ns for ns in project_ns_info}


def base64_encode_params(info):
    """base64编码
    """
    json_extra = bytes(json.dumps(info), 'utf-8')
    return base64.b64encode(json_extra)
