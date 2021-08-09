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
from django.conf.urls import include, url

from . import views

cluster_urlpatterns = [
    # 监控信息(New)
    url(r"^overview/$", views.performance.Cluster.as_view({"get": "overview"})),
    url(r"^cpu_usage/$", views.performance.Cluster.as_view({"get": "cpu_usage"})),
    url(r"^memory_usage/$", views.performance.Cluster.as_view({"get": "memory_usage"})),
    # Mesos metrics, 依赖BCS 1.18.3 版本
    url(r"^mesos_cpu_resource_remain/$", views.performance.MesosCluster.as_view({"get": "mesos_cpu_resource_remain"})),
    url(r"^mesos_cpu_resource_total/$", views.performance.MesosCluster.as_view({"get": "mesos_cpu_resource_total"})),
    url(r"^mesos_cpu_resource_used/$", views.performance.MesosCluster.as_view({"get": "mesos_cpu_resource_used"})),
    url(
        r"^mesos_memory_resource_remain/$",
        views.performance.MesosCluster.as_view({"get": "mesos_memory_resource_remain"}),
    ),
    url(
        r"^mesos_memory_resource_total/$",
        views.performance.MesosCluster.as_view({"get": "mesos_memory_resource_total"}),
    ),
    url(
        r"^mesos_memory_resource_used/$", views.performance.MesosCluster.as_view({"get": "mesos_memory_resource_used"})
    ),
    url(r"^disk_usage/$", views.performance.Cluster.as_view({"get": "disk_usage"})),
    url(r"^node/overview/$", views.performance.Node.as_view({"get": "overview"})),
    url(r"^node/info/$", views.performance.Node.as_view({"get": "info"})),
    url(r"^node/cpu_usage/$", views.performance.Node.as_view({"get": "cpu_usage"})),
    url(r"^node/memory_usage/$", views.performance.Node.as_view({"get": "memory_usage"})),
    url(r"^node/network_receive/$", views.performance.Node.as_view({"get": "network_receive"})),
    url(r"^node/network_transmit/$", views.performance.Node.as_view({"get": "network_transmit"})),
    url(r"^node/diskio_usage/$", views.performance.Node.as_view({"get": "diskio_usage"})),
    url(r"^pod/cpu_usage/$", views.performance.Pod.as_view({"get": "cpu_usage", "post": "cpu_usage"})),
    url(r"^pod/memory_usage/$", views.performance.Pod.as_view({"get": "memory_usage", "post": "memory_usage"})),
    url(
        r"^pod/network_receive/$", views.performance.Pod.as_view({"get": "network_receive", "post": "network_receive"})
    ),
    url(
        r"^pod/network_transmit/$",
        views.performance.Pod.as_view({"get": "network_transmit", "post": "network_transmit"}),
    ),
    url(r"^container/cpu_usage/$", views.performance.Container.as_view({"get": "cpu_usage", "post": "cpu_usage"})),
    url(r"^container/cpu_limit/$", views.performance.Container.as_view({"get": "cpu_limit", "post": "cpu_limit"})),
    url(
        r"^container/memory_usage/$",
        views.performance.Container.as_view({"get": "memory_usage", "post": "memory_usage"}),
    ),
    url(
        r"^container/memory_limit/$",
        views.performance.Container.as_view({"get": "memory_limit", "post": "memory_limit"}),
    ),
    url(r"^container/disk_read/$", views.performance.Container.as_view({"get": "disk_read", "post": "disk_read"})),
    url(r"^container/disk_write/$", views.performance.Container.as_view({"get": "disk_write", "post": "disk_write"})),
    url(
        r"^servicemonitors/$",
        views.servicemonitor.ServiceMonitor.as_view({"get": "list", "post": "create", "delete": "batch_delete"}),
    ),
    url(r"^targets/$", views.servicemonitor.Targets.as_view({"get": "list_instance"})),
    url(r"^services/$", views.servicemonitor.Services.as_view({"get": "list"})),
    url(r"^prometheus/update/$", views.servicemonitor.PrometheusUpdate.as_view({"get": "get", "put": "update"})),
    url(
        r"^servicemonitors/(?P<namespace>[\w-]+)/(?P<name>[\w-]+)/$",
        views.servicemonitor.ServiceMonitor.as_view({"get": "get", "delete": "delete", "put": "update"}),
    ),
    url(
        r"^servicemonitors/(?P<namespace>[\w-]+)/(?P<name>[\w-]+)/targets/$",
        views.servicemonitor.Targets.as_view({"get": "list"}),
    ),
    url(
        r"^servicemonitors/(?P<namespace>[\w-]+)/(?P<name>[\w-]+)/targets/graph/$",
        views.servicemonitor.Targets.as_view({"get": "graph"}),
    ),
]


urlpatterns = [
    url(r"^clusters/(?P<cluster_id>[\w-]+)/metrics/", include(cluster_urlpatterns)),
]
