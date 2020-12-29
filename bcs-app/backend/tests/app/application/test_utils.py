# -*- coding: utf-8 -*-
import pytest
from typing import Dict

from backend.apps.application.utils import get_k8s_resource_status
from backend.apps.application import constants
from backend.utils import FancyDict

running = constants.ResourceStatus.Running.value
abnormal = constants.ResourceStatus.Unready.value
completed = constants.ResourceStatus.Completed.value


@pytest.mark.parametrize(
    "resource_name, replicas, available, expect",
    [
        ("deployment", 1, 0, abnormal),
        ("deployment", 1, 1, running),
        ("deployment", 0, 0, running),
        ("daemonset", 1, 0, abnormal),
        ("daemonset", 1, 1, running),
        ("daemonset", 0, 0, running),
        ("statefulset", 1, 0, abnormal),
        ("statefulset", 1, 1, running),
        ("statefulset", 0, 0, running),
    ],
)
def test_k8s_resource_status(resource_name, replicas, available, expect):
    resource = FancyDict()
    status = get_k8s_resource_status(resource_name, resource, replicas, available)
    assert status == expect


@pytest.mark.parametrize(
    "resource_name, replicas, available, completions, expect",
    [
        ("job", 1, 0, 0, abnormal),
        ("job", 1, 0, 1, abnormal),
        ("job", 1, 1, 1, completed),
    ],
)
def test_k8s_job_status(resource_name, replicas, available, completions, expect):
    resource = FancyDict(data=FancyDict(spec=FancyDict(completions=completions)))
    status = get_k8s_resource_status(resource_name, resource, replicas, available)
    assert status == expect
