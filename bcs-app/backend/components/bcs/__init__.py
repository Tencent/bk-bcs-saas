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

from django.conf import settings
from django.utils.functional import cached_property

from backend.components import paas_cc
from backend.utils import cache, exceptions

APIGW = 'bcs_api'
API_HOST = settings.BCS_API_PRE_PATH


@cache.region.cache_on_arguments(expiration_time=600)
def cache_api_host(access_token, project_id, cluster_id, env):
    """cached api host
    cache performance, importance, cluster id shoud be unique
    参数在实例化MesosClient时检查
    """
    if cluster_id:
        cluster = paas_cc.get_cluster(access_token, project_id, cluster_id)
        if cluster.get('code') != 0:
            raise exceptions.ComponentError(cluster.get('message'))
        environment = cluster['data']['environment']
        stag = settings.BCS_API_ENV[environment]
    else:
        stag = env

    host = API_HOST.format(APIGW_HOST=settings.APIGW_HOST, APIGW=APIGW, STAG=stag)
    return host


class BCSClientBase:
    def __init__(self, access_token, project_id, cluster_id, env):
        self.access_token = access_token
        self.project_id = project_id
        self.cluster_id = cluster_id
        self.env = env

        # 初始化时就检查参数
        if not project_id:
            raise ValueError("project_id不能为空")

        if not cluster_id and not env:
            raise ValueError("cluster_id, env不能同时为空")

    @cached_property
    def api_host(self):
        """
        cluster_id, project为空，则使用env指定环境
        env如果没有指定，使用配置中的env
        环境区分
        DEV 环境 测试集群 -> Mesos UAT环境
                正式集群 -> Mesos DEBUG环境
        Test 环境 测试集群 -> Mesos UAT 环境
                正式集群 -> Mesos DEBUG环境
        Prod 环境 测试集群 -> Mesos DEBUG环境
                正式集群 -> Mesos PROD环境
        各个环境请在配置文件中配置，函数只通过集群动态选择
        """
        return cache_api_host(self.access_token, self.project_id, self.cluster_id, self.env)

    @property
    def _bcs_server_host(self):
        """通过不同的stag映射不同的bcs server原生地址
        """
        host = settings.BCS_SERVER_HOST[self._bcs_server_stag]
        return host

    @property
    def _bcs_server_stag(self):
        """获取集群所在stag
        """
        stag = self.api_host.split('/')[-1]
        return stag

    @property
    def _bcs_https_server_host(self):
        """有单独配置 BCS_HTTPS_SERVER_HOST 配置项
        """
        server_host = getattr(settings, 'BCS_HTTPS_SERVER_HOST', None)
        if server_host:
            return server_host[self._bcs_server_stag]
        return self._bcs_server_host

    @property
    def _bcs_server_host_ip(self):
        """获取server hostip配置
        """
        server_ip = getattr(settings, 'BCS_SERVER_HOST_IP', None)
        if server_ip:
            return server_ip[self._bcs_server_stag]

    @property
    def _bke_server_host(self):
        """bke地址
        """
        return settings.BKE_SERVER_HOST

    @property
    def _bke_server_host_ip(self):
        """bke地址
        """
        return getattr(settings, 'BKE_SERVER_HOST_IP', None)

    @property
    def _bke_https_server_host(self):
        """bke HTTPS 地址
        """
        server_host = getattr(settings, 'BKE_HTTPS_SERVER_HOST', None)
        if server_host:
            return server_host
        return self._bke_server_host

    @property
    def bcs_https_server_host(self):
        """根据集群ENV，获取bcs https 地址
        """
        stag = self._bcs_server_stag
        return settings.BCS_CLUSTER_ENV_AND_HTTPS_SERVER_HOST.get(stag)

    @property
    def headers(self):
        _headers = {
            "BCS-ClusterID": self.cluster_id,
            "X-BKAPI-AUTHORIZATION": json.dumps({
                "access_token": self.access_token,
                "project_id": self.project_id
            })
        }
        return _headers
