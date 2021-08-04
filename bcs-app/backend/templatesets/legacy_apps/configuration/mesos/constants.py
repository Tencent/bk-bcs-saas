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
from ..constants import FILE_DIR_PATTERN, KEY_NAME_PATTERN, MRESOURCE_NAMES, NUM_VAR_PATTERN

# 验证变量的情况，并且支持BCS变量标识 $
RES_NAME_PATTERN = "^[a-zA-Z{\$]{1}[a-zA-Z0-9-{}_\$]{0,254}$"

# 挂载卷名称
VOL_NAME_PATTERN = "^[a-zA-Z{\$]{1}[a-zA-Z0-9-_{}\$]{0,254}$"

APPLICATION_SCHEMA = {
    "type": "object",
    "required": ["metadata", "restartPolicy", "killPolicy", "spec"],
    "properties": {
        "metadata": {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string", "pattern": RES_NAME_PATTERN}},
        },
        "restartPolicy": {
            "type": "object",
            "required": ["policy", "interval", "backoff", "maxtimes"],
            "properties": {
                "policy": {"type": "string", "enum": ["Never", "Always", "OnFailure"]},
                "interval": {
                    "oneOf": [{"type": "string", "pattern": NUM_VAR_PATTERN}, {"type": "number", "minimum": 0}]
                },
                "backoff": {
                    "oneOf": [{"type": "string", "pattern": NUM_VAR_PATTERN}, {"type": "number", "minimum": 0}]
                },
                "maxtimes": {
                    "oneOf": [{"type": "string", "pattern": NUM_VAR_PATTERN}, {"type": "number", "minimum": 0}]
                },
            },
        },
        "killPolicy": {
            "type": "object",
            "required": ["gracePeriod"],
            "properties": {
                "gracePeriod": {
                    "oneOf": [{"type": "string", "pattern": NUM_VAR_PATTERN}, {"type": "number", "minimum": 0}]
                },
            },
        },
        "constraint": {
            "type": "object",
            "required": ["intersectionItem"],
            "properties": {
                "intersectionItem": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["unionData"],
                        "properties": {
                            "unionData": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["name", "operate"],
                                    "properties": {
                                        "name": {"type": "string", "minLength": 1},
                                        "operate": {
                                            "type": "string",
                                            "enum": [
                                                "UNIQUE",
                                                "MAXPER",
                                                "CLUSTER",
                                                "GROUPBY",
                                                "LIKE",
                                                "UNLIKE",
                                                "GREATER",
                                                "TOLERATION",
                                            ],
                                        },
                                        "type": {"type": "number", "minimum": 1, "maximum": 4},
                                    },
                                },
                            }
                        },
                    },
                }
            },
        },
        "spec": {
            "type": "object",
            "required": ["instance", "template"],
            "properties": {
                "instance": {
                    "oneOf": [{"type": "string", "pattern": NUM_VAR_PATTERN}, {"type": "number", "minimum": 0}]
                },
                "template": {
                    "type": "object",
                    "required": ["spec"],
                    "properties": {
                        "spec": {
                            "type": "object",
                            "required": ["networkMode", "networkType", "containers"],
                            "properties": {
                                "networkMode": {
                                    "type": "string",
                                    "enum": ["CUSTOM", "BRIDGE", "HOST", "USER", "NONE"],
                                },
                                "networkType": {"type": "string", "enum": ["cni", "cnm"]},
                                "containers": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "required": ["type", "image", "imagePullPolicy", "privileged", "resources"],
                                        "properties": {
                                            "type": {"type": "string", "enum": ["MESOS"]},
                                            "image": {"type": "string", "minLength": 1},
                                            "imagePullPolicy": {"type": "string", "enum": ["Always", "IfNotPresent"]},
                                            "privileged": {"type": "boolean"},
                                            "resources": {
                                                "type": "object",
                                                "required": ["limits", "requests"],
                                                "properties": {
                                                    "limits": {
                                                        "type": "object",
                                                        "required": ["cpu", "memory"],
                                                        "properties": {
                                                            "cpu": {
                                                                "oneOf": [
                                                                    {"type": "string", "pattern": "^$"},
                                                                    {"type": "string", "pattern": NUM_VAR_PATTERN},
                                                                    {"type": "number", "minimum": 0},
                                                                ]
                                                            },
                                                            "memory": {
                                                                "oneOf": [
                                                                    {"type": "string", "pattern": "^$"},
                                                                    {"type": "string", "pattern": NUM_VAR_PATTERN},
                                                                    {"type": "number", "minimum": 0},
                                                                ]
                                                            },
                                                        },
                                                    },
                                                    "requests": {
                                                        "type": "object",
                                                        "required": ["cpu", "memory"],
                                                        "properties": {
                                                            "cpu": {
                                                                "oneOf": [
                                                                    {"type": "string", "pattern": "^$"},
                                                                    {"type": "string", "pattern": NUM_VAR_PATTERN},
                                                                    {"type": "number", "minimum": 0},
                                                                ]
                                                            },
                                                            "memory": {
                                                                "oneOf": [
                                                                    {"type": "string", "pattern": "^$"},
                                                                    {"type": "string", "pattern": NUM_VAR_PATTERN},
                                                                    {"type": "number", "minimum": 0},
                                                                ]
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                            "volumes": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "required": ["name", "volume"],
                                                    "properties": {
                                                        "name": {"type": "string", "pattern": VOL_NAME_PATTERN},
                                                        "volume": {
                                                            "type": "object",
                                                            "required": ["hostPath", "mountPath"],
                                                            "properties": {
                                                                "hostPath": {
                                                                    "oneOf": [
                                                                        {"type": "string", "pattern": "^$"},
                                                                        {
                                                                            "type": "string",
                                                                            "pattern": FILE_DIR_PATTERN,
                                                                        },
                                                                    ]
                                                                },
                                                                "mountPath": {
                                                                    "type": "string",
                                                                    "pattern": FILE_DIR_PATTERN,
                                                                },
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                            "healthChecks": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "required": [
                                                        "type",
                                                        "delaySeconds",
                                                        "intervalSeconds",
                                                        "timeoutSeconds",
                                                        "consecutiveFailures",
                                                        "gracePeriodSeconds",
                                                    ],
                                                    "properties": {
                                                        "type": {
                                                            "type": "string",
                                                            "enum": [
                                                                "",
                                                                "HTTP",
                                                                "TCP",
                                                                "COMMAND",
                                                                "REMOTE_HTTP",
                                                                "REMOTE_TCP",
                                                            ],
                                                        },
                                                        "delaySeconds": {
                                                            "oneOf": [
                                                                {"type": "string", "pattern": NUM_VAR_PATTERN},
                                                                {"type": "number", "minimum": 0},
                                                            ]
                                                        },
                                                        "intervalSeconds": {
                                                            "oneOf": [
                                                                {"type": "string", "pattern": NUM_VAR_PATTERN},
                                                                {"type": "number", "minimum": 0},
                                                            ]
                                                        },
                                                        "timeoutSeconds": {
                                                            "oneOf": [
                                                                {"type": "string", "pattern": NUM_VAR_PATTERN},
                                                                {"type": "number", "minimum": 0},
                                                            ]
                                                        },
                                                        "consecutiveFailures": {
                                                            "oneOf": [
                                                                {"type": "string", "pattern": NUM_VAR_PATTERN},
                                                                {"type": "number", "minimum": 0},
                                                            ]
                                                        },
                                                        "gracePeriodSeconds": {
                                                            "oneOf": [
                                                                {"type": "string", "pattern": NUM_VAR_PATTERN},
                                                                {"type": "number", "minimum": 0},
                                                            ]
                                                        },
                                                        "command": {
                                                            "type": "object",
                                                            "properties": {"value": {"type": "string"}},
                                                        },
                                                        "tcp": {
                                                            "type": "object",
                                                            "properties": {
                                                                "port": {
                                                                    "oneOf": [{"type": "number"}, {"type": "string"}]
                                                                },
                                                                "portName": {
                                                                    "oneOf": [
                                                                        {"type": "string", "pattern": "^$"},
                                                                        {
                                                                            "type": "string",
                                                                            "pattern": RES_NAME_PATTERN,
                                                                        },
                                                                    ]
                                                                },
                                                            },
                                                        },
                                                        "http": {
                                                            "type": "object",
                                                            "properties": {
                                                                "port": {
                                                                    "oneOf": [{"type": "number"}, {"type": "string"}]
                                                                },
                                                                "portName": {
                                                                    "oneOf": [
                                                                        {"type": "string", "pattern": "^$"},
                                                                        {
                                                                            "type": "string",
                                                                            "pattern": RES_NAME_PATTERN,
                                                                        },
                                                                    ]
                                                                },
                                                                "scheme": {"type": "string"},
                                                                "path": {"type": "string"},
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                            "ports": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "required": ["protocol", "name", "containerPort", "hostPort"],
                                                    "properties": {
                                                        "protocol": {
                                                            "type": "string",
                                                            "enum": ["HTTP", "TCP", "UDP", ""],
                                                        },
                                                        "name": {
                                                            "oneOf": [
                                                                {"type": "string", "pattern": "^$"},
                                                                {"type": "string", "pattern": RES_NAME_PATTERN},
                                                            ]
                                                        },
                                                        "hostPort": {
                                                            "oneOf": [
                                                                {"type": "string", "pattern": "^$"},
                                                                {"type": "string", "pattern": NUM_VAR_PATTERN},
                                                                {"type": "number", "minimum": -1, "maximum": 65535},
                                                            ]
                                                        },
                                                        "containerPort": {
                                                            "oneOf": [
                                                                {"type": "string", "pattern": "^$"},
                                                                {"type": "string", "pattern": NUM_VAR_PATTERN},
                                                                {"type": "number", "minimum": 1, "maximum": 65535},
                                                            ]
                                                        },
                                                    },
                                                },
                                            },
                                            "command": {"type": "string"},
                                            "args": {"type": "array"},
                                            "env": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "required": ["name", "value"],
                                                    "properties": {
                                                        "name": {"type": "string", "minLength": 1},
                                                        "value": {"type": "string"},
                                                    },
                                                },
                                            },
                                            "parameters": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "required": ["key", "value"],
                                                    "properties": {
                                                        "key": {"type": "string", "minLength": 1},
                                                        "value": {"type": "string"},
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        }
                    },
                },
            },
        },
    },
}

DEPLOYMENT_SCHEMA = {
    "type": "object",
    "required": ["strategy"],
    "properties": {
        "strategy": {
            "type": "object",
            "required": ["type", "rollingupdate"],
            "properties": {
                "type": {"type": "string", "enum": ["RollingUpdate"]},
                "rollingupdate": {
                    "type": "object",
                    "required": ["maxUnavilable", "maxSurge", "upgradeDuration", "rollingOrder"],
                    "properties": {
                        "maxUnavilable": {
                            "oneOf": [
                                {"type": "string", "pattern": NUM_VAR_PATTERN},
                                {"type": "number", "minimum": 0},
                            ]
                        },
                        "maxSurge": {
                            "oneOf": [
                                {"type": "string", "pattern": NUM_VAR_PATTERN},
                                {"type": "number", "minimum": 0},
                            ]
                        },
                        "upgradeDuration": {
                            "oneOf": [
                                {"type": "string", "pattern": NUM_VAR_PATTERN},
                                {"type": "number", "minimum": 0},
                            ]
                        },
                        "rollingOrder": {"type": "string", "enum": ["CreateFirst", "DeleteFirst"]},
                    },
                },
            },
        }
    },
}

SERVICE_SCHEMA = {
    "type": "object",
    "required": ["metadata", "spec"],
    "properties": {
        "metadata": {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string", "pattern": RES_NAME_PATTERN},
                "lb_labels": {
                    "type": "object",
                    "required": ["BCSBALANCE"],
                    "properties": {"BCSBALANCE": {"type": "string", "enum": ["source", "roundrobin", "leastconn"]}},
                },
            },
        },
        "spec": {
            "type": "object",
            "required": ["type", "clusterIP", "ports"],
            "properties": {
                "type": {"type": "string", "enum": ["ClusterIP", "None"]},
                "clusterIP": {"oneOf": [{"type": "string"}, {"type": "array", "items": {"type": "string"}}]},
                "ports": {
                    "type": "array",
                    "items": {
                        "anyOf": [
                            {
                                "type": "object",
                                "required": ["protocol", "name", "servicePort"],
                                "properties": {
                                    "protocol": {"type": "string", "enmu": ["TCP", "UDP"]},
                                    "name": {"type": "string", "pattern": RES_NAME_PATTERN},
                                    "servicePort": {
                                        "oneOf": [
                                            {"type": "string", "pattern": NUM_VAR_PATTERN},
                                            {"type": "number", "minimum": 1, "maximum": 65535},
                                        ]
                                    },
                                },
                            },
                            {
                                "type": "object",
                                "required": ["protocol", "name", "servicePort", "domainName"],
                                "properties": {
                                    "protocol": {"type": "string", "enmu": ["HTTP"]},
                                    "name": {"type": "string", "pattern": RES_NAME_PATTERN},
                                    "servicePort": {
                                        "oneOf": [
                                            {"type": "string", "pattern": NUM_VAR_PATTERN},
                                            {"type": "number", "minimum": 1, "maximum": 65535},
                                        ]
                                    },
                                    "domainName": {"type": "string", "format": "hostname"},
                                },
                            },
                            {
                                "type": "object",
                                "required": ["protocol", "name", "servicePort", "domainName"],
                                "properties": {
                                    "protocol": {"type": "string", "enmu": ["HTTP", "TCP", "UDP"]},
                                    "name": {"type": "string", "pattern": "^$"},
                                    "servicePort": {"type": "string", "pattern": "^$"},
                                    "domainName": {"type": "string", "pattern": "^$"},
                                },
                            },
                        ]
                    },
                },
            },
        },
    },
}

CONFIGMAP_SCHEMA = {
    "type": "object",
    "required": ["metadata", "datas"],
    "properties": {
        "metadata": {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string", "pattern": RES_NAME_PATTERN}},
        },
        "datas": {
            "type": "object",
            "patternProperties": {
                KEY_NAME_PATTERN: {
                    "anyOf": [
                        {
                            "type": "object",
                            "required": ["type", "content"],
                            "properties": {
                                "type": {"type": "string", "enum": ["file"]},
                                "content": {"type": "string", "minLength": 1},
                            },
                        },
                        {
                            "type": "object",
                            "required": ["type", "content"],
                            "properties": {
                                "type": {"type": "string", "enum": ["http"]},
                                "content": {"type": "string", "format": "uri"},
                            },
                        },
                    ]
                }
            },
            "additionalProperties": False,
        },
    },
}

SECRET_SCHEMA = {
    "type": "object",
    "required": ["metadata", "datas"],
    "properties": {
        "metadata": {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string", "pattern": RES_NAME_PATTERN}},
        },
        "datas": {
            "type": "object",
            "patternProperties": {
                KEY_NAME_PATTERN: {
                    "type": "object",
                    "required": ["content"],
                    "properties": {"content": {"type": "string", "minLength": 1}},
                }
            },
            "additionalProperties": False,
        },
    },
}

HPA_SCHNEA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "id": "mesos_hpa",
    "type": "object",
    "required": ["apiVersion", "kind", "metadata", "spec"],
    "properties": {
        "apiVersion": {"type": "string", "enum": ["v4"]},
        "kind": {"type": "string", "enum": ["autoscaler"]},
        "metadata": {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string", "pattern": RES_NAME_PATTERN}},
        },
        "spec": {
            "type": "object",
            "required": ["scaleTargetRef", "minInstance", "maxInstance", "metrics"],
            "properties": {
                "scaleTargetRef": {
                    "type": "object",
                    "required": ["kind", "name"],
                    "properties": {
                        "kind": {"type": "string", "enum": ["Deployment"]},
                        "name": {"type": "string", "pattern": RES_NAME_PATTERN},
                    },
                },
                "minInstance": {"type": "number", "minimum": 0},
                "maxInstance": {"type": "number", "minimum": 0},
                "metrics": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["type", "name", "target"],
                        "properties": {
                            "type": {"type": "string", "enum": ["Resource"]},
                            "name": {"type": "string", "enum": ["cpu", "memory"]},
                            "target": {
                                "type": "object",
                                "required": ["type", "averageUtilization"],
                                "properties": {
                                    "type": {"type": "string", "enum": ["AverageUtilization"]},
                                    "averageUtilization": {"type": "number", "minimum": 0},
                                },
                            },
                        },
                    },
                },
            },
        },
    },
}

INGRESS_SCHNEA = {
    "type": "object",
    "required": ["apiVersion", "kind", "metadata", "spec"],
    "properties": {
        "apiVersion": {"type": "string", "enum": ["clb.bmsf.tencent.com/v1"]},
        "kind": {"type": "string", "enum": ["ClbIngress"]},
        "metadata": {
            "type": "object",
            "required": ["name", "labels"],
            "properties": {"name": {"type": "string", "pattern": RES_NAME_PATTERN}, "kind": {"type": "string"}},
        },
    },
}

CONFIG_SCHEMA = [
    APPLICATION_SCHEMA,
    DEPLOYMENT_SCHEMA,
    SERVICE_SCHEMA,
    CONFIGMAP_SCHEMA,
    SECRET_SCHEMA,
    HPA_SCHNEA,
    INGRESS_SCHNEA,
]

CONFIG_SCHEMA_MAP = dict(zip(MRESOURCE_NAMES, CONFIG_SCHEMA))
