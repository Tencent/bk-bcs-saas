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
from django.conf import settings

# 镜像路径前缀
if settings.DEPOT_PREFIX:
    image_path_prefix = f'{settings.DEPOT_PREFIX}/public'
else:
    image_path_prefix = 'public/bcs'
image_prefix = f'{settings.DEVOPS_ARTIFACTORY_HOST}/{image_path_prefix}'

# service 中 app_weight 需要修改为 app_id
MESOS_TEMPLATE = {
    "code": 0,
    "message": "OK",
    "data": {
        "deployment": [
            {
                "id": 3,
                "app_id": "1520395319",
                "name": "deploy-nginx1",
                "desc": "rumpetroll deployment",
                "config": {
                    "strategy": {
                        "type": "RollingUpdate",
                        "rollingupdate": {
                            "maxUnavilable": 1,
                            "maxSurge": 1,
                            "upgradeDuration": 30,
                            "rollingOrder": "CreateFirst",
                        },
                    }
                },
            }
        ],
        "service": [
            {
                "id": 53,
                "name": "rum-redis-svc",
                "app_id": {"1520394355": 100},
                "config": {
                    "webCache": {
                        "link_app": ["1520394355"],
                        "link_app_weight": [{"id": "1520394355", "name": "rum-test", "weight": 100}],
                        "labelListCache": [{"key": "", "value": ""}],
                    },
                    "isLinkLoadBalance": False,
                    "kind": "service",
                    "metadata": {"name": "rum-redis-svc", "labels": {}},
                    "spec": {
                        "type": "None",
                        "clusterIP": [],
                        "ports": [
                            {
                                "name": "",
                                "protocol": "http",
                                "targetPort": "",
                                "domainName": "",
                                "path": "",
                                "servicePort": "",
                            }
                        ],
                    },
                },
            },
            {
                "id": 150,
                "name": "rum-rum-svc",
                "app_id": {"1520395319": 100},
                "config": {
                    "webCache": {
                        "link_app": ["1520395319"],
                        "link_app_weight": [{"id": "1520395319", "name": "rum-rumpetroll", "weight": 100}],
                        "labelListCache": [{"key": "", "value": ""}],
                    },
                    "isLinkLoadBalance": False,
                    "kind": "service",
                    "metadata": {"name": "rum-rum-svc", "labels": {}},
                    "spec": {
                        "type": "None",
                        "clusterIP": [],
                        "ports": [
                            {
                                "name": "rum-port",
                                "protocol": "HTTP",
                                "targetPort": 20001,
                                "domainName": "bcs-rumpetroll.wsd.bking.com",
                                "path": "",
                                "servicePort": 80,
                                "id": 1520394369864,
                            }
                        ],
                    },
                },
            },
        ],
        "application": [
            {
                "id": "857",
                "app_id": "1520395319",
                "desc": "rumpetroll service",
                "config": {
                    "webCache": {
                        "remarkListCache": [{"key": "", "value": ""}],
                        "labelListCache": [{"key": "", "value": ""}],
                        "isMetric": True,
                        "metricIdList": [],
                        "logLabelListCache": [{"key": "", "value": ""}],
                    },
                    "kind": "application",
                    "restartPolicy": {"policy": "Always", "interval": 5, "backoff": 10, "maxtimes": 0},
                    "killPolicy": {"gracePeriod": 10},
                    "metricPolicy": {"isUsed": False, "list": []},
                    "constraint": {
                        "intersectionItem": [
                            {
                                "unionData": [
                                    {
                                        "name": "hostname",
                                        "operate": "CLUSTER",
                                        "type": 4,
                                        "arg_value": "",
                                        "set": {"item": []},
                                    }
                                ]
                            }
                        ]
                    },
                    "metadata": {"annotations": {}, "labels": {}, "name": "rum-rumpetroll"},
                    "spec": {
                        "instance": 2,
                        "template": {
                            "metadata": {},
                            "spec": {
                                "containers": [
                                    {
                                        "name": "rumpetroll",
                                        "desc": "rumpetroll container",
                                        "command": "",
                                        "args_text": "",
                                        "args": [],
                                        "parameters": [],
                                        "logPathList": [],
                                        "parameter_list": [{"key": "", "value": ""}],
                                        "type": "MESOS",
                                        "env_list": [
                                            {
                                                "type": "custom",
                                                "key": "REDIS_HOST",
                                                "value": "rum-redis-svc.{{SYS_NAMESPACE}}",
                                            },
                                            {"type": "custom", "key": "REDIS_PORT", "value": "31181"},
                                            {"type": "custom", "key": "HOST", "value": "0.0.0.0"},
                                            {"type": "custom", "key": "MAX_CLIENT", "value": "20"},
                                        ],
                                        # NOTE: imageName仅供前端匹配镜像使用，格式是镜像列表中name:value
                                        "imageName": f"{image_path_prefix}/mesos/rumpetroll:{image_path_prefix}/mesos/rumpetroll",  # noqa
                                        "imageVersion": "3.1",
                                        "image": f"{image_prefix}/mesos/rumpetroll:3.1",
                                        "imagePullPolicy": "Always",
                                        "privileged": False,
                                        "ports": [
                                            {
                                                "id": 1520394369864,
                                                "containerPort": 80,
                                                "hostPort": 0,
                                                "name": "rum-port",
                                                "protocol": "HTTP",
                                                "isLink": "端口在 Service[rum-rum-svc] 中已经被关联，不能修改协议！",
                                                "isDisabled": False,
                                            }
                                        ],
                                        "healthChecks": [
                                            {
                                                "type": "",
                                                "delaySeconds": 10,
                                                "intervalSeconds": 60,
                                                "timeoutSeconds": 20,
                                                "consecutiveFailures": 3,
                                                "gracePeriodSeconds": 300,
                                                "command": {"portName": "", "value": ""},
                                                "http": {
                                                    "port": "",
                                                    "portName": "",
                                                    "scheme": "http",
                                                    "path": "",
                                                    "headers": {},
                                                },
                                                "tcp": {"port": "", "portName": ""},
                                            }
                                        ],
                                        "resources": {
                                            "requests": {"cpu": 1, "memory": 100},
                                            "limits": {"cpu": '', "memory": ''},
                                        },
                                        "volumes": [],
                                        "logListCache": [{"value": ""}],
                                    }
                                ],
                                "networkMode": "HOST",
                                "networkType": "cnm",
                                "custom_value": "",
                            },
                        },
                    },
                    "customLogLabel": {},
                    "monitorLevel": "general",
                },
                "name": "rum-rumpetroll",
            },
            {
                "id": "860",
                "app_id": "1520394355",
                "desc": "redis service for rumpetroll",
                "config": {
                    "webCache": {
                        "remarkListCache": [{"key": "", "value": ""}],
                        "labelListCache": [{"key": "", "value": ""}],
                        "isMetric": False,
                        "metricIdList": [],
                        "logLabelListCache": [{"key": "", "value": ""}],
                    },
                    "kind": "application",
                    "restartPolicy": {"policy": "Always", "interval": 5, "backoff": 10, "maxtimes": 0},
                    "killPolicy": {"gracePeriod": 10},
                    "metricPolicy": {"isUsed": False, "list": []},
                    "constraint": {
                        "intersectionItem": [
                            {
                                "unionData": [
                                    {
                                        "name": "hostname",
                                        "operate": "CLUSTER",
                                        "type": 4,
                                        "arg_value": "",
                                        "set": {"item": []},
                                    }
                                ]
                            }
                        ]
                    },
                    "metadata": {"annotations": {}, "labels": {}, "name": "rum-redis"},
                    "spec": {
                        "instance": 1,
                        "template": {
                            "metadata": {},
                            "spec": {
                                "containers": [
                                    {
                                        "name": "rum-redis",
                                        "desc": "redis container",
                                        "command": "",
                                        "args_text": "",
                                        "args": [],
                                        "parameters": [],
                                        "logPathList": [],
                                        "parameter_list": [{"key": "", "value": ""}],
                                        "type": "MESOS",
                                        "env_list": [{"type": "custom", "key": "", "value": ""}],
                                        # NOTE: imageName仅供前端匹配镜像使用，格式是镜像列表中name:value
                                        "imageName": f"{image_path_prefix}/mesos/rumpetrol-redis:{image_path_prefix}/mesos/rumpetrol-redis",  # noqa
                                        "imageVersion": "latest",
                                        "image": f"{image_prefix}/mesos/rumpetrol-redis:latest",
                                        "imagePullPolicy": "Always",
                                        "privileged": False,
                                        "ports": [
                                            {
                                                "id": 1520394123208,
                                                "containerPort": 6379,
                                                "hostPort": 31181,
                                                "name": "redis-port",
                                                "protocol": "HTTP",
                                                "isLink": "",
                                                "isDisabled": False,
                                            }
                                        ],
                                        "healthChecks": [
                                            {
                                                "type": "",
                                                "delaySeconds": 10,
                                                "intervalSeconds": 60,
                                                "timeoutSeconds": 20,
                                                "consecutiveFailures": 3,
                                                "gracePeriodSeconds": 300,
                                                "command": {"portName": "", "value": ""},
                                                "http": {
                                                    "port": "",
                                                    "portName": "",
                                                    "scheme": "http",
                                                    "path": "",
                                                    "headers": {},
                                                },
                                                "tcp": {"port": "", "portName": ""},
                                            }
                                        ],
                                        "resources": {
                                            "requests": {"cpu": 1, "memory": 100},
                                            "limits": {"cpu": '', "memory": ''},
                                        },
                                        "volumes": [],
                                        "logListCache": [{"value": ""}],
                                    }
                                ],
                                "networkMode": "BRIDGE",
                                "networkType": "cnm",
                                "custom_value": "",
                            },
                        },
                    },
                    "customLogLabel": {},
                    "monitorLevel": "general",
                },
                "name": "rum-redis",
            },
        ],
    },
}
