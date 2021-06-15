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
from .featureflag.views import ClusterFeatureFlagViewSet
from .views.cluster import UpgradeClusterViewSet
from .views.node_views import labels, nodes, taints

urlpatterns = [
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/clusters/?$',
        views.ClusterCreateListViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='api.projects.clusters.create',
    ),
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/clusters/simple/$',
        views.ClusterCreateListViewSet.as_view({'get': 'list_clusters'}),
    ),
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/cluster/(?P<cluster_id>[\w\-]+)/?$',
        views.ClusterCreateGetUpdateViewSet.as_view({'get': 'retrieve', 'put': 'update', 'post': 'reinstall'}),
        name='api.projects.cluster',
    ),
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/clusters/(?P<cluster_id>[\w\-]+)/namespaces/$',
        views.NamespaceViewSet.as_view({'get': 'list_namespaces'}),
    ),
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/cluster/(?P<cluster_id>[\w\-]+)/opers/$',
        views.ClusterCheckDeleteViewSet.as_view({'get': 'check_cluster', 'delete': 'delete'}),
    ),
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/clusters_exist/$',
        views.ClusterFilterViewSet.as_view({'get': 'get'}),
        name='api.projects.filter_cluster',
    ),
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/cluster/(?P<cluster_id>[\w\-]+)/logs/?$',
        views.ClusterInstallLogView.as_view({'get': 'get'}),
        name='api.projects.cluster_install_log',
    ),
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/areas/?$',
        views.AreaListViewSet.as_view({'get': 'list'}),
        name='api.projects.areas',
    ),
    url(
        r'^api/areas/(?P<area_id>\d+)/$',
        views.AreaInfoViewSet.as_view({'get': 'info'}),
        name='api.areas.info',
    ),
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/cluster_nodes/(?P<cluster_id>[\w\-]+)/?$',
        views.NodeCreateListViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='api.projects.nodes',
    ),
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/clusters/(?P<cluster_id>[\w\-]+)/nodes/$',
        views.NodeCreateListViewSet.as_view({"post": "post_node_list", "get": "list_nodes_ip"}),
    ),
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/cluster/(?P<cluster_id>[\w\-]+)/node/(?P<node_id>[\w\-]+)/logs/?$',
        # noqa
        views.NodeUpdateLogView.as_view({'get': 'get'}),
        name='api.projects.node_update_log',
    ),
    # 单个节点docker版本信息
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/cluster/(?P<cluster_id>[\w\-]+)/node/info/',
        views.NodeInfo.as_view({'get': 'info'}),
    ),
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/cluster/(?P<cluster_id>[\w\-]+)/node/containers/',
        views.NodeContainers.as_view({'get': 'list'}),
    ),
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/cluster/(?P<cluster_id>[\w\-]+)/node/(?P<node_id>[\w\-]+)/failed_delete/?$',
        # noqa
        views.FailedNodeDeleteViewSet.as_view({'delete': 'delete'}),
    ),
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/cluster/(?P<cluster_id>[\w\-]+)/node/(?P<node_id>[\w\-]+)/?$',
        views.NodeGetUpdateDeleteViewSet.as_view(
            {'get': 'retrieve', 'put': 'update', 'delete': 'delete', 'post': 'reinstall'}
        ),
        name='api.projects.node',
    ),
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/cc_host_info/?$',
        views.CCHostListViewSet.as_view({'post': 'post'}),
        name='api.projects.cc_host_info',
    ),
    # 监控信息
    url(
        r'^api/projects/(?P<project_id>\w+)/metrics/cluster/summary/$',
        views.ClusterSummaryMetrics.as_view({'get': 'list'}),
    ),
    url(
        r'^api/projects/(?P<project_id>\w+)/metrics/cluster/?$',
        views.ClusterMetrics.as_view({'get': 'list'}),
    ),
    url(
        r'^api/projects/(?P<project_id>\w+)/metrics/node/?$',
        views.NodeMetrics.as_view({'get': 'list'}),
    ),
    url(
        r'^api/projects/(?P<project_id>\w+)/metrics/docker/?$',
        views.DockerMetrics.as_view({'get': 'list', 'post': 'multi'}),
    ),
    url(
        r'^api/projects/(?P<project_id>\w+)/metrics/node/summary/?$',
        views.NodeSummaryMetrics.as_view({'get': 'list'}),
    ),
    # cluster info
    url(
        r'^api/projects/(?P<project_id>\w{32})/clusters/(?P<cluster_id>[\w\-]+)/info/$',
        views.ClusterInfo.as_view({'get': 'cluster_info'}),
    ),
    # mster info
    url(
        r'^api/projects/(?P<project_id>\w{32})/clusters/(?P<cluster_id>[\w\-]+)/masters/info/$',
        views.ClusterMasterInfo.as_view({'get': 'cluster_masters'}),
    ),
    # node labels
    url(
        r'^api/projects/(?P<project_id>\w{32})/node_label_info/$',
        views.NodeLabelQueryCreateViewSet.as_view({'get': 'get_node_labels', 'post': 'create_node_labels'}),
    ),
    url(
        r'^api/projects/(?P<project_id>\w{32})/node_label_list/$', views.NodeLabelListViewSet.as_view({'get': 'list'})
    ),
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/clusters/(?P<cluster_id>[\w\-]+)/nodes/(?P<node_id>[\w\-]+)/force_delete/$',
        # noqa
        views.NodeForceDeleteViewSet.as_view({'delete': 'delete'}),
        name='api.projects.node.force_delete',
    ),
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/clusters/(?P<cluster_id>[\w\-]+)/nodes/(?P<node_id>[\w\-]+)/pods/scheduler/$',
        # noqa
        views.RescheduleNodePods.as_view({'put': 'put'}),
        name='api.projects.node.pod_taskgroup.reschedule',
    ),
    url(
        r"^api/projects/(?P<project_id>[\w\-]+)/clusters/(?P<cluster_id>[\w\-]+)/ippools/$",
        views.MesosIPPoolViewSet.as_view({"get": "get"}),
    ),
    url(
        r"^api/projects/(?P<project_id>\w{32})/clusters/(?P<cluster_id>[\w\-]+)/upgradeable_versions/$",
        UpgradeClusterViewSet.as_view({"get": "get_upgradeable_versions"}),
    ),
    url(
        r"^api/projects/(?P<project_id>\w{32})/clusters/(?P<cluster_id>[\w\-]+)/version/$",
        UpgradeClusterViewSet.as_view({"put": "upgrade"}),
    ),
]

