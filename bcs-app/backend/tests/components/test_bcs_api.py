# -*- coding: utf-8 -*-
import pytest
from requests_mock import ANY

from backend.components.base import ComponentAuth
from backend.components.bcs_api import BcsApiClient

BCS_AUTH_TOKEN = 'example-auth-token'


@pytest.fixture(autouse=True)
def setup_token(settings):
    settings.BCS_AUTH_TOKEN = BCS_AUTH_TOKEN


class TestBcsApiClient:
    def test_get_cluster_simple(self, project_id, cluster_id, requests_mock):
        requests_mock.get(ANY, json={'id': 'foo-id'})

        client = BcsApiClient(ComponentAuth('fake_token'))
        result = client.query_cluster_id('stag', project_id, cluster_id)
        assert result == 'foo-id'

        req_history = requests_mock.request_history[0]
        # Assert token was in request headers and access_token was in query string
        assert req_history.headers.get('Authorization') == BCS_AUTH_TOKEN
        assert 'access_token=fake_token' in req_history.url

    def test_get_cluster_credentials(self, requests_mock):
        requests_mock.get(ANY, json={'name': 'foo'})

        client = BcsApiClient(ComponentAuth('fake_token'))
        resp = client.get_cluster_credentials('stag', 'fake-bcs-cluster-foo')
        assert resp == {'name': 'foo'}
