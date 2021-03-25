# -*- coding: utf-8 -*-
from unittest.mock import patch

import pytest

from backend.infras.host_service import host
from backend.infras.host_service.perms import can_use_hosts
from backend.utils.error_codes import APIError

fake_cc_host_ok_results = {
    "result": True,
    "data": [{"bk_host_innerip": "127.0.0.1,127.0.0.3"}, {"bk_host_innerip": "127.0.0.2"}],
}
fake_cc_host_null_results = {"result": False}
fake_cc_host_not_match_results = {"results": True, "data": [{"bk_host_innerip": "127.0.0.1"}]}
expect_used_ip_list = ["127.0.0.1", "127.0.0.2"]


class TestCheckUseHost:
    @patch("backend.infras.host_service.perms.get_cc_hosts", return_value=fake_cc_host_ok_results)
    def test_ok(self, biz_id, username):
        assert can_use_hosts(biz_id, username, expect_used_ip_list)

    @patch("backend.infras.host_service.perms.get_cc_hosts", return_value=fake_cc_host_null_results)
    def test_null_resp_failed(self, biz_id, username):
        assert not can_use_hosts(biz_id, username, expect_used_ip_list)

    @patch("backend.infras.host_service.perms.get_cc_hosts", return_value=fake_cc_host_not_match_results)
    def test_not_match_failed(self, biz_id, username):
        assert not can_use_hosts(biz_id, username, expect_used_ip_list)


class TestGetCCHosts:
    @patch("backend.infras.host_service.host.cc.get_app_hosts", return_value={"result": False})
    def test_get_null_hosts(self, mock_get_app_hosts, biz_id, username):
        assert host.get_cc_hosts(username, biz_id) == []

    @patch("backend.infras.host_service.host.cc.get_app_hosts", return_value=fake_cc_host_ok_results)
    def test_get_hosts(self, mock_get_app_hosts, biz_id, username):
        assert host.get_cc_hosts(username, biz_id) == fake_cc_host_ok_results["data"]


class TestGetAgentStatus:
    @patch(
        "backend.infras.host_service.host.gse.get_agent_status",
        return_value=[
            {"ip": "127.0.0.1", "bk_cloud_id": 0, "bk_agent_alive": 1},
            {"ip": "127.0.0.2", "bk_cloud_id": 0, "bk_agent_alive": 1},
            {"ip": "127.0.0.3", "bk_cloud_id": 0, "bk_agent_alive": 1},
        ],
    )
    def test_get_agent_status(self, mocker):
        host_list = [
            host.HostData(inner_ip="127.0.0.1", bk_cloud_id_list=[host.BKCloudInfo(id=0)]),
            host.HostData(inner_ip="127.0.0.2,127.0.0.3", bk_cloud_id_list=[host.BKCloudInfo(id=0)]),
        ]
        agent_data = host.get_agent_status("admin", host_list)
        # 因为有一个主机两个网卡: 127.0.0.2, 127.0.0.3
        assert len(agent_data) == 3
        assert {"ip": "127.0.0.3", "bk_cloud_id": 0, "bk_agent_alive": 1} in agent_data


try:
    from .test_host_ext import *  # noqa
except ImportError as e:
    pass


fake_task_id = 123
fake_task_url = "http://test.com"


