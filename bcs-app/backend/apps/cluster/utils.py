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
from datetime import datetime

from django.conf import settings
from django.core.paginator import Paginator
from django.utils.translation import ugettext as _

from backend.utils.error_codes import error_codes

DEFAULT_PAGE_LIMIT = 5
RoleNodeTag = 'N'
RoleMasterTag = 'M'


def custom_paginator(raw_data, offset, limit=None):
    """使用django paginator进行分页处理
    """
    limit = limit or DEFAULT_PAGE_LIMIT
    page_cls = Paginator(raw_data, limit)
    curr_page = 1
    if offset or offset == 0:
        curr_page = (offset // limit) + 1
    # 如果当前页大于总页数，返回为空
    count = page_cls.count
    if curr_page > page_cls.num_pages:
        return {
            "count": count,
            "results": []
        }
    # 获取当前页的数据
    curr_page_info = page_cls.page(curr_page)
    curr_page_list = curr_page_info.object_list
    return {
        "count": count,
        "results": curr_page_list
    }


def delete_node_labels_record(LabelModel, node_id_list, username):
    """删除数据库中关于节点标签的处理
    """
    LabelModel.objects.filter(node_id__in=node_id_list, is_deleted=False).update(
        is_deleted=True,
        deleted_time=datetime.now(),
        updator=username,
        labels=json.dumps({})
    )


def gen_hostname_params(ip_list, cluster_id, is_master):
    return ["%s %s" % (ip, gen_hostname(ip, cluster_id, is_master)) for ip in ip_list]


def gen_hostname(ip, cluster_id, is_master):
    role = RoleMasterTag if is_master else RoleNodeTag
    ip_str = ip.replace('.', '-')
    host_name = "ip-%s-%s-%s" % (ip_str, role, cluster_id)
    return host_name.lower()


def cluster_env_transfer(env_name, b2f=True):
    """tranfer name for frontend or cc
    """
    if b2f:
        transfer_name = settings.CLUSTER_ENV_FOR_FRONT.get(env_name)
    else:
        transfer_name = settings.CLUSTER_ENV.get(env_name)
    if not transfer_name:
        raise error_codes.APIError(_("没有查询到集群所属环境"))
    return transfer_name


def status_transfer(status, running_status_list, failed_status_list):
    """status display for frontend
    """
    if status in running_status_list:
        return "running"
    elif status in failed_status_list:
        return "failed"
    return "success"

def use_prometheus_source(request):
    """是否使用prometheus数据源
    """
    if settings.DEFAULT_METRIC_SOURCE == 'prometheus':
        return True
    if request.project.project_code in settings.DEFAULT_METRIC_SOURCE_PROM_WLIST:
        return True
    return False
