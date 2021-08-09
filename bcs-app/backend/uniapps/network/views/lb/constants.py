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

from backend.utils.basic import ChoicesEnum

MESOS_LB_ENV_CONFIG = []
LB_HAPROXY_STATS_FRONTEND_AUTH_PASSWORD = getattr(settings, "LB_HAPROXY_STATS_FRONTEND_AUTH_PASSWORD", None)
if LB_HAPROXY_STATS_FRONTEND_AUTH_PASSWORD:
    MESOS_LB_ENV_CONFIG = [
        {"name": "LB_HAPROXY_STATS_FRONTEND_AUTH_USER", "value": "bcsadmin"},
        {"name": "LB_HAPROXY_STATS_FRONTEND_AUTH_PASSWORD", "value": LB_HAPROXY_STATS_FRONTEND_AUTH_PASSWORD},
    ]


# mesos lb service manifest
MESOS_LB_SERVICE = {
    "apiVersion": "v4",
    "kind": "service",
    "metadata": {"name": "", "namespace": ""},
    "spec": {"selector": {}},
}

# mesos lb deployment manifest
MESOS_LB_DEPLOYMENT = {
    "apiVersion": "v4",
    "kind": "deployment",
    "restartPolicy": {"policy": "OnFailure", "interval": 10},
    "constraint": {},
    "metadata": {"name": "", "namespace": ""},
    "spec": {
        "instance": 1,
        "strategy": {
            "type": "RollingUpdate",
            "rollingupdate": {
                "maxUnavilable": 1,
                "maxSurge": 1,
                "upgradeDuration": 20,
                "rollingOrder": "DeleteFirst",
                "rollingManually": False,
            },
        },
        "template": {
            "metadata": {"labels": {}},
            "spec": {
                "containers": [
                    {
                        "command": "/bcs-lb/start.sh",
                        "args": [],
                        "type": "MESOS",
                        "image": "",
                        "imagePullPolicy": "Always",
                        "privileged": True,
                        "resources": {},
                        "configmaps": [],
                        "env": MESOS_LB_ENV_CONFIG,
                    }
                ],
                "networkMode": "",
                "networkType": "",
            },
        },
    },
}

# mesos lb的状态
class MESOS_LB_STATUS(ChoicesEnum):
    NOT_DEPLOYED = "not_deployed"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    STOPPING = "stopping"
    STOPPED = "stopped"

    _choices_labels = (
        (NOT_DEPLOYED, "not_deployed"),
        (DEPLOYING, "deploying"),
        (DEPLOYED, "deployed"),
        (STOPPING, "stopping"),
        (STOPPED, "stopped"),
    )


# mesos deployment和application的稳定状态
MESOS_APP_STABLE_STATUS = ["Abnormal", "Running", "Finish", "Failed", "Lost"]
