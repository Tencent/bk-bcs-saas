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
from typing import Dict, List

from backend.components import bcs_api

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

    def create_project(self, *args, **kwargs) -> Dict:
        return {"code": 0, "data": self.make_project_data()}

    def query_project(self, project_id) -> Dict:
        return self.make_project_data()

    def update_project(self, *args, **kwargs) -> Dict:
        return {"code": 0, "data": self.make_project_data()}

    def update_project_not_exist(self, *args, **kwargs) -> Dict:
        return {"code": bcs_api.record_not_exist_code}

    def add_cluster(self, *args, **kwargs) -> Dict:
        return {"code": 0, "data": self.make_add_cluster_resp()}

    def update_cluster(self, cluster_config: bcs_api.UpdatedClusterConfig) -> Dict:
        return self.make_update_cluster_data()

    def delete_cluster(
        self, cluster_id: str, is_force: bool = False, is_clean_resource=True, only_delete_info=False
    ) -> Dict:
        return {"code": 0, "data": self.make_delete_cluster_resp(cluster_id)}

    def add_nodes(self, cluster_id: str, node_config: bcs_api.NodeConfig) -> Dict:
        return self.make_add_nodes_data()

    def delete_nodes(self, cluster_id: str, nodes: List[str], delete_mode: str, is_force: bool = False) -> Dict:
        return self.make_delete_nodes_data()

    def query_task(self, task_id: str) -> Dict:
        return self.make_query_task_data(task_id)

    @staticmethod
    def make_project_data() -> Dict:
        return {
            "projectID": "string",
            "name": "string",
            "englishName": "string",
            "creator": "string",
            "updater": "string",
            "projectType": 0,
            "useBKRes": True,
            "description": "string",
            "isOffline": True,
            "kind": "string",
            "businessID": "string",
            "deployType": 0,
            "bgID": "string",
            "bgName": "string",
            "deptID": "string",
            "deptName": "string",
            "centerID": "string",
            "centerName": "string",
            "isSecret": True,
            "credentials": {
                "additionalProp1": {"key": "string", "secret": "string"},
                "additionalProp2": {"key": "string", "secret": "string"},
                "additionalProp3": {"key": "string", "secret": "string"},
            },
            "createTime": "string",
            "updateTime": "string",
        }

    @staticmethod
    def make_add_cluster_resp() -> Dict:
        return {
            "code": 0,
            "message": "string",
            "result": True,
            "data": {
                "clusterID": "string",
                "clusterName": "string",
                "federationClusterID": "string",
                "provider": "string",
                "region": "string",
                "vpcID": "string",
                "projectID": "string",
                "businessID": "string",
                "environment": "string",
                "engineType": "string",
                "isExclusive": True,
                "clusterType": "string",
                "labels": {"additionalProp1": "string", "additionalProp2": "string", "additionalProp3": "string"},
                "creator": "string",
                "createTime": "string",
                "updateTime": "string",
                "bcsAddons": {
                    "additionalProp1": {
                        "system": "string",
                        "link": "string",
                        "params": {
                            "additionalProp1": "string",
                            "additionalProp2": "string",
                            "additionalProp3": "string",
                        },
                    },
                    "additionalProp2": {
                        "system": "string",
                        "link": "string",
                        "params": {
                            "additionalProp1": "string",
                            "additionalProp2": "string",
                            "additionalProp3": "string",
                        },
                    },
                    "additionalProp3": {
                        "system": "string",
                        "link": "string",
                        "params": {
                            "additionalProp1": "string",
                            "additionalProp2": "string",
                            "additionalProp3": "string",
                        },
                    },
                },
                "extraAddons": {
                    "additionalProp1": {
                        "system": "string",
                        "link": "string",
                        "params": {
                            "additionalProp1": "string",
                            "additionalProp2": "string",
                            "additionalProp3": "string",
                        },
                    },
                    "additionalProp2": {
                        "system": "string",
                        "link": "string",
                        "params": {
                            "additionalProp1": "string",
                            "additionalProp2": "string",
                            "additionalProp3": "string",
                        },
                    },
                    "additionalProp3": {
                        "system": "string",
                        "link": "string",
                        "params": {
                            "additionalProp1": "string",
                            "additionalProp2": "string",
                            "additionalProp3": "string",
                        },
                    },
                },
                "systemID": "string",
                "manageType": "string",
                "master": {
                    "additionalProp1": {
                        "nodeID": "string",
                        "innerIP": "string",
                        "instanceType": "string",
                        "CPU": 0,
                        "mem": 0,
                        "GPU": 0,
                        "status": "string",
                        "zoneID": "string",
                        "nodeGroupID": "string",
                        "clusterID": "string",
                    },
                    "additionalProp2": {
                        "nodeID": "string",
                        "innerIP": "string",
                        "instanceType": "string",
                        "CPU": 0,
                        "mem": 0,
                        "GPU": 0,
                        "status": "string",
                        "zoneID": "string",
                        "nodeGroupID": "string",
                        "clusterID": "string",
                    },
                    "additionalProp3": {
                        "nodeID": "string",
                        "innerIP": "string",
                        "instanceType": "string",
                        "CPU": 0,
                        "mem": 0,
                        "GPU": 0,
                        "status": "string",
                        "zoneID": "string",
                        "nodeGroupID": "string",
                        "clusterID": "string",
                    },
                },
                "networkSettings": {
                    "clusterIPv4CIDR": "string",
                    "serviceIPv4CIDR": "string",
                    "maxNodePodNum": "string",
                    "maxServiceNum": "string",
                },
                "clusterBasicSettings": {
                    "OS": "string",
                    "version": "string",
                    "clusterTags": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string",
                    },
                },
                "clusterAdvanceSettings": {
                    "IPVS": True,
                    "containerRuntime": "string",
                    "runtimeVersion": "string",
                    "extraArgs": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string",
                    },
                },
                "nodeSettings": {"dockerGraphPath": "string", "mountTarget": "string"},
                "status": "string",
                "updator": "string",
            },
            "task": {
                "taskID": "string",
                "taskType": "string",
                "status": "string",
                "message": "string",
                "start": "string",
                "end": "string",
                "executionTime": 0,
                "currentStep": "string",
                "stepSequence": ["string"],
                "steps": {
                    "additionalProp1": {
                        "name": "string",
                        "system": "string",
                        "link": "string",
                        "params": {
                            "additionalProp1": "string",
                            "additionalProp2": "string",
                            "additionalProp3": "string",
                        },
                        "retry": 0,
                        "start": "string",
                        "end": "string",
                        "executionTime": 0,
                        "status": "string",
                        "message": "string",
                        "lastUpdate": "string",
                    },
                    "additionalProp2": {
                        "name": "string",
                        "system": "string",
                        "link": "string",
                        "params": {
                            "additionalProp1": "string",
                            "additionalProp2": "string",
                            "additionalProp3": "string",
                        },
                        "retry": 0,
                        "start": "string",
                        "end": "string",
                        "executionTime": 0,
                        "status": "string",
                        "message": "string",
                        "lastUpdate": "string",
                    },
                    "additionalProp3": {
                        "name": "string",
                        "system": "string",
                        "link": "string",
                        "params": {
                            "additionalProp1": "string",
                            "additionalProp2": "string",
                            "additionalProp3": "string",
                        },
                        "retry": 0,
                        "start": "string",
                        "end": "string",
                        "executionTime": 0,
                        "status": "string",
                        "message": "string",
                        "lastUpdate": "string",
                    },
                },
                "clusterID": "string",
                "projectID": "string",
                "creator": "string",
                "lastUpdate": "string",
                "updator": "string",
                "forceTerminate": True,
            },
        }

    @staticmethod
    def make_update_cluster_data() -> Dict:
        {
            "clusterID": "string",
            "clusterName": "string",
            "federationClusterID": "string",
            "provider": "string",
            "region": "string",
            "vpcID": "string",
            "projectID": "string",
            "businessID": "string",
            "environment": "string",
            "engineType": "string",
            "isExclusive": True,
            "clusterType": "string",
            "labels": {"additionalProp1": "string", "additionalProp2": "string", "additionalProp3": "string"},
            "creator": "string",
            "createTime": "string",
            "updateTime": "string",
            "bcsAddons": {
                "additionalProp1": {
                    "system": "string",
                    "link": "string",
                    "params": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string",
                    },
                },
                "additionalProp2": {
                    "system": "string",
                    "link": "string",
                    "params": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string",
                    },
                },
                "additionalProp3": {
                    "system": "string",
                    "link": "string",
                    "params": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string",
                    },
                },
            },
            "extraAddons": {
                "additionalProp1": {
                    "system": "string",
                    "link": "string",
                    "params": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string",
                    },
                },
                "additionalProp2": {
                    "system": "string",
                    "link": "string",
                    "params": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string",
                    },
                },
                "additionalProp3": {
                    "system": "string",
                    "link": "string",
                    "params": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string",
                    },
                },
            },
            "systemID": "string",
            "manageType": "string",
            "master": {
                "additionalProp1": {
                    "nodeID": "string",
                    "innerIP": "string",
                    "instanceType": "string",
                    "CPU": 0,
                    "mem": 0,
                    "GPU": 0,
                    "status": "string",
                    "zoneID": "string",
                    "nodeGroupID": "string",
                    "clusterID": "string",
                },
                "additionalProp2": {
                    "nodeID": "string",
                    "innerIP": "string",
                    "instanceType": "string",
                    "CPU": 0,
                    "mem": 0,
                    "GPU": 0,
                    "status": "string",
                    "zoneID": "string",
                    "nodeGroupID": "string",
                    "clusterID": "string",
                },
                "additionalProp3": {
                    "nodeID": "string",
                    "innerIP": "string",
                    "instanceType": "string",
                    "CPU": 0,
                    "mem": 0,
                    "GPU": 0,
                    "status": "string",
                    "zoneID": "string",
                    "nodeGroupID": "string",
                    "clusterID": "string",
                },
            },
            "networkSettings": {
                "clusterIPv4CIDR": "string",
                "serviceIPv4CIDR": "string",
                "maxNodePodNum": "string",
                "maxServiceNum": "string",
            },
            "clusterBasicSettings": {
                "OS": "string",
                "version": "string",
                "clusterTags": {
                    "additionalProp1": "string",
                    "additionalProp2": "string",
                    "additionalProp3": "string",
                },
            },
            "clusterAdvanceSettings": {
                "IPVS": True,
                "containerRuntime": "string",
                "runtimeVersion": "string",
                "extraArgs": {
                    "additionalProp1": "string",
                    "additionalProp2": "string",
                    "additionalProp3": "string",
                },
            },
            "nodeSettings": {"dockerGraphPath": "string", "mountTarget": "string"},
            "status": "string",
            "updator": "string",
        }

    @staticmethod
    def make_delete_cluster_resp(cluster_id: str) -> Dict:
        return {
            "code": 0,
            "message": "string",
            "result": True,
            "data": {
                "clusterID": cluster_id,
                "clusterName": "string",
                "federationClusterID": "string",
                "provider": "string",
                "region": "string",
                "vpcID": "string",
                "projectID": "string",
                "businessID": "string",
                "environment": "string",
                "engineType": "string",
                "isExclusive": True,
                "clusterType": "string",
                "labels": {"additionalProp1": "string", "additionalProp2": "string", "additionalProp3": "string"},
                "creator": "string",
                "createTime": "string",
                "updateTime": "string",
                "bcsAddons": {
                    "additionalProp1": {
                        "system": "string",
                        "link": "string",
                        "params": {
                            "additionalProp1": "string",
                            "additionalProp2": "string",
                            "additionalProp3": "string",
                        },
                    },
                    "additionalProp2": {
                        "system": "string",
                        "link": "string",
                        "params": {
                            "additionalProp1": "string",
                            "additionalProp2": "string",
                            "additionalProp3": "string",
                        },
                    },
                    "additionalProp3": {
                        "system": "string",
                        "link": "string",
                        "params": {
                            "additionalProp1": "string",
                            "additionalProp2": "string",
                            "additionalProp3": "string",
                        },
                    },
                },
                "extraAddons": {
                    "additionalProp1": {
                        "system": "string",
                        "link": "string",
                        "params": {
                            "additionalProp1": "string",
                            "additionalProp2": "string",
                            "additionalProp3": "string",
                        },
                    },
                    "additionalProp2": {
                        "system": "string",
                        "link": "string",
                        "params": {
                            "additionalProp1": "string",
                            "additionalProp2": "string",
                            "additionalProp3": "string",
                        },
                    },
                    "additionalProp3": {
                        "system": "string",
                        "link": "string",
                        "params": {
                            "additionalProp1": "string",
                            "additionalProp2": "string",
                            "additionalProp3": "string",
                        },
                    },
                },
                "systemID": "string",
                "manageType": "string",
                "master": {
                    "additionalProp1": {
                        "nodeID": "string",
                        "innerIP": "string",
                        "instanceType": "string",
                        "CPU": 0,
                        "mem": 0,
                        "GPU": 0,
                        "status": "string",
                        "zoneID": "string",
                        "nodeGroupID": "string",
                        "clusterID": "string",
                    },
                    "additionalProp2": {
                        "nodeID": "string",
                        "innerIP": "string",
                        "instanceType": "string",
                        "CPU": 0,
                        "mem": 0,
                        "GPU": 0,
                        "status": "string",
                        "zoneID": "string",
                        "nodeGroupID": "string",
                        "clusterID": "string",
                    },
                    "additionalProp3": {
                        "nodeID": "string",
                        "innerIP": "string",
                        "instanceType": "string",
                        "CPU": 0,
                        "mem": 0,
                        "GPU": 0,
                        "status": "string",
                        "zoneID": "string",
                        "nodeGroupID": "string",
                        "clusterID": "string",
                    },
                },
                "networkSettings": {
                    "clusterIPv4CIDR": "string",
                    "serviceIPv4CIDR": "string",
                    "maxNodePodNum": "string",
                    "maxServiceNum": "string",
                },
                "clusterBasicSettings": {
                    "OS": "string",
                    "version": "string",
                    "clusterTags": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string",
                    },
                },
                "clusterAdvanceSettings": {
                    "IPVS": True,
                    "containerRuntime": "string",
                    "runtimeVersion": "string",
                    "extraArgs": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string",
                    },
                },
                "nodeSettings": {"dockerGraphPath": "string", "mountTarget": "string"},
                "status": "string",
                "updator": "string",
            },
            "tasks": [
                {
                    "taskID": "string",
                    "taskType": "string",
                    "status": "string",
                    "message": "string",
                    "start": "string",
                    "end": "string",
                    "executionTime": 0,
                    "currentStep": "string",
                    "stepSequence": ["string"],
                    "steps": {
                        "additionalProp1": {
                            "name": "string",
                            "system": "string",
                            "link": "string",
                            "params": {
                                "additionalProp1": "string",
                                "additionalProp2": "string",
                                "additionalProp3": "string",
                            },
                            "retry": 0,
                            "start": "string",
                            "end": "string",
                            "executionTime": 0,
                            "status": "string",
                            "message": "string",
                            "lastUpdate": "string",
                        },
                        "additionalProp2": {
                            "name": "string",
                            "system": "string",
                            "link": "string",
                            "params": {
                                "additionalProp1": "string",
                                "additionalProp2": "string",
                                "additionalProp3": "string",
                            },
                            "retry": 0,
                            "start": "string",
                            "end": "string",
                            "executionTime": 0,
                            "status": "string",
                            "message": "string",
                            "lastUpdate": "string",
                        },
                        "additionalProp3": {
                            "name": "string",
                            "system": "string",
                            "link": "string",
                            "params": {
                                "additionalProp1": "string",
                                "additionalProp2": "string",
                                "additionalProp3": "string",
                            },
                            "retry": 0,
                            "start": "string",
                            "end": "string",
                            "executionTime": 0,
                            "status": "string",
                            "message": "string",
                            "lastUpdate": "string",
                        },
                    },
                    "clusterID": "string",
                    "projectID": "string",
                    "creator": "string",
                    "lastUpdate": "string",
                    "updator": "string",
                    "forceTerminate": True,
                }
            ],
        }

    @staticmethod
    def make_add_nodes_data() -> Dict:
        return {
            "taskID": "string",
            "taskType": "string",
            "status": "string",
            "message": "string",
            "start": "string",
            "end": "string",
            "executionTime": 0,
            "currentStep": "string",
            "stepSequence": ["string"],
            "steps": {
                "additionalProp1": {
                    "name": "string",
                    "system": "string",
                    "link": "string",
                    "params": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string",
                    },
                    "retry": 0,
                    "start": "string",
                    "end": "string",
                    "executionTime": 0,
                    "status": "string",
                    "message": "string",
                    "lastUpdate": "string",
                },
                "additionalProp2": {
                    "name": "string",
                    "system": "string",
                    "link": "string",
                    "params": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string",
                    },
                    "retry": 0,
                    "start": "string",
                    "end": "string",
                    "executionTime": 0,
                    "status": "string",
                    "message": "string",
                    "lastUpdate": "string",
                },
                "additionalProp3": {
                    "name": "string",
                    "system": "string",
                    "link": "string",
                    "params": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string",
                    },
                    "retry": 0,
                    "start": "string",
                    "end": "string",
                    "executionTime": 0,
                    "status": "string",
                    "message": "string",
                    "lastUpdate": "string",
                },
            },
            "clusterID": "string",
            "projectID": "string",
            "creator": "string",
            "lastUpdate": "string",
            "updator": "string",
            "forceTerminate": True,
        }

    @staticmethod
    def make_delete_nodes_data() -> Dict:
        return {
            "taskID": "string",
            "taskType": "string",
            "status": "string",
            "message": "string",
            "start": "string",
            "end": "string",
            "executionTime": 0,
            "currentStep": "string",
            "stepSequence": ["string"],
            "steps": {
                "additionalProp1": {
                    "name": "string",
                    "system": "string",
                    "link": "string",
                    "params": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string",
                    },
                    "retry": 0,
                    "start": "string",
                    "end": "string",
                    "executionTime": 0,
                    "status": "string",
                    "message": "string",
                    "lastUpdate": "string",
                },
                "additionalProp2": {
                    "name": "string",
                    "system": "string",
                    "link": "string",
                    "params": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string",
                    },
                    "retry": 0,
                    "start": "string",
                    "end": "string",
                    "executionTime": 0,
                    "status": "string",
                    "message": "string",
                    "lastUpdate": "string",
                },
                "additionalProp3": {
                    "name": "string",
                    "system": "string",
                    "link": "string",
                    "params": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string",
                    },
                    "retry": 0,
                    "start": "string",
                    "end": "string",
                    "executionTime": 0,
                    "status": "string",
                    "message": "string",
                    "lastUpdate": "string",
                },
            },
            "clusterID": "string",
            "projectID": "string",
            "creator": "string",
            "lastUpdate": "string",
            "updator": "string",
            "forceTerminate": True,
        }

    @staticmethod
    def make_query_task_data(task_id: str) -> Dict:
        return {
            "taskID": task_id,
            "taskType": "string",
            "status": "string",
            "message": "string",
            "start": "string",
            "end": "string",
            "executionTime": 0,
            "currentStep": "string",
            "stepSequence": ["string"],
            "steps": {
                "additionalProp1": {
                    "name": "string",
                    "system": "string",
                    "link": "string",
                    "params": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string",
                    },
                    "retry": 0,
                    "start": "string",
                    "end": "string",
                    "executionTime": 0,
                    "status": "string",
                    "message": "string",
                    "lastUpdate": "string",
                },
                "additionalProp2": {
                    "name": "string",
                    "system": "string",
                    "link": "string",
                    "params": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string",
                    },
                    "retry": 0,
                    "start": "string",
                    "end": "string",
                    "executionTime": 0,
                    "status": "string",
                    "message": "string",
                    "lastUpdate": "string",
                },
                "additionalProp3": {
                    "name": "string",
                    "system": "string",
                    "link": "string",
                    "params": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string",
                    },
                    "retry": 0,
                    "start": "string",
                    "end": "string",
                    "executionTime": 0,
                    "status": "string",
                    "message": "string",
                    "lastUpdate": "string",
                },
            },
            "clusterID": "string",
            "projectID": "string",
            "creator": "string",
            "lastUpdate": "string",
            "updator": "string",
            "forceTerminate": True,
        }
