# -*- coding: utf-8 -*-
from copy import deepcopy
from unittest.mock import patch

import pytest

from backend.celery_app.periodic_tasks import PRS, FinalState, PollResult
from backend.celery_app.tasks.application import MesosCreateAppHandler, MesosDeleteAppStatusPoller

fake_app_base_params = {
    "access_token": "access_token",
    "project_id": "project_id",
    "cluster_id": "cluster_id",
    "name": "name",
    "namespace": "ns",
}


@pytest.mark.parametrize(
    "mesos_app_resp, expect_task_status",
    [
        ({"code": 0}, PRS.DONE.value),
        ({"code": 1}, PRS.DOING.value),
        ({"code": 0, "data": [{"metadata": {"name": "test"}}]}, PRS.DOING.value),
        ({"code": 0, "data": []}, PRS.DONE.value),
    ],
)
@patch("backend.celery_app.tasks.application.MesosDeleteAppStatusPoller.query_mesos_app")
def test_query_status(mock_query_mesos_app, mesos_app_resp, expect_task_status):
    mock_query_mesos_app.return_value = mesos_app_resp
    resp = MesosDeleteAppStatusPoller(fake_app_base_params).query_status()
    assert resp.status == expect_task_status


@pytest.mark.parametrize(
    "poller_result, platform_instance_id, expect_task_return",
    [
        (PollResult(code=FinalState.FINISHED.value), 1, True),
        (PollResult(code=FinalState.FINISHED.value), 0, True),
        (PollResult(code=FinalState.EXECUTE_TIMEOUT.value), 0, False),
    ],
)
@patch("backend.components.bcs.mesos.MesosClient.create_application", return_value={"code": 0})
def test_create_app(
    mock_create_application,
    poller_result,
    platform_instance_id,
    expect_task_return,
    app_manifest,
    mesos_instance_record,
):
    assert mesos_instance_record.category == "application"

    params = deepcopy(fake_app_base_params)
    params.update({"kind": "application", "manifest": app_manifest, "instance_id": platform_instance_id})
    handler = MesosCreateAppHandler(params)

    # 更新db记录
    handler.update_db_record(
        instance_id=mesos_instance_record.instance_id, from_platform=True, status="Running", is_bcs_success=True
    )

    assert handler.final_result_handler(poller_result) == expect_task_return
