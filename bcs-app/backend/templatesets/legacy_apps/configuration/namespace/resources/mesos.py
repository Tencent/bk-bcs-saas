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
import base64
import logging

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from backend.components import paas_cc
from backend.components.bcs.mesos import MesosClient
from backend.container_service.misc.depot.api import get_jfrog_account
from backend.templatesets.legacy_apps.instance.constants import MESOS_IMAGE_SECRET, OLD_MESOS_IMAGE_SECRET
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes

logger = logging.getLogger(__name__)


def delete(access_token, project_id, cluster_id, ns_name):
    # 删除平台创建的secret，用于拉取image
    # TODO: 后续多次使用时，可以放置到resources中
    client = MesosClient(access_token, project_id, cluster_id, env=None)
    # 兼容ZK和etcd存储的不同的secret名称
    for secret_name in [MESOS_IMAGE_SECRET, OLD_MESOS_IMAGE_SECRET]:
        resp = client.delete_secret(ns_name, secret_name)
        if resp.get("code") == ErrorCode.NoError:
            continue
        msg = resp.get("message") or ""
        # TODO: 现阶段只能通过message判断secret不存在，并且忽略不存在的情况
        if ("not found" in msg) or ("not exist" in msg):
            continue
        raise error_codes.APIError(_("删除secret异常，{}").format(msg))


def get_namespace(access_token, project_id, cluster_id):
    """
    NOTE: mesos没有命名空间的概念，这样命名空间被应用等占用才会查询到命名空间
    """
    client = MesosClient(access_token, project_id, cluster_id, env=None)
    resp = client.get_used_namespace()
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(f'get namespace error, {resp.get("message")}')

    return resp.get('data') or []


def create_imagepullsecret(access_token, project_id, project_code, cluster_id, namespace):
    # get dept domain
    dept_domain = paas_cc.get_jfrog_domain(access_token, project_id, cluster_id)
    # 判断是否为研发仓库，正式环境分为：研发仓库、生产仓库，这2个仓库的账号要分开申请
    is_bk_dept = True if dept_domain.startswith(settings.BK_JFROG_ACCOUNT_DOMAIN) else False
    dept_account = get_jfrog_account(access_token, project_code, project_id, is_bk_dept)
    # get user or pwd by dept account
    user = dept_account.get('user', '')
    pwd = dept_account.get('password', '')
    # compose config
    secret_config = {
        "kind": "secret",
        "metadata": {"name": MESOS_IMAGE_SECRET, "namespace": namespace},
        "datas": {
            "user": {"content": base64.b64encode(user.encode(encoding="utf-8")).decode()},
            "pwd": {"content": base64.b64encode(pwd.encode(encoding="utf-8")).decode()},
        },
        "apiVersion": "v4",
    }
    client = MesosClient(access_token, project_id, cluster_id, env=None)
    resp = client.create_secret(namespace, secret_config)
    if (resp.get('code') != ErrorCode.NoError) and ('already exist' not in resp.get('message', '')):
        raise error_codes.APIError(f'create secret error, result.get("message")')
