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
from datetime import datetime, timedelta

import pytest

from backend.bcs_k8s.app.models import App
from backend.bcs_k8s.app.views import AppView

pytestmark = pytest.mark.django_db

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
timeout_time = (datetime.now() - timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")


@pytest.fixture(autouse=True)
def cluster_record():
    App.objects.create(
        id=1,
        created=datetime.now(),
        updated=datetime.now(),
        project_id="project_id",
        cluster_id="cluster_id",
        name="demo",
        namespace="demo",
        namespace_id=0,
        transitioning_result=False,
        transitioning_message="",
        chart_id=1,
        release_id=1,
        transitioning_action="Install",
        transitioning_on=True,
        version="1.0.0",
    )


@pytest.mark.parametrize(
    "data, expect",
    [
        (
            {
                "id": 1,
                "transitioning_on": True,
                "transitioning_result": True,
                "updated": current_time,
                "transitioning_message": "",
            },
            {
                "id": 1,
                "transitioning_on": True,
                "transitioning_result": True,
                "updated": current_time,
                "transitioning_message": "",
            },
        ),
        (
            {
                "id": 1,
                "transitioning_on": True,
                "transitioning_result": True,
                "updated": timeout_time,
                "transitioning_message": "",
            },
            {
                "id": 1,
                "transitioning_on": False,
                "transitioning_result": False,
                "updated": timeout_time,
                "transitioning_message": "Helm操作超时，请重试!",
            },
        ),
    ],
)
def test_update_record_status(data, expect):
    AppView._update_record_status(data, data)
    assert App.objects.get(id=1).transitioning_on is expect["transitioning_on"]
    assert data == expect
