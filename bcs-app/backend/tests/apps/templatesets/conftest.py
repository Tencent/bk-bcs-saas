# -*- coding: utf-8 -*-
#
# Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
# Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
import pytest

from backend.apps.configuration import models
from backend.apps.configuration.constants import TemplateEditMode

NGINX_DEPLOYMENT_JSON = {
    "apiVersion": "apps/v1beta2",
    "kind": "Deployment",
    "monitorLevel": "general",
    "webCache": {
        "volumes": [{"type": "emptyDir", "name": "", "source": ""}],
        "isUserConstraint": False,
        "remarkListCache": [{"key": "", "value": ""}],
        "labelListCache": [{"key": "app", "value": "nginx", "isSelector": True, "disabled": False}],
        "logLabelListCache": [{"key": "", "value": ""}],
        "isMetric": False,
        "metricIdList": [],
        "affinityYaml": "",
        "nodeSelectorList": [{"key": "", "value": ""}],
        "hostAliasesCache": [],
    },
    "customLogLabel": {},
    "metadata": {"name": "deployment-1"},
    "spec": {
        "minReadySeconds": 0,
        "replicas": 1,
        "strategy": {"type": "RollingUpdate", "rollingUpdate": {"maxUnavailable": 1, "maxSurge": 0}},
        "selector": {"matchLabels": {"app": "nginx"}},
        "template": {
            "metadata": {"labels": {"app": "nginx"}, "annotations": {}},
            "spec": {
                "restartPolicy": "Always",
                "terminationGracePeriodSeconds": 10,
                "nodeSelector": {},
                "affinity": {},
                "hostNetwork": 0,
                "dnsPolicy": "ClusterFirst",
                "volumes": [],
                "containers": [
                    {
                        "name": "container-1",
                        "webCache": {
                            "desc": "",
                            "imageName": "paas/k8stest/nginx",
                            "imageVersion": "",
                            "args_text": "",
                            "containerType": "container",
                            "livenessProbeType": "HTTP",
                            "readinessProbeType": "HTTP",
                            "logListCache": [{"value": ""}],
                            "env_list": [
                                {"type": "custom", "key": "eeee", "value": "{{test3}}.{{test7}}"},
                                {"type": "custom", "key": "fff", "value": "{{hieitest1}}"},
                            ],
                            "isImageCustomed": False,
                        },
                        "volumeMounts": [],
                        "image": "example.com:8443/paas/k8stest/nginx:{{image_version}}",
                        "imagePullPolicy": "IfNotPresent",
                        "ports": [{"id": 1570707798811, "containerPort": 80, "name": "http", "protocol": "TCP"}],
                        "command": "",
                        "args": "",
                        "env": [],
                        "workingDir": "",
                        "securityContext": {"privileged": False},
                        "resources": {
                            "limits": {"cpu": "", "memory": ""},
                            "requests": {"cpu": "", "memory": ""},
                        },
                        "livenessProbe": {
                            "httpGet": {"port": "", "path": "", "httpHeaders": []},
                            "tcpSocket": {"port": ""},
                            "exec": {"command": ""},
                            "initialDelaySeconds": 15,
                            "periodSeconds": 10,
                            "timeoutSeconds": 5,
                            "failureThreshold": 3,
                            "successThreshold": 1,
                        },
                        "readinessProbe": {
                            "httpGet": {"port": "", "path": "", "httpHeaders": []},
                            "tcpSocket": {"port": ""},
                            "exec": {"command": ""},
                            "initialDelaySeconds": 15,
                            "periodSeconds": 10,
                            "timeoutSeconds": 5,
                            "failureThreshold": 3,
                            "successThreshold": 1,
                        },
                        "lifecycle": {
                            "preStop": {"exec": {"command": ""}},
                            "postStart": {"exec": {"command": ""}},
                        },
                        "imageVersion": "{{image_version}}",
                        "logPathList": [],
                    }
                ],
                "initContainers": [],
            },
        },
    },
}

NGINX_SVC_JSON = {
    "apiVersion": "v1",
    "kind": "Service",
    "webCache": {"link_app": [], "link_labels": ["app:nginx"], "serviceIPs": ""},
    "metadata": {"name": "service-1", "labels": {}, "annotations": {}},
    "spec": {
        "type": "ClusterIP",
        "selector": {"app": "nginx"},
        "clusterIP": "",
        "ports": [
            {
                "name": "http",
                "port": 80,
                "protocol": "TCP",
                "targetPort": "http",
                "nodePort": "",
                "id": 1570707798811,
            }
        ],
    },
}


@pytest.fixture
def form_show_version(db, project_id):
    template = models.Template.objects.create(
        project_id=project_id, name="nginx", edit_mode=TemplateEditMode.PageForm.value
    )
    deploy = models.K8sDeployment.perform_create(
        name="nginx-deployment",
        config=NGINX_DEPLOYMENT_JSON,
    )
    svc = models.K8sService.perform_create(name="nginx-service", config=NGINX_SVC_JSON)

    ventity = models.VersionedEntity.objects.create(
        template_id=template.id, entity={"K8sDeployment": str(deploy.id), "K8sService": str(svc.id)}
    )

    return models.ShowVersion.objects.create(name="v1", template_id=template.id, real_version_id=ventity.id)
