# -*- coding: utf-8 -*-
from unittest.mock import patch

from backend.components import cc


@patch("backend.components.cc.get_all_application")
def test_successful_get_app_by_user_role(mock_get_all_application):
    # 成功返回
    mock_get_all_application.return_value = {"code": 0, "data": [{"bk_biz_name": "test", "bk_biz_id": 1}]}
    biz_list = cc.get_app_by_user_role("admin")
    assert biz_list == [{"name": "test", "id": 1}]


@patch("backend.components.cc.get_all_application")
def test_failed_get_app_by_user_role(mock_get_all_application):
    # 异常返回
    mock_get_all_application.return_value = {"code": 400}
    biz_list = cc.get_app_by_user_role("admin")
    assert len(biz_list) == 0
