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
from django.conf.urls import url

from . import views

urlpatterns = [
    # 查询指定版本的 Application 信息
    url(
        r'^api/configuration/(?P<project_id>\w{32})/apps/(?P<version_id>\-?\d+)/$',
        views.ApplicationView.as_view({'get': 'list_apps'}),
    ),
    url(
        r'^api/configuration/projects/(?P<project_id>\w{32})/deployment/(?P<version_id>\-?\d+)/$',
        views.DeploymentView.as_view({'get': 'list'}),
    ),
    # 查询指定版本的 port 信息
    url(
        r'^api/configuration/(?P<project_id>\w{32})/ports/(?P<version_id>\-?\d+)/$',
        views.ApplicationView.as_view({'get': 'list_container_ports'}),
    ),
    # 检查端口是否已经被关联
    url(
        r'^api/configuration/(?P<project_id>\w{32})/check/version/(?P<version_id>\d+)/port/(?P<port_id>\-?\d+)/$',
        views.ApplicationView.as_view({'get': 'check_port_associated_with_service'}),
    ),
    # 查询 configmap 信息
    url(
        r'^api/configuration/(?P<project_id>\w{32})/configmap/(?P<version_id>\-?\d+)/$',
        views.ApplicationView.as_view({'get': 'list_configmaps'}),
    ),
    # 查询 secret 信息
    url(
        r'^api/configuration/(?P<project_id>\w{32})/secret/(?P<version_id>\-?\d+)/$',
        views.ApplicationView.as_view({'get': 'list_secrets'}),
    ),
    # 查询 namespace 下的 loadbalance 信息
    url(
        r'^api/configuration/projects/(?P<project_id>\w{32})/clusters/(?P<cluster_id>[\w\-]+)/lbs/$',
        views.ApplicationView.as_view({'get': 'get_lbs'}),
    ),
    # 查询指定版本的 Service 信息
    url(
        r'^api/projects/(?P<project_id>\w{32})/mesos/service/(?P<version_id>\-?\d+)/$',
        views.ServiceView.as_view({'get': 'list_services'}),
    ),
]
