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
import json
import logging
from typing import Dict, List, Tuple, Union

from django.conf import settings

from backend.apps.cluster import models
from backend.components import base as comp_base
from backend.components import ops, paas_auth, paas_cc
from backend.packages.blue_krill.async_utils.poll_task import (
    CallbackHandler,
    CallbackResult,
    CallbackStatus,
    PollingResult,
    PollingStatus,
    TaskPoller,
)

TASK_FAILED_STATUS = ["FAILURE", "REVOKED", "FAILED"]
TASK_SUCCESS_STATUS = ["SUCCESS", "FINISHED"]

logger = logging.getLogger(__name__)


class ClusterOrNodeTaskPoller(TaskPoller):
    """轮训集群及节点添加、删除任务的状态"""

    default_retry_delay_seconds = getattr(settings, "POLLING_INTERVAL_SECONDS", 10)
    overall_timeout_seconds = getattr(settings, "POLLING_TIMEOUT_SECONDS", 3600)

    def query(self) -> PollingResult:
        # 获取任务记录
        record = self.get_task_record()
        # 解析任务
        step_logs, status, tke_cluster_id = self._get_task_result(record)
        # 更新记录字段
        self._update_record_fields(record, status, step_logs, tke_cluster_id)
        polling_status = PollingStatus.DOING.value
        if record.is_finished:
            polling_status = PollingStatus.DONE.value

        return PollingResult(status=polling_status)

    def get_task_record(self) -> Union[models.ClusterInstallLog, models.NodeUpdateLog]:
        """获取task记录"""
        params = self.params
        # 任务类型: cluster/node
        model_type = params["model_type"]
        # 任务记录的ID
        task_record_id = params["pk"]
        task_model = models.log_factory(model_type)
        if not task_model:
            logger.error(f'not found {model_type} task')
            return

        # 获取记录
        record = task_model.objects.filter(pk=task_record_id).last()
        if not record:
            logger.error(f'not found task: {task_record_id}')
            return
        # 判断任务是否结束
        if record.is_finished:
            logger.info(f'record: {task_record_id} has been finished')
            return record
        return record

    def _parse_steps(self, data: Dict) -> List:
        step_logs = data.get("steps") or []
        logs, failed_logs = [], []
        # 获取返回的任务日志
        for log in step_logs:
            # 渲染步骤名称，用于前端展示
            step_status = log.get("status")
            step_name_status = {"state": step_status, "name": "- %s" % (log.get("name", "").capitalize())}
            # NOTE: 兼容先前，并行时，返回的日志，可能正常和错误交叉，为方便前端展示，需要处理为前面步骤为成功，后面步骤为失败
            if step_status in TASK_FAILED_STATUS:
                failed_logs.append(step_name_status)
            else:
                logs.append(step_name_status)
        # 合并子步骤
        logs.extend(failed_logs)
        return logs

    def _get_task_result(self, record: Union[models.ClusterInstallLog, models.NodeUpdateLog]) -> Tuple[List, str, str]:
        """解析任务状态
        兼容先前的逻辑, 返回日志格式{"state": "任务总状态", "node_tasks": "子步骤logs"}
        """
        token = paas_auth.get_access_token()
        task_result = get_task_result(token["access_token"], record)
        # 获取状态及步骤
        data = task_result.get("data") or {}
        return self._parse_steps(data), data.get("status", ""), data.get("tke_cluster_id", "")

    def _update_record_fields(
        self,
        record: Union[models.ClusterInstallLog, models.NodeUpdateLog],
        status: str,
        step_logs: List,
        tke_cluster_id: str = "",
    ):
        if status in TASK_FAILED_STATUS:
            record.status = get_failed_status(record.oper_type)
        elif status in TASK_SUCCESS_STATUS:
            record.status = models.CommonStatus.Normal
        # 处于失败或成功状态时，认为任务已经结束
        if status in TASK_FAILED_STATUS or status in TASK_SUCCESS_STATUS:
            record.is_finished = True
            record.is_polling = False
        if step_logs:
            record.log = json.dumps({"state": status, "node_tasks": step_logs})
        # 添加tke集群的cluster_id
        log_params = record.log_params
        # 如果配置不存在，则不作调整
        if "config" in log_params:
            log_params["config"].update({"extra_cluster_id": tke_cluster_id})
            record.params = json.dumps(log_params)
        record.save(update_fields=["status", "is_finished", "is_polling", "params", "log", "update_at"])


