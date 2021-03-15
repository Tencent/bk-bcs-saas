# -*- coding: utf-8 -*-
from unittest.mock import patch

from backend.infras.host_service import host
from backend.infras.host_service.perms import can_use_hosts

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
    def test_get_agent_status(self):
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
