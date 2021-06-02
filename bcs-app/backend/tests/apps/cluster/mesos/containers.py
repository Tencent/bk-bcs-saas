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
import mock
import pytest

from backend.container_service.clusters.driver.mesos import MesosDriver

fake_data = {
    "data": [
        {
            "namespace": "test",
            "_id": "60784aee781a70b71a3550e5",
            "data": {
                "hostIP": "127.0.0.1",
                "containerStatuses": [
                    {"containerID": "2e78a746b6ef5420e2ab3e7ba74c032cae8bb027ea83a29e4e7bd5564bde1577"}
                ],
            },
        },
        {
            "_id": "60784b02781a70b71a355158",
            "data": {
                "hostIP": "127.0.0.2",
                "containerStatuses": [
                    {"containerID": "c106a168ee3fd72d3581ed21073f5db1262732f89687fb01a5bcd1044a9f88b5"}
                ],
            },
            "namespace": "test1",
        },
    ]
}

fake_data_with_skip_namespace = {
    "data": [
        {
            "namespace": "test",
            "_id": "60784aee781a70b71a3550e5",
            "data": {
                "hostIP": "127.0.0.1",
                "containerStatuses": [
                    {"containerID": "2e78a746b6ef5420e2ab3e7ba74c032cae8bb027ea83a29e4e7bd5564bde1577"}
                ],
            },
        },
        {
            "_id": "60784b02781a70b71a355158",
            "data": {
                "hostIP": "127.0.0.3",
                "containerStatuses": [
                    {"containerID": "c106a168ee3fd72d3581ed21073f5db1262732f89687fb01a5bcd1044a9f88b5"}
                ],
            },
            "namespace": "test2",
        },
    ]
}


@pytest.mark.parametrize(
    "raw_data, expect",
    [(fake_data, {"127.0.0.1": 1, "127.0.0.2": 1}), (fake_data_with_skip_namespace, {"127.0.0.1": 1})],
)
def test_host_count(raw_data, expect):
    with mock.patch("backend.container_service.clusters.driver.mesos.MESOS_SKIP_NS_LIST", ["test2"]):
        data = MesosDriver.host_container_map(raw_data, raw_data)
    assert data == expect
