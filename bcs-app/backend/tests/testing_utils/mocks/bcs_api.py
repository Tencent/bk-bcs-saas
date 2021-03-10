# -*- coding: utf-8 -*-
from typing import Dict

from .utils import mockable_function


class StubBcsApiClient:
    """使用假数据的 BCS-Api client 对象"""

    def __init__(self, *args, **kwargs):
        pass

    @mockable_function
    def query_cluster_id(self, env_name: str, project_id: str, cluster_id: str) -> str:
        return {'id': 'faked-bcs-cluster-id-100'}

    @mockable_function
    def get_cluster_credentials(self, env_name: str, bcs_cluster_id: str) -> Dict:
        return {'server_address_path': '/foo', 'user_token': 'foo-token'}
