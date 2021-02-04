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

from .views import service
from .views.charts import versions
from .views.ingress import mesos as mesos_ingress
from .views.lb import k8s, mesos_new

MESOS_CLUSTER_ID_REGEX = "BCS-((?!K8S)\w)+-[0-9]{5,7}"


urlpatterns = [
    # services：列表
    url(r'^api/network/(?P<project_id>\w{32})/services/$', service.Services.as_view({'get': 'get'})),
    url(
        r'^api/network/(?P<project_id>\w{32})/services/clusters/(?P<cluster_id>[\w\-]+)/'
        'namespaces/(?P<namespace>[\w\-]+)/endpoints/(?P<name>[\w.\-]+)/$',
        service.Services.as_view({'get': 'get_service_info', 'post': 'update_services', 'delete': 'delete_services'}),
    ),
    # 批量删除service
    url(
        r'^api/network/(?P<project_id>\w{32})/services/batch/$',
        service.Services.as_view({'post': 'batch_delete_services'}),
    ),
    # for k8s nginx ingress controller
    url(
        r'^api/network/(?P<project_id>\w{32})/k8s/lb/$',
        k8s.NginxIngressListCreateViewSet.as_view({'get': 'list', 'post': 'create'}),
    ),
    url(
        r'^api/network/(?P<project_id>\w{32})/clusters/(?P<cluster_id>[\w.\-]+)/k8s/lb/namespaces/$',
        k8s.NginxIngressListNamespaceViewSet.as_view({'get': 'list'}),
    ),
    url(
        r'^api/network/(?P<project_id>\w{32})/k8s/lb/(?P<pk>\d+)/$',
        k8s.NginxIngressRetrieveUpdateViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
    ),  # noqa
    # mesos ingress相关
    url(
        r'^api/projects/(?P<project_id>\w{32})/mesos/ingresses/$',
        mesos_ingress.IngressListViewSet.as_view({'get': 'list'}),
    ),
    url(
        r'^api/projects/(?P<project_id>\w{32})/clusters/(?P<cluster_id>%s)/'
        r'namespaces/(?P<namespace>[\w\-]+)/ingresses/(?P<name>[\w\-]+)/$' % MESOS_CLUSTER_ID_REGEX,
        mesos_ingress.IngressRetrieveOperateViewSet.as_view({'get': 'retrieve', 'delete': 'delete', 'put': 'update'}),
    ),
    url(
        r'^api/network/projects/(?P<project_id>\w{32})/chart/versions/$',
        versions.K8SIngressControllerViewSet.as_view({"get": "get_chart_versions"}),
    ),
    url(
        r'^api/network/projects/(?P<project_id>\w{32})/chart/versions/-/detail/$',
        versions.K8SIngressControllerViewSet.as_view({"post": "get_version_detail"}),
    ),
    url(
        r'^api/network/projects/(?P<project_id>\w{32})/clusters/-/mesos-lbs/$',
        mesos_new.LoadBalancersViewSet.as_view({"get": "list", "post": "create"}),
    ),
    url(
        r'^api/network/projects/(?P<project_id>\w{32})/clusters/(?P<cluster_id>[\w\-]+)'
        '/namespaces/(?P<namespace>[\w\-]+)/mesos-lbs/(?P<name>[\w\-]+)/$',
        mesos_new.LoadBalancerViewSet.as_view({"get": "detail", "put": "update_record", "delete": "delete_record"}),
    ),
    url(
        r'^api/network/projects/(?P<project_id>\w{32})/clusters/(?P<cluster_id>[\w\-]+)'
        '/namespaces/(?P<namespace>[\w\-]+)/mesos-lbs/(?P<name>[\w\-]+)/operation/$',
        mesos_new.LoadBalancerViewSet.as_view({"post": "deploy", "delete": "stop"}),
    ),
]
