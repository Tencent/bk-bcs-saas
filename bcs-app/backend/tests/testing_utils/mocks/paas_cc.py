# -*- coding: utf-8 -*-
import uuid
from typing import Dict

from .utils import mockable_function


class StubPaaSCCClient:
    """使用假数据的 PaaSCCClient 对象"""

    def __init__(self, *args, **kwargs):
        pass

    @mockable_function
    def get_cluster(self, project_id: str, cluster_id: str) -> Dict:
        return self.wrap_resp(self.make_cluster_data(project_id, cluster_id))

    @staticmethod
    def wrap_resp(data):
        return {
            'code': 0,
            'data': data,
            'message': '',
            'request_id': uuid.uuid4().hex,
            'result': True,
        }

    @staticmethod
    def make_cluster_data(project_id: str, cluster_id: str):
        _stub_time = '2021-01-01T00:00:00+08:00'
        return {
            'area_id': 1,
            'artifactory': '',
            'capacity_updated_at': _stub_time,
            'cluster_id': cluster_id,
            'cluster_num': 1,
            'config_svr_count': 0,
            'created_at': _stub_time,
            'creator': 'unknown',
            'description': 'cluster description',
            'disabled': False,
            'environment': 'stag',
            'extra_cluster_id': '',
            'ip_resource_total': 0,
            'ip_resource_used': 0,
            'master_count': 0,
            'name': 'test-cluster',
            'need_nat': True,
            'node_count': 1,
            'project_id': project_id,
            'remain_cpu': 10,
            'remain_disk': 0,
            'remain_mem': 10,
            'status': 'normal',
            'total_cpu': 12,
            'total_disk': 0,
            'total_mem': 64,
            'type': 'k8s',
            'updated_at': _stub_time,
        }
