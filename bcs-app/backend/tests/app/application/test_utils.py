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
    "replicas, available, expect",
    [
        (1, 0, abnormal),
        (1, 1, running),
        (0, 0, running),
    ],
)
def test_k8s_resource_status(replicas, available, expect):
    resource = FancyDict()
    status = get_k8s_resource_status("deployment", resource, replicas, available)
    assert status == expect


@pytest.mark.parametrize(
    "replicas, available, completions, expect",
    [
        (1, 0, 0, abnormal),
        (1, 0, 1, abnormal),
        (1, 1, 1, completed),
    ],
)
def test_k8s_job_status(replicas, available, completions, expect):
    resource = FancyDict(data=FancyDict(spec=FancyDict(completions=completions)))
    status = get_k8s_resource_status("job", resource, replicas, available)
    assert status == expect
