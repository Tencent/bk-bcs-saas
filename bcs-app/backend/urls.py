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
from django.conf.urls import include, url
from django.contrib import admin
from django.views.decorators.cache import never_cache

from backend.utils import healthz
from backend.utils.serializers import patch_datetime_field
from backend.utils.views import VueTemplateView, LoginSuccessView

patch_datetime_field()

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^api/healthz/", healthz.healthz_view),
    url(r"^api/test/sentry/", healthz.test_sentry),
    url(r"^", include("backend.accounts.urls")),
    # 项目管理
    url(r"^", include("backend.apps.projects.urls", namespace="projects")),
    # 仓库管理
    url(r"^", include("backend.apps.depot.urls", namespace="depot")),
    # 集群管理
    url(r"^", include("backend.apps.cluster.urls", namespace="clusters")),
    # web_console
    url(r"^", include("backend.web_console.rest_api.urls", namespace="web_console")),
    # 网络管理
    url(r"^", include("backend.apps.network.urls", namespace="network")),
    # Resource管理
    url(r"^", include("backend.apps.resource.urls", namespace="resource")),
    # metric
    url(r"^", include("backend.apps.metric.urls", namespace="metric")),
    url(r"^api/projects/(?P<project_id>\w{32})/", include("backend.apps.metric.urls_new")),
    # 配置管理
    url(r"^", include("backend.apps.configuration.urls", namespace="configuration")),
    # 变量管理
    url(r"^", include("backend.apps.variable.urls", namespace="variable")),
    # 应用管理
    url(r"^", include("backend.apps.application.urls", namespace="application")),
    url(r"^", include("backend.activity_log.urls", namespace="activity_log")),
    # 权限验证
    url(r"^", include("backend.apps.verfy.urls", namespace="verfy")),
    # 监控中心, 有个controller_list api
    url(r"^", include("backend.apps.paas_monitor.urls", namespace="paas_monitor")),
    url(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # BCS K8S special urls
    url(r"^", include("backend.bcs_k8s.helm.urls", namespace="bcs_k8s_app")),
    url(r"^", include("backend.bcs_k8s.app.urls", namespace="bcs_k8s_helm")),
    # Ticket凭证管理
    url(r"^", include("backend.apps.ticket.urls", namespace="ticket")),
    url(r"^", include("backend.bcs_k8s.authtoken.urls", namespace="bcs_authtoken")),
    url(r"^api/hpa/projects/(?P<project_id>\w{32})/", include("backend.apps.hpa.urls", namespace="hpa")),
]

# 导入版本特定的urls
try:
    from backend.urls_bk import urlpatterns as urlpatterns_bk

    urlpatterns += urlpatterns_bk
except ImportError:
    pass


# vue urls 需要放到最后面
urlpatterns_vue = [
    # fallback to vue view
    url(r"^login_success.html", never_cache(LoginSuccessView.as_view())),
    url(r"^.*$", never_cache(VueTemplateView.as_view())),
]
urlpatterns += urlpatterns_vue
