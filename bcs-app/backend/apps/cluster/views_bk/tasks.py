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
import time
from datetime import datetime, timedelta

from celery import shared_task
from django.conf import settings

from backend.apps.cluster import models
from backend.components import ops, paas_cc, ssm
from backend.utils.errcodes import ErrorCode

logger = logging.getLogger(__name__)
POLLING_TIMEOUT = timedelta(seconds=getattr(settings, "POLLING_TIMEOUT_SECONDS", 3600))
POLLING_INTERVAL_SECONDS = getattr(settings, "POLLING_INTERVAL_SECONDS", 5)
TASK_FAILE_SUCCESS_STATUS = ["FAILURE", "SUCCESS"]
TASK_FAILED_STATUS = ["FAILURE"]
TASK_SUCCESS_STATUS = ["SUCCESS"]
CLUSTER_INSTALL_LOG = "ClusterInstallLog"


def log_status(log):
    if log.oper_type in [models.ClusterOperType.ClusterRemove, models.NodeOperType.NodeRemove]:
        status = models.CommonStatus.RemoveFailed
    else:
        status = models.CommonStatus.InitialFailed
    return status


def _polling_once(model, log):
    token_dict = ssm.get_client_access_token()
    params = json.loads(log.params)
    resp = ops.get_task_result(
        token_dict["access_token"], log.project_id, log.task_id, params.get("cc_app_id"), params.get("username")
    )
    if resp.get("code") != ErrorCode.NoError:
        logger.error("query task failed, detail: %s" % resp.get("message"))
    data = resp.get("data") or {}
    status = data.get("status", "UNKNOWN")
    step_logs = data.get("steps") or []
    logs = []
    running_logs = []
    failure_logs = []
    for index, val in enumerate(step_logs, 1):
        local_status = val.get("status")
        local_name = "- %s" % (val.get("name", "").capitalize())
        local_name_status = {"state": local_status, "name": local_name}
        if local_status in TASK_SUCCESS_STATUS:
            logs.append(local_name_status)
        elif local_status in TASK_FAILED_STATUS:
            failure_logs.append(local_name_status)
        else:
            running_logs.append(local_name_status)
    logs.extend(running_logs)
    logs.extend(failure_logs)

    if status in TASK_FAILE_SUCCESS_STATUS:
        if status in TASK_FAILED_STATUS:
            log.status = log_status(log)
        else:
            log.status = models.CommonStatus.Normal
        log.is_finished = True
        log.is_polling = False
    if logs:
        log.log = json.dumps({"state": status, "node_tasks": logs})
    log.save()
    return log


def delete_iam_cluster_resource(log):
    """删除iam集群信息"""
    pass


def update_cluster_status(log):
    if log.oper_type == models.ClusterOperType.ClusterRemove:
        if log.status == models.CommonStatus.Normal:
            status = models.CommonStatus.Removed
        else:
            status = log.status
    else:
        status = log.status
    for i in range(2):
        token_dict = ssm.get_client_access_token()
        resp = paas_cc.update_cluster(token_dict["access_token"], log.project_id, log.cluster_id, {"status": status})
        if resp.get("code") != ErrorCode.NoError:
            logger.error("Update cluster[%s] status failed, detail: %s" % (log.cluster_id, resp.get("message")))
        else:
            logger.info("Update cluster[%s] success" % log.cluster_id)
            break
    if log.oper_type in [models.ClusterOperType.ClusterInstall, models.NodeOperType.NodeInstall]:
        return
    if log.status not in [models.CommonStatus.Normal]:
        return
    for i in range(2):
        # 删除集群及master
        token_dict = ssm.get_client_access_token()
        resp = paas_cc.delete_cluster(token_dict["access_token"], log.project_id, log.cluster_id)
        if resp.get("code") != ErrorCode.NoError:
            logger.error("Delete cluster[%s] failed, detail: %s" % (log.cluster_id, resp.get("message")))
        else:
            logger.info("Delete cluster[%s] success" % log.cluster_id)
            break
    # 删除iam集群
    delete_iam_cluster_resource(log)


def update_node_status(log):
    params = json.loads(log.params)
    ip_list = list(params.get("node_info", {}).keys())
    if log.oper_type == models.NodeOperType.NodeRemove:
        if log.status == models.CommonStatus.Normal:
            status = models.CommonStatus.Removed
        else:
            status = log.status
    else:
        status = log.status
    for i in range(2):
        token_dict = ssm.get_client_access_token()
        resp = paas_cc.update_node_list(
            token_dict["access_token"],
            log.project_id,
            log.cluster_id,
            [{"inner_ip": ip, "status": status} for ip in ip_list],
        )
        if resp.get("code") != ErrorCode.NoError:
            logger.error("Update node[%s] status failed, detail: %s" % (json.dumps(ip_list), resp.get("message")))
        else:
            logger.info("Update node[%s] status success" % json.dumps(ip_list))
            break


def update_status(log_type, log):
    if log_type == CLUSTER_INSTALL_LOG:
        update_cluster_status(log)
    else:
        update_node_status(log)


@shared_task
def polling_task(log_type, log_pk):
    model = models.log_factory(log_type)
    if not model:
        logger.error("log not found for type: %s", log_type)
        return

    log = model.objects.filter(pk=log_pk).last()
    if not log:
        logger.error("log not found for pk: %s", log_pk)
        return

    if not log.task_id:
        logger.error("task id is null for pk: %s", log_pk)
        return

    if log.is_finished:
        logger.info("log[%s] has been finished", log_pk)
        return

    end_time = datetime.now() + POLLING_TIMEOUT
    while not log.is_finished and log.is_polling:
        time.sleep(POLLING_INTERVAL_SECONDS)
        if datetime.now() > end_time:
            break
        try:
            log = _polling_once(model, log)
        except Exception as err:
            logger.exception("query task failed, detail: %s" % err)
    # 超时更新状态
    if not log.is_finished:
        log.is_finished = True
        log.is_polling = False
        log.status = log_status(log)
        log.save()
    # 更新配置中心状态
    update_status(log_type, log)


try:
    from .tasks_ext import *  # noqa
except ImportError as e:
    logger.debug("Load extension failed: %s", e)
