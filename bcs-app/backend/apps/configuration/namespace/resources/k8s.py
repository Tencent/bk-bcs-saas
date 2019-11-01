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
import logging

from django.conf import settings

from backend.components import paas_cc
from backend.components.bcs.k8s import K8SClient
from backend.utils.error_codes import error_codes
from backend.utils.errcodes import ErrorCode
from backend.apps.constants import K8S_SYS_NAMESPACE, K8S_PLAT_NAMESPACE
from backend.apps.depot.api import get_jfrog_account, get_bk_jfrog_auth
from backend.apps.instance.constants import K8S_IMAGE_SECRET_PRFIX

logger = logging.getLogger(__name__)


def delete(access_token, project_id, cluster_id, ns_name):
    client = K8SClient(access_token, project_id, cluster_id, env=None)
    resp = client.delete_namespace(ns_name)
    if resp.get('code') == ErrorCode.NoError:
        return
    if 'not found' in resp.get('message'):
        return
    raise error_codes.APIError(f'delete namespace error, name: {ns_name}, {resp.get("message")}')


def get_namespace(access_token, project_id, cluster_id):
    client = K8SClient(access_token, project_id, cluster_id, env=None)
    resp = client.get_namespace()
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(f'get namespace error, {resp.get("message")}')
    data = resp.get('data') or []
    namespace_list = []
    # 过滤掉 系统命名空间和平台占用命名空间
    # TODO: 命名空间是否有状态不为Active的场景
    K8S_SYS_NAMESPACE.extend(K8S_PLAT_NAMESPACE)
    for info in data:
        if info['resourceName'] in K8S_SYS_NAMESPACE:
            continue
        namespace_list.append(info['resourceName'])
    return namespace_list


def create_jforg_account(access_token, project_id, project_code, cluster_id):
    domain_list = paas_cc.get_jfrog_domain_list(access_token, project_id, cluster_id)
    if not domain_list:
        raise error_codes.APIError('get jfrog domain error, domain is empty')
    domain_list = set(domain_list)
    # get user auth by project
    jfrog_account = get_jfrog_account(access_token, project_code, project_id)
    user_pwd = f'{jfrog_account.get("user")}:{jfrog_account.get("password")}'
    user_auth = {'auth': base64.b64encode(user_pwd.encode(encoding='utf-8')).decode()}
    # compose many jfrog account auth
    auth_dict = {}
    for _d in domain_list:
        if _d.startswith(settings.BK_JFROG_ACCOUNT_DOMAIN):
            _bk_auth = get_bk_jfrog_auth(access_token, project_code, project_id)
            auth_dict[_d] = _bk_auth
        else:
            auth_dict[_d] = user_auth

    return auth_dict


def create_secret(access_token, project_id, project_code, cluster_id, namespace):
    """先和先前逻辑保持一致
    """
    jfrog_auth = {'auths': create_jforg_account(access_token, project_id, project_code, cluster_id)}
    auth_bytes = bytes(json.dumps(jfrog_auth), 'utf-8')
    secret_config = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {
            "name": f"{K8S_IMAGE_SECRET_PRFIX}{namespace}",
            "namespace": namespace
        },
        "data": {
            ".dockerconfigjson": base64.b64encode(auth_bytes).decode()
        },
        "type": "kubernetes.io/dockerconfigjson"
    }
    #
    client = K8SClient(access_token, project_id, cluster_id, env=None)
    resp = client.create_secret(namespace, secret_config)
    if (resp.get('code') != ErrorCode.NoError) and ('already exists' not in resp.get('message', '')):
        raise error_codes.APIError(f'create secret error, {resp.get("message")}')