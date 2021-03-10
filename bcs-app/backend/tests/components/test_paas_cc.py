# -*- coding: utf-8 -*-
from requests_mock import ANY

from backend.components.base import ComponentAuth
from backend.components.paas_cc import PaaSCCClient


class TestPaaSCCClient:
    def test_get_cluster_simple(self, project_id, cluster_id, requests_mock):
        requests_mock.get(ANY, json={'foo': 'bar'})

        client = PaaSCCClient(ComponentAuth('token'))
        resp = client.get_cluster(project_id, cluster_id)
        assert resp == {'foo': 'bar'}
        assert requests_mock.called
