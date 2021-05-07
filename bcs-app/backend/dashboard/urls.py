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

from backend.dashboard.subscribe.urls import router as subscribe_router
from backend.dashboard.workloads.urls import router as workload_router

urlpatterns = [
    url(r"^crds/", include("backend.dashboard.custom_object.urls")),
    url(r"^workloads/", include(workload_router.urls)),
    url(r"^subscribe/", include(subscribe_router.urls)),
]