# batch operation
urlpatterns += [
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/clusters/(?P<cluster_id>[\w\-]+)/nodes/batch/$',
        views.BatchUpdateDeleteNodeViewSet.as_view({'put': 'batch_update_nodes', 'delete': 'batch_delete_nodes'}),
    ),
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/clusters/(?P<cluster_id>[\w\-]+)/nodes/reinstall/$',
        views.BatchReinstallNodes.as_view({'post': 'reinstall_nodes'}),
    ),
]

# query api
urlpatterns += [
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/nodes/label_keys/$',
        views.QueryNodeLabelKeys.as_view({'get': 'label_keys'}),
    ),
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/nodes/label_values/$',
        views.QueryNodeLabelKeys.as_view({'get': 'label_values'}),
    ),
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/cluster_type_versions/$',
        views.ClusterVersionViewSet.as_view({'get': 'versions'}),
    ),
    url(r'^api/projects/(?P<project_id>[\w\-]+)/nodes/export/$', views.ExportNodes.as_view({'post': 'export'})),
    url(
        r"^api/cluster_mgr/projects/(?P<project_id>\w{32})/nodes/-/labels/detail/$",
        views.ListNodelabelsViewSets.as_view({"post": "list_labels_details"}),
    ),
    url(
        r"^api/cluster_mgr/projects/(?P<project_id>\w{32})/nodes/labels/$",
        views.QueryNodeLabelsViewSet.as_view({"get": "query_labels"}),
    ),
]

# operation api
urlpatterns += [
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/clusters/(?P<cluster_id>[\w\-]+)/nodes/(?P<node_id>\d+)/$',
        views.DeleteNodeRecordViewSet.as_view({'delete': 'delete'}),
    ),
    url(
        r"^api/cluster_mgr/projects/(?P<project_id>\w{32})/nodes/-/labels/$",
        views.NodelabelsViewSets.as_view({"post": "set_labels", "get": "list_labels"}),
    ),
]

urlpatterns += [
    url(
        r"^api/cluster_mgr/projects/(?P<project_id>\w{32})/clusters/(?P<cluster_id>[\w\-]+)/nodes/$",
        nodes.NodeViewSets.as_view({"get": "list_nodes"}),
    )
]

# 节点 taint 相关 API
urlpatterns += [
    url(
        r"^api/cluster_mgr/projects/(?P<project_id>\w{32})/clusters/(?P<cluster_id>[\w\-]+)/nodes/taints/$",
        taints.NodeTaintsViewSet.as_view({"post": "query_taints", "put": "set_taints"}),
    )
]

# 节点 标签 相关 API
urlpatterns += [
    url(
        r"^api/cluster_mgr/projects/(?P<project_id>\w{32})/clusters/(?P<cluster_id>[\w\-]+)/nodes/labels/$",
        labels.NodeLabelsViewSet.as_view({"post": "query_labels", "put": "set_labels"}),
    )
]

urlpatterns += [
    url(
        r'^api/projects/(?P<project_id>[\w\-]+)/clusters/(?P<cluster_id>[\w\-]+)/feature_flags/$',
        ClusterFeatureFlagViewSet.as_view({'get': 'get_cluster_feature_flags'}),
    )
]


# 导入版本特定urls
try:
    from .urls_ext import urlpatterns as urlpatterns_ext

    urlpatterns += urlpatterns_ext
except ImportError:
    pass
