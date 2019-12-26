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
from django.conf.urls import url
from . import views


urlpatterns = [
    # 监控信息(New)
    url(r'^overview/$',
        views.performance.Cluster.as_view({'get': 'overview'})),

    url(r'^cpu/$',
        views.performance.Cluster.as_view({'get': 'cpu_usage'})),

    url(r'^memory/$',
        views.performance.Cluster.as_view({'get': 'memory_usage'})),

    url(r'^disk/$',
        views.performance.Cluster.as_view({'get': 'disk_usage'})),

    url(r'^node/cpu/$',
        views.performance.Node.as_view({'get': 'cpu_usage'})),

    url(r'^node/memory/$',
        views.performance.Node.as_view({'get': 'memory_usage'})),

    url(r'^node/network/$',
        views.performance.Node.as_view({'get': 'network_usage'})),

    url(r'^node/diskio/$',
        views.performance.Node.as_view({'get': 'diskio_usage'})),

    url(r'^container/cpu/$',
        views.performance.Container.as_view({'get': 'cpu_usage'})),

    url(r'^container/memory/$',
        views.performance.Container.as_view({'get': 'memory_usage'})),

    url(r'^container/network/$',
        views.performance.Container.as_view({'get': 'network_usage'})),

    url(r'^container/diskio/$',
        views.performance.Container.as_view({'get': 'diskio_usage'})),
]
