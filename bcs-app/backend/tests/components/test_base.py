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
import pytest
import requests

from backend.components.base import BaseHttpClient, CompInternalError, CompRequestError, update_url_parameters
from backend.tests.testing_utils.base import nullcontext


class TestBaseHttpClient:
    def test_default_kwargs(self, requests_mock):
        requests_mock.get('http://test.com', json={})
        client = BaseHttpClient()
        client.request('GET', 'http://test.com/')

        req_history = requests_mock.request_history[0]
        assert req_history.headers.get('X-Request-Id') is not None
        assert req_history.timeout is not None
        assert req_history.verify is client._ssl_verify

    def test_request_json(self, requests_mock):
        requests_mock.get('http://test.com', json={'foo': 'bar'})
        client = BaseHttpClient()
        assert client.request_json('GET', 'http://test.com/') == {'foo': 'bar'}

    @pytest.mark.parametrize(
        'req_exc,exc',
        [
            (requests.exceptions.ConnectTimeout, CompRequestError),
            (ValueError, CompInternalError),
        ],
    )
    def test_request_error(self, req_exc, exc, requests_mock):
        requests_mock.get('http://test.com', exc=req_exc)
        with pytest.raises(exc):
            BaseHttpClient().request('GET', 'http://test.com/')

    @pytest.mark.parametrize(
        'status_code,exc',
        [
            (200, None),
            (404, CompRequestError),
            (500, CompRequestError),
        ],
    )
    def test_status_errors(self, status_code, exc, requests_mock):
        requests_mock.get('http://test.com', json={'foo': 'bar'}, status_code=status_code)
        exc_context = pytest.raises(exc) if exc else nullcontext()
        with exc_context:
            BaseHttpClient().request('GET', 'http://test.com/')


@pytest.mark.parametrize(
    'url,parameters,expected_result',
    [
        ('http://foo.com/path', {'foo': 'bar'}, 'http://foo.com/path?foo=bar'),
        ('https://foo.com/path/?bar=3', {'foo': 'bar'}, 'https://foo.com/path/?bar=3&foo=bar'),
        ('http://foo.com/path/?foo=3', {'foo': 'bar'}, 'http://foo.com/path/?foo=bar'),
        ('http://foo.com/path/?bar=3', {'foo': ['bar', 'baz']}, 'http://foo.com/path/?bar=3&foo=bar&foo=baz'),
    ],
)
def test_update_url_parameters(url, parameters, expected_result):
    result = update_url_parameters(url, parameters)
    assert result == expected_result
