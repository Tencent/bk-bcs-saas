# -*- coding: utf-8 -*-
import time
from unittest import mock

import pytest

from backend.container_service.clusters import models
from backend.container_service.clusters.tasks import ClusterOrNodeTaskPoller, TaskStatusResultHandler
from backend.packages.blue_krill.async_utils.poll_task import (
    CallbackResult,
    CallbackStatus,
    PollingMetadata,
    TaskPoller,
)
from backend.tests.bcs_mocks.fake_ops import FakeOPSClient

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def cluster_record():
    models.ClusterInstallLog.objects.create(
        id=1,
        project_id="project_id",
        cluster_id="cluster_id",
        task_id="task_id",
        token="access_token",
        operator="admin",
        params='{"cc_app_id": 1}',
        log='{}',
        is_finished=False,
        is_polling=True,
        status="RUNNING",
        oper_type="initialize",
    )


class TestClusterOrNodeTaskPoller:
    @mock.patch(
        "backend.container_service.clusters.tasks.ops.OPSClient",
        new=FakeOPSClient,
    )
    @mock.patch(
        "backend.container_service.clusters.tasks.paas_auth.get_access_token",
        return_values={"access_token": "access_token"},
    )
    def test_task_query(self, get_access_token):
        record = models.ClusterInstallLog.objects.get(id=1)
        assert record.project_id == "project_id"

        started_at = time.time()
        metadata = PollingMetadata(retries=0, query_started_at=started_at, queried_count=0)
        poller = ClusterOrNodeTaskPoller(params={"model_type": "ClusterInstallLog", "pk": 1}, metadata=metadata)
        task_record = poller.get_task_record()
        assert task_record.project_id == "project_id"

        step_logs, status, _ = poller._get_task_result(record)
        assert step_logs == [{"state": "RUNNING", "name": "- Step one"}, {"state": "FAILURE", "name": "- Step two"}]
        assert status == "FAILURE"


class TestTaskStatusResultHandler:
    @mock.patch("backend.container_service.clusters.tasks.update_status", return_values=None)
    def test_callback(self, status):
        callback_result = CallbackResult(status=CallbackStatus.TIMEOUT.value)
        started_at = time.time()
        metadata = PollingMetadata(retries=0, query_started_at=started_at, queried_count=0)
        poller = ClusterOrNodeTaskPoller(params={"model_type": "ClusterInstallLog", "pk": 1}, metadata=metadata)
        TaskStatusResultHandler().handle(callback_result, poller)

        record = models.ClusterInstallLog.objects.get(id=1)
        assert record.status == models.CommonStatus.InitialFailed
