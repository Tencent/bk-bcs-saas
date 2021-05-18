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
from django.urls import path, re_path
from django.views.decorators.cache import never_cache

from backend.utils import healthz
from backend.utils.views import LoginSuccessView, VueTemplateView

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^api/healthz/", healthz.healthz_view),
    url(r"^api/test/sentry/", healthz.test_sentry),
    url(r"^", include("backend.accounts.urls")),
    # 项目管理, namespace 名称 SKIP_REQUEST_NAMESPACE 配置中, 不能省略
    re_path(r"^", include(("backend.apps.projects.urls", "backend.apps.projects"), namespace="projects")),
    # 仓库管理
    url(r"^", include("backend.apps.depot.urls")),
    # 集群管理
    url(r"^", include("backend.apps.cluster.urls")),
    # web_console
    url(r"^", include("backend.web_console.rest_api.urls")),
    # 网络管理
    url(r"^", include("backend.apps.network.urls")),
    # Resource管理
    url(r"^", include("backend.apps.resource.urls")),
    # metric
    url(r"^", include("backend.apps.metric.urls")),
    url(r"^api/projects/(?P<project_id>\w{32})/", include("backend.apps.metric.urls_new")),
    # 配置管理(旧模板集)
    url(r"^", include("backend.apps.configuration.urls")),
    # TODO 新模板集url入口，后续替换上面的configuration
    url(r"^api/templatesets/projects/(?P<project_id>\w{32})/", include("backend.apps.templatesets.urls")),
    # 变量管理
    url(r"^", include("backend.apps.variable.urls")),
    # 应用管理
    url(r"^", include("backend.apps.application.urls")),
    url(r"^", include("backend.activity_log.urls")),
    # 权限验证
    url(r"^", include("backend.apps.verfy.urls")),
    url(r"^api-auth/", include("rest_framework.urls")),
    # BCS K8S special urls
    url(r"^", include("backend.bcs_k8s.helm.urls")),
    url(r"^", include("backend.bcs_k8s.app.urls")),
    # Ticket凭证管理
    url(r"^", include("backend.apps.ticket.urls")),
    url(r"^", include("backend.bcs_k8s.authtoken.urls")),
    url(
        r"^api/hpa/projects/(?P<project_id>\w{32})/",
        include(
            "backend.apps.hpa.urls",
        ),
    ),
    # cd部分api
    url(r"^cd_api/", include("backend.apps.apis.urls")),
    url(r"^apis/", include("backend.apis.urls")),
    url(
        r"^api/dashboard/projects/(?P<project_id>\w{32})/clusters/(?P<cluster_id>[\w\-]+)/",
        include("backend.dashboard.urls"),
    ),
    path(
        "api/logstream/projects/<slug:project_id>/clusters/<slug:cluster_id>/",
        include("backend.container_service.observability.log_stream.urls"),
    ),
]

# 导入版本特定的urls
try:
    from backend.urls_ext import urlpatterns as urlpatterns_ext

    urlpatterns += urlpatterns_ext
except ImportError:
    pass


# vue urls 需要放到最后面
urlpatterns_vue = [
    # fallback to vue view
    url(r"^login_success.html", never_cache(LoginSuccessView.as_view())),
    url(r"^.*$", never_cache(VueTemplateView.as_view())),
]
urlpatterns += urlpatterns_vue
