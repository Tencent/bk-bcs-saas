# -*- coding: utf-8 -*-
from typing import Dict

import pytest

from backend.uniapps.application import constants
from backend.uniapps.application.utils import exclude_records, get_k8s_resource_status
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


@pytest.mark.parametrize(
    "cluster_id_from_params,cluster_id_from_instance,cluster_type_from_params,cluster_type_from_instance,expect",
    [
        ("cluster_one", "cluster_one", "test", "test", False),
        ("cluster_one", "cluster_two", "test", "test", True),
        ("cluster_one", "cluster_one", "test", "prod", False),
        ("cluster_one", None, "test", "test", True),
        (None, "cluster_one", "test", "test", False),
        (None, "cluster_one", "test", "prod", True),
    ],
)
def test_exclude_records(
    cluster_id_from_params, cluster_id_from_instance, cluster_type_from_params, cluster_type_from_instance, expect
):
    assert (
        exclude_records(
            cluster_id_from_params, cluster_id_from_instance, cluster_type_from_params, cluster_type_from_instance
        )
        is expect
    )
