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

from backend.components.bcs_api import cluster


class StubBcsClusterApiClient:
    """使用假数据的 BCS cluster Api client 对象"""

    def __init__(self, *args, **kwargs):
        pass

    def add_cluster(self, *args, **kwargs) -> Dict:
        return {"code": 0, "data": self.make_add_cluster_resp()}

    def update_cluster(self, cluster_config: cluster.UpdatedClusterConfig) -> Dict:
        return self.make_update_cluster_data()

    def delete_cluster(
        self, cluster_id: str, is_force: bool = False, is_clean_resource=True, only_delete_info=False
    ) -> Dict:
        return {"code": 0, "data": self.make_delete_cluster_resp(cluster_id)}

    def add_nodes(self, cluster_id: str, node_config: cluster.NodeConfig) -> Dict:
        return self.make_add_nodes_data()

    def delete_nodes(self, cluster_id: str, nodes: List[str], delete_mode: str, is_force: bool = False) -> Dict:
        return self.make_delete_nodes_data()

    def query_task(self, task_id: str) -> Dict:
        return self.make_query_task_data(task_id)

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
