# -*- coding: utf-8 -*-
import json
import pytest

from backend.apps.instance.models import InstanceConfig


manifest = {
    "kind": "application",
    "restartPolicy": {"policy": "OnFailure", "interval": 5, "backoff": 10, "maxtimes": 0},
    "killPolicy": {"gracePeriod": 10},
    "metricPolicy": {"isUsed": False, "list": []},
    "constraint": {"intersectionItem": []},
    "metadata": {"name": "name", "namespace": "ns"},
    "spec": {
        "instance": 1,
        "template": {
            "metadata": {},
            "spec": {
                "containers": [
                    {
                        "name": "container-1",
                        "command": "",
                        "args": [],
                        "workingDir": "",
                        "parameters": [],
                        "logPathList": [],
                        "type": "MESOS",
                        "image": "test.harbor.com/paas/public/k8s/redis:1.0",
                        "isImageCustomed": False,
                        "imagePullPolicy": "Always",
                        "privileged": False,
                        "ports": [{"containerPort": 6379, "hostPort": 6379, "name": "trestle23", "protocol": "TCP"}],
                        "healthChecks": [],
                        "resources": {"limits": {"cpu": "", "memory": ""}, "requests": {"cpu": "2", "memory": "4096"}},
                        "volumes": [],
                        "env": [],
                        "secrets": [],
                        "configmaps": [],
                    }
                ],
                "networkMode": "BRIDGE",
                "networkType": "cnm",
            },
        },
    },
    "apiVersion": "v4",
}


@pytest.fixture
def app_manifest():
    return manifest


@pytest.fixture
def mesos_instance_record(db):
    return InstanceConfig.objects.create(
        instance_id=1, namespace="ns", category="application", name="name", config=json.dumps(manifest)
    )
