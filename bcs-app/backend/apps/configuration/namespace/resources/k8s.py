# -*- coding: utf-8 -*-
import logging

from backend.components.bcs.k8s import K8SClient
from backend.utils.error_codes import error_codes
from backend.utils.errcodes import ErrorCode

logger = logging.getLogger(__name__)


class Namespace:

    @classmethod
    def delete(cls, access_token, project_id, cluster_id, ns_name):
        client = K8SClient(access_token, project_id, cluster_id, env=None)
        resp = client.delete_namespace(ns_name)
        if resp.get('code') == ErrorCode.NoError:
            return
        if 'not found' in resp.get('message'):
            return
        raise error_codes.APIError(f'delete namespace error, name: {ns_name}, {resp.get("message")}')