class TaskStatusResultHandler(CallbackHandler):
    """处理超时状态，更新db记录及bcs cc中状态"""

    def handle(self, result: CallbackResult, poller: TaskPoller):
        record = poller.get_task_record()
        if result.status == CallbackStatus.TIMEOUT.value:
            record.set_finish_polling_status(
                finish_flag=True, polling_flag=False, status=get_failed_status(record.oper_type)
            )
        # 更新bcs cc中集群或节点状态
        update_status(poller.params["model_type"], record)


def get_task_result(access_token: str, record: Union[models.ClusterInstallLog, models.NodeUpdateLog]) -> Dict:
    params = json.loads(record.params)
    return ops.get_task_result(
        access_token, record.project_id, record.task_id, params.get("cc_app_id"), params.get("username")
    )


def update_status(log_type: str, record: Union[models.ClusterInstallLog, models.NodeUpdateLog]):
    if log_type == "ClusterInstallLog":
        update_cluster_status(record)
    else:
        update_node_status(record)


def get_failed_status(op_type: str) -> str:
    """处理异常时，针对不同操作的状态"""
    if op_type in [models.ClusterOperType.ClusterRemove, models.NodeOperType.NodeRemove]:
        status = models.CommonStatus.RemoveFailed
    elif op_type in [models.ClusterOperType.ClusterUpgrade, models.ClusterOperType.ClusterReupgrade]:
        status = models.ClusterStatus.UpgradeFailed
    else:
        status = models.CommonStatus.InitialFailed
    return status


def get_bcs_cc_record_status(record: Union[models.ClusterInstallLog, models.NodeUpdateLog]) -> str:
    """获取存储在bcs cc的记录的状态"""
    if record.oper_type in [models.ClusterOperType.ClusterRemove, models.NodeOperType.NodeRemove]:
        if record.status == models.CommonStatus.Normal:
            status = models.CommonStatus.Removed
        else:
            status = record.status
        return status
    return record.status


def update_cluster_status(record: Union[models.ClusterInstallLog, models.NodeUpdateLog]):
    """更新集群状态"""
    # 获取access_token
    token = paas_auth.get_access_token()
    access_token = token["access_token"]

    bcs_cc_client = paas_cc.PaaSCCClient(comp_base.ComponentAuth(access_token=access_token))
    project_id = record.project_id
    cluster_id = record.cluster_id
    # 更新集群状态
    status = get_bcs_cc_record_status(record)
    params = json.loads(record.params)
    req_data = {"status": status, "extra_cluster_id": params.get("config", {}).get("extra_cluster_id")}
    bcs_cc_client.update_cluster(project_id, cluster_id, req_data)
    logger.info(f'Update cluster[{cluster_id}] success')

    # 如果当前为删除操作，并且状态为删除的，则删除当前记录
    if (record.oper_type == models.ClusterOperType.ClusterRemove) and (status == models.CommonStatus.Removed):
        # 删除集群及master
        bcs_cc_client.delete_cluster(project_id, cluster_id)
        logger.info(f'Delete cluster[{cluster_id}] success')


def update_node_status(record: Union[models.ClusterInstallLog, models.NodeUpdateLog]):
    params = json.loads(record.params)
    ip_list = list(params.get("node_info", {}).keys())
    status = get_bcs_cc_record_status(record)
    # 获取access token
    token = paas_auth.get_access_token()
    # 更新节点状态
    bcs_cc_client = paas_cc.PaaSCCClient(comp_base.ComponentAuth(access_token=token["access_token"]))
    bcs_cc_client.update_node_list(
        record.project_id,
        record.cluster_id,
        [paas_cc.UpdateNodesData(inner_ip=ip, status=status) for ip in ip_list],
    )
    logger.info(f'Update node[{json.dumps(ip_list)}] status success')


try:
    from .tasks_ext import get_task_result  # noqa
except ImportError as e:
    logger.debug("Load extension failed: %s", e)
