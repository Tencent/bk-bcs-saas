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
import mock
import pytest

from backend.tests.conftest import TEST_PROJECT_ID

pytestmark = pytest.mark.django_db
API_URL_PREFIX = f'/api/projects/{TEST_PROJECT_ID}/cc'


def fake_search_topo(*args, **kwargs):
    """ 返回测试用 topo 数据 """
    return {
        "result": True,
        "message": "success",
        "data": [
            {
                "default": 0,
                "bk_obj_name": "业务",
                "bk_obj_id": "biz",
                "child": [
                    {
                        "default": 0,
                        "bk_obj_name": "集群",
                        "bk_obj_id": "set",
                        "child": [
                            {
                                "default": 0,
                                "bk_obj_name": "模块",
                                "bk_obj_id": "module",
                                "child": [],
                                "bk_inst_id": 5003,
                                "bk_inst_name": "bcs-master",
                            },
                            {
                                "default": 0,
                                "bk_obj_name": "模块",
                                "bk_obj_id": "module",
                                "child": [],
                                "bk_inst_id": 5002,
                                "bk_inst_name": "bcs-node",
                            },
                        ],
                        "bk_inst_id": 5001,
                        "bk_inst_name": "BCS-K8S-1001",
                    }
                ],
                "bk_inst_id": 10001,
                "bk_inst_name": "BCS",
            }
        ],
    }


def fake_list_all_hosts(*args, **kwargs):
    """ 返回测试用主机数据 """
    return {
        "code": 0,
        "result": True,
        "message": "success",
        "data": [
            {
                "bk_bak_operator": "test_user",
                "bk_cloud_id": 0,
                "bk_comment": "",
                "bk_host_id": 123456,
                "bk_host_innerip": "127.0.0.1",
                "bk_host_name": "",
                "bk_host_outerip": "",
                "bk_idc_area": "xxx",
                "bk_idc_area_id": 1,
                "bk_os_name": "Linux",
                "bk_os_version": "1.0.0",
                "bk_svr_type_id": 1,
                "classify_level_name": "1",
                "hard_memo": "",
                "idc_id": 1,
                "idc_name": "IDC_NAME",
                "idc_unit_id": 1,
                "idc_unit_name": "123",
                "module_name": "A38000",
                "operator": "test_user",
                "rack": "3ABC-1",
                "svr_device_class": "S1234",
                "svr_type_name": "CVM_TEST",
            },
        ],
    }


def fake_get_project_cluster_resource(*args, **kwargs):
    """ 返回测试用的项目，集群数据 """
    return {
        "code": 0,
        "data": [
            {
                "cluster_list": [
                    {
                        "id": "BCS-K8S-1001",
                        "is_public": False,
                        "name": "测试用集群",
                        "namespace_list": [{"id": 101, "name": "default"}],
                    },
                ],
                "code": "service_test",
                "id": "b3776666666666666667037f",
                "name": "容器服务测试",
            },
        ],
        "message": "Query resource success",
        "result": True,
    }


def fake_get_all_cluster_hosts(*args, **kwargs):
    """ 返回测试用的集群节点信息 """
    return [{"cluster_id": "BCS-K8S-1001", "inner_ip": "127.0.0.1", "status": "normal"}]


def fake_get_agent_status(*args, **kwargs):
    """ 返回测试用 Agent 状态信息 """
    return [
        {"ip": "127.0.0.1", "bk_cloud_id": 0, "bk_agent_alive": 1},
        {"ip": "127.0.0.2", "bk_cloud_id": 0, "bk_agent_alive": 0},
    ]


class TestCCAPI:
    """ 测试 CMDB API 相关接口 """

    @mock.patch('backend.container_service.clusters.views.cc_host.cc.search_biz_inst_topo', new=fake_search_topo)
    def test_get_biz_inst_topology(self, api_client):
        """ 测试创建资源接口 """
        response = api_client.get(f'{API_URL_PREFIX}/topology/')
        assert response.json()['code'] == 0

    # mock cmdb, paas_cc, gse 接口
    @mock.patch(
        'backend.container_service.clusters.views.cc_host.cc.list_all_hosts_by_condition', new=fake_list_all_hosts
    )
    @mock.patch(
        'backend.container_service.clusters.views.cc_host.paas_cc.get_project_cluster_resource',
        new=fake_get_project_cluster_resource,
    )
    @mock.patch(
        'backend.container_service.clusters.views.cc_host.paas_cc.get_all_cluster_hosts',
        new=fake_get_all_cluster_hosts,
    )
    @mock.patch('backend.container_service.clusters.views.cc_host.gse.get_agent_status', new=fake_get_agent_status)
    def test_list_hosts(self, api_client):
        """ 测试获取资源列表接口 """
        response = api_client.post(f'{API_URL_PREFIX}/hosts/', data={})
        assert response.json()['code'] == 0
        # TODO 补充检查数据等 assert
