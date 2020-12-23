# -*- coding: utf-8 -*-
import pytest
from urllib3.response import HTTPResponse
from kubernetes.client import V1Namespace, V1ObjectMeta
from kubernetes.client.rest import ApiException, RESTResponse

from backend.components.bcs.resources.api_response import response
from backend.tests.testing_utils.base import dict_is_subequal


@pytest.mark.parametrize(
    'result,format_data,expected_resp',
    [
        # Kubernetes object response
        (V1Namespace(metadata=V1ObjectMeta(name='foo')), True, {'result': True, 'code': 0, 'message': 'success'}),
        # Normal data type
        ({'foo': 'bar'}, False, {'code': 0, 'data': {'foo': 'bar'}, 'message': 'success', 'result': True}),
        # Raises APIException error
        (
            ApiException(status=404, http_resp=RESTResponse(HTTPResponse(status=404))),
            True,
            {'code': 4001, 'message': 'request bcs api error, (404)\nReason: None\n', 'result': False},
        ),
        (
            ApiException(status=400, http_resp=RESTResponse(HTTPResponse(status=404, body='{"message": "foobar"}'))),
            True,
            {'code': 4001, 'message': 'foobar', 'result': False},
        ),
        # Raises other exceptions
        (ValueError('unknown error'), True, {'code': 4001, 'message': 'unknown error', 'result': False}),
    ],
)
def test_response(result, format_data, expected_resp):
    def _decorated():
        if isinstance(result, Exception):
            raise result
        else:
            return result

    resp = response(format_data=format_data)(_decorated)()
    assert dict_is_subequal(expected_resp, resp)
