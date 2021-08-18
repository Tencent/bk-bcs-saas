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
from mock import patch
from rest_framework.test import APIRequestFactory

from backend.iam.open_apis.views import ResourceAPIView

factory = APIRequestFactory()


class TestTemplatesetAPI:
    """测试模板集资源拉取接口"""

    @patch("backend.iam.open_apis.provider.templateset.list_templatesets")
    def test_list_instance(self, mock_filter_templatesets, fake_project_id, fake_templateset_ids, template_data):
        """测试list_instance方法"""
        mock_filter_templatesets.return_value = template_data
        request = factory.post(
            '/apis/iam/v1/templatesets/',
            {
                'method': 'list_instance',
                'type': 'templateset',
                'page': {'offset': 0, 'limit': 1},
                "filter": {'parent': {'id': fake_project_id}},
            },
        )
        p_view = ResourceAPIView.as_view()
        response = p_view(request)
        data = response.data
        assert data['count'] == 2
        assert data['results'][0]['display_name'] == 'templateset_0001'

    @patch("backend.iam.open_apis.provider.templateset.list_templatesets")
    def test_fetch_instance_info_with_ids(
        self, mock_filter_templatesets, fake_project_id, fake_templateset_ids, template_data
    ):
        mock_filter_templatesets.return_value = template_data
        request = factory.post(
            '/apis/iam/v1/templatesets/',
            {
                'method': 'fetch_instance_info',
                'type': 'templateset',
                'page': {'offset': 0, 'limit': 1},
                "filter": {'parent': {'id': fake_project_id}},
            },
        )
        p_view = ResourceAPIView.as_view()
        response = p_view(request)
        data = response.data
        assert len(data) == 2
        assert data[0]['display_name'] == 'templateset_0001'
