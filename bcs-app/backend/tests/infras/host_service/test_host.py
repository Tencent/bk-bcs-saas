# -*- coding: utf-8 -*-
import pytest
from unittest.mock import patch

from backend.infras.host_service.perms import check_use_hosts
from backend.infras.host_service.exceptions import IPPermissionDenied


fake_cc_host_ok_results = {
    "result": True,
    "data": [{"bk_host_innerip": "127.0.0.1"}, {"bk_host_innerip": "127.0.0.2"}],
}
fake_cc_host_null_results = {"result": False}
fake_cc_host_not_match_results = {"results": True, "data": [{"bk_host_innerip": "127.0.0.1"}]}
expect_used_ip_list = ["127.0.0.1", "127.0.0.2"]


class TestCheckUseHost:
    @patch("backend.infras.host_service.perms.get_cc_hosts", return_value=fake_cc_host_ok_results)
    def test_ok(self, biz_id, username):
        check_use_hosts(biz_id, username, expect_used_ip_list)

    @patch("backend.infras.host_service.perms.get_cc_hosts", return_value=fake_cc_host_null_results)
    def test_null_resp_failed(self, biz_id, username):
        with pytest.raises(IPPermissionDenied):
            check_use_hosts(biz_id, username, expect_used_ip_list)

    @patch("backend.infras.host_service.perms.get_cc_hosts", return_value=fake_cc_host_not_match_results)
    def test_not_match_failed(self, biz_id, username):
        with pytest.raises(IPPermissionDenied):
            check_use_hosts(biz_id, username, expect_used_ip_list)