class TestSopsApi:
    fake_params = {
        "cc_app_id": "1",
        "username": "admin",
        "region": "ap-nanjing",
        "cvm_type": "cvm_type",
        "disk_size": 100,
        "replicas": 1,
        "network_type": "overlay",
    }

    @patch(
        "backend.infras.host_service.host.sops.SopsClient.create_task",
        return_value={"result": True, "data": {"task_id": fake_task_id, "task_url": fake_task_url}},
    )
    @patch(
        "backend.infras.host_service.host.sops.SopsClient.start_task",
        return_value={"result": True, "data": {"task_id": fake_task_id}},
    )
    def test_create_and_start_sops_task(self, mock_start_task, mock_create_task):
        task_id, task_url = host.create_and_start_sops_task(**self.fake_params)
        assert task_id == fake_task_id
        assert task_url == fake_task_url

    @patch(
        "backend.infras.host_service.host.sops.SopsClient.create_task",
        return_value={"result": False, "message": "error message"},
    )
    def test_create_task_failed(self, mock_create_task):
        with pytest.raises(APIError):
            host.create_and_start_sops_task(**self.fake_params)

    @patch(
        "backend.infras.host_service.host.sops.SopsClient.get_task_status",
        return_value={
            "result": True,
            "data": {
                'children': {
                    'n93767c5d8d83d94a22bda6423358fda': {
                        'children': {},
                        'elapsed_time': 0,
                        'error_ignorable': False,
                        'finish_time': '2021-03-18 16:03:42 +0800',
                        'id': 'n93767c5d8d83d94a22bda6423358fda',
                        'loop': 1,
                        'name': "<class 'pipeline.core.flow.event.EmptyStartEvent'>",
                        'retry': 0,
                        'skip': False,
                        'start_time': '2021-03-18 16:03:42 +0800',
                        'state': 'FINISHED',
                        'state_refresh_at': '2021-03-18T08:03:42.394Z',
                        'version': 'd5d697dc92c73aea97461d93c24b886a',
                    },
                    'n9a9632fba9e39efa587cfc3a0666e1a': {
                        'children': {},
                        'elapsed_time': 734,
                        'error_ignorable': False,
                        'finish_time': '',
                        'id': 'n9a9632fba9e39efa587cfc3a0666e1a',
                        'loop': 1,
                        'name': '申领服务器（轮询）',
                        'retry': 0,
                        'skip': False,
                        'start_time': '2021-03-18 16:03:44 +0800',
                        'state': 'RUNNING',
                        'state_refresh_at': '2021-03-18T08:03:44.738Z',
                        'version': 'faed5baeb6003518bff75235aea6b6bb',
                    },
                    'nc7e829074ca3024a393e1187cfde9f5': {
                        'children': {},
                        'elapsed_time': 2,
                        'error_ignorable': False,
                        'finish_time': '2021-03-18 16:03:44 +0800',
                        'id': 'nc7e829074ca3024a393e1187cfde9f5',
                        'loop': 1,
                        'name': '申请CVM服务器',
                        'retry': 0,
                        'skip': False,
                        'start_time': '2021-03-18 16:03:42 +0800',
                        'state': 'FINISHED',
                        'state_refresh_at': '2021-03-18T08:03:44.662Z',
                        'version': '982549095a6b35b2bceebadee64c516d',
                    },
                    'n93767c5d8d83d94a22bda6423358fd1': {
                        'children': {},
                        'elapsed_time': 0,
                        'error_ignorable': False,
                        'finish_time': '2021-03-18 16:03:42 +0800',
                        'id': 'n93767c5d8d83d94a22bda6423358fda',
                        'loop': 1,
                        'name': "<class 'pipeline.core.flow.event.EmptyEndEvent'>",
                        'retry': 0,
                        'skip': False,
                        'start_time': '2021-03-18 16:03:42 +0800',
                        'state': 'FINISHED',
                        'state_refresh_at': '2021-03-18T08:03:42.394Z',
                        'version': 'd5d697dc92c73aea97461d93c24b886a',
                    },
                },
                'elapsed_time': 737,
                'error_ignorable': False,
                'finish_time': '',
                'id': 'n9355daa30c330188f02d5a75bc17e2a',
                'loop': 1,
                'name': "<class 'pipeline.core.pipeline.Pipeline'>",
                'retry': 0,
                'skip': False,
                'start_time': '2021-03-18 16:03:42 +0800',
                'state': 'RUNNING',
                'state_refresh_at': '2021-03-18T08:03:42.374Z',
                'version': '',
            },
        },
    )
    def test_get_task_state_and_steps(self, mock_get_task_status):
        status_and_steps = host.get_task_state_and_steps(fake_task_id)
        assert status_and_steps["state"] == "RUNNING"
        assert status_and_steps["steps"]["申请CVM服务器"]["state"] == "FINISHED"
        assert "<class 'pipeline.core.flow.event.EmptyStartEvent'>" not in status_and_steps["steps"]
        assert "<class 'pipeline.core.flow.event.EmptyEndEvent'>" not in status_and_steps["steps"]
