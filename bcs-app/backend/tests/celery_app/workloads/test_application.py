# -*- coding: utf-8 -*-
from copy import deepcopy
from unittest.mock import patch

from backend.apps.instance.models import InstanceConfig
from backend.celery_app.periodic_tasks import PRS, PollResult, FinalState
from backend.celery_app.tasks.application import MesosRebuildAppTaskStatus, MesosCreateAppHandler


fake_app_base_params = {
    "access_token": "access_token",
    "project_id": "project_id",
    "cluster_id": "cluster_id",
    "name": "name",
    "namespace": "ns",
}


@patch("backend.components.bcs.mesos.MesosClient.get_mesos_app_instances", return_value={"code": 0, "data": []})
def test_query_status_done(mock_get_mesos_app_instances):
    params = deepcopy(fake_app_base_params)
    params["kind"] = "application"
    resp = MesosRebuildAppTaskStatus(params).query_status()
    assert resp.status == PRS.DONE.value


@patch(
    "backend.components.bcs.mesos.MesosClient.get_deployment",
    return_value={"code": 0, "data": [{"data": {"status": "Running"}}]},
)
def test_query_status_doing(mock_get_deployment):
    params = deepcopy(fake_app_base_params)
    params["kind"] = "deployment"
    resp = MesosRebuildAppTaskStatus(params).query_status()
    assert resp.status == PRS.DOING.value


def test_create_app_timeout():
    poll_result = PollResult(code=FinalState.EXECUTE_TIMEOUT.value)
    assert not MesosCreateAppHandler(fake_app_base_params).final_result_handler(poll_result)


@patch("backend.components.bcs.mesos.MesosClient.create_application", return_value={"code": 0})
def test_create_not_from_platform_app(mock_create_application, app_manifest):
    """非平台APP的创建"""
    params = fake_app_base_params
    params.update({"kind": "application", "manifest": app_manifest, "instance_id": 0})
    handler = MesosCreateAppHandler(params)

    assert handler.params["instance_id"] == 0

    poll_result = PollResult(code=FinalState.FINISHED.value)
    assert handler.final_result_handler(poll_result)


@patch("backend.components.bcs.mesos.MesosClient.create_application", return_value={"code": 0})
def test_create_platform_app(mock_create_application, app_manifest, mesos_instance_record):
    """平台APP的创建"""
    assert mesos_instance_record.category == "application"

    params = fake_app_base_params
    params.update({"kind": "application", "manifest": app_manifest, "instance_id": 1})
    handler = MesosCreateAppHandler(fake_app_base_params)

    # 更新db记录
    handler.update_db_record(
        instance_id=mesos_instance_record.instance_id, from_platform=True, status="Running", is_bcs_success=True
    )
    obj = InstanceConfig.objects.get(id=mesos_instance_record.instance_id)
    assert obj.oper_type == "rebuild"

    poll_result = PollResult(code=FinalState.FINISHED.value)
    assert handler.final_result_handler(poll_result)
