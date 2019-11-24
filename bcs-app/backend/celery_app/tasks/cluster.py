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

import re
import time
import logging
import json
from datetime import timedelta, datetime

from django.conf import settings
from django.utils.translation import ugettext as _

from celery import shared_task

from backend.utils.errcodes import ErrorCode
from backend.apps.cluster import models
from backend.components import jobs, paas_cc, cc, so
from backend.apps import constants
from backend.components.bcs.bcs_common_api import BCSClient
from backend.components.bcs import k8s, mesos
from backend.apps.configuration.utils_ns import register_default_ns
from backend.utils.client import get_bcs_client
from backend.bcs_k8s.app.views import helm_init
from backend.utils.send_msg import send_message

logger = logging.getLogger(__name__)
logger_sentry = logging.getLogger("sentry_logger")

STEP_INDEX_REGEX = re.compile("\d.*?")
POLLING_INTERVAL_SECONDS = getattr(settings, "POLLING_INTERVAL_SECONDS", 5)
POLLING_TIMEOUT = timedelta(
    seconds=getattr(settings, "POLLING_TIMEOUT_SECONDS", 3600))
DELETE_POLLING_TIMEOUT = timedelta(seconds=600)
# 针对bke的轮训超时时间为120s
BKE_POLLING_TIMEOUT = timedelta(seconds=60)

# JOB状态码
DEFAULT_SUCCESS_STATUS = [3, 9, 403]
INITIAL_CHECK = "initial_check"
INITIALIZE = "initialize"
SO_INITIAL = "so_initial"
REINSTALL = 'reinstall'


def _polling_bke_status(pk, log_type="NodeUpdateLog"):
    """
    """
    model = models.log_factory(log_type)
    log = model.objects.filter(pk=pk).last()

    end_time = datetime.now() + BKE_POLLING_TIMEOUT
    status = models.CommonStatus.Normal
    message = ""
    while not log.is_finished and log.is_polling:
        if datetime.now() > end_time:
            break
        try:
            bke_client = get_bcs_client(log.project_id, log.cluster_id, log.token)
            bke_client.get_cluster_credential()
            status = models.CommonStatus.Normal
            break
        except Exception as err:
            status = models.NodeStatus.BkeFailed
            message = "%s" % err
    bke_log_save(log, log_type, status, message=message)
    return

def bke_log_save(log, log_type, status, message=""):
    log.is_finished = True
    log.is_polling = False
    log.status = status
    if status != models.CommonStatus.Normal:
        err_msg = "%s" % message if message else status
    else:
        err_msg = "SUCCESS"
    log.log = json.dumps({
        "status": status,
        "node_tasks": [{"name": _("1.安装BKE Agent"), "state": err_msg}]
    })
    log.save()
    update_node_cluster_check_status(log, log_type, status=status)


@shared_task
def polling_bke_status(pk):
    _polling_bke_status(pk)


@shared_task
def chain_polling_bke_status(log_info):
    """检查BKE Agent是否安装成功
    """
    if not log_info:
        return
    log_pk, log_type = log_info
    model = models.log_factory(log_type)
    log = model.objects.filter(pk=log_pk).last()
    new_log = models.NodeUpdateLog.objects.create(  # noqa
        project_id=log.project_id,
        cluster_id=log.cluster_id,
        token=log.token,
        node_id=log.node_id,
        params=log.params,
        operator=log.operator,
        oper_type=models.NodeOperType.BkeInstall
    )
    try:
        bke_cluster_info = helm_init(new_log.token, new_log.project_id, new_log.cluster_id, 'kube-system')
    except Exception as err:
        logger.error("Install bke error, token: %s, project_id: %s, cluster_id: %s, error detail: %s"
                     % (new_log.token, new_log.project_id, new_log.cluster_id, err))
        bke_log_save(new_log, log_type, models.NodeStatus.BkeFailed, message=err)
        return

    # 异常记录LOG
    if bke_cluster_info.get("code") != ErrorCode.NoError:
        message = bke_cluster_info.get("message")
        logger.error("Install bke error, detail: %s" % message)
        bke_log_save(new_log, log_type, models.NodeStatus.BkeFailed, message)
        return
    _polling_bke_status(new_log.id)


def _polling_once(model, log):
    log = model.objects.filter(pk=log.pk).last()
    if not log:
        logger.error("log not found for pk: %s", log.pk)
        return log

    client = BCSClient(
        log.token, log.project_id, log.cluster_id, None
    )
    rsp = client.get_task_result(log.task_id)
    if rsp.get("code") != ErrorCode.NoError:
        if str(rsp.get("code")) == "5000":
            log.is_polling = False
            log.is_finished = True
            log.status = models.CommonStatus.InitialFailed
            log.save()
        return log

    data = rsp.get("data") or {}
    status = data.get("status", "UNKNOWN")
    gcloud_steps = data.get("steps") or {}
    steps = []
    failed = False
    for k, v in gcloud_steps.items():
        index = STEP_INDEX_REGEX.findall(k)
        if index:
            index = index[0]
        else:
            index = 0
        if v.get("state") in ["FAILURE", "REVOKED"]:
            failed = True
        steps.append((int(index), {
            "state": v.get("state"),
            "name": v.get("stage_name"),
        }))
    steps.sort()

    if status == "SUCCESS":
        log.status = "normal"
        log.is_finished = True
    elif status == "BLOCKED" and failed:
        if log.oper_type in [models.NodeOperType.NodeRemove, models.CommonStatus.Removing]:
            log.status = "remove_failed"
        else:
            log.status = "initial_failed"
        log.is_finished = True
    else:
        if log.oper_type == [models.NodeOperType.NodeRemove, models.CommonStatus.Removing]:
            log.status = "removing"
        else:
            log.status = "initializing"

    log.log = json.dumps({
        "state": status,
        "node_tasks": [
            i[1] for i in steps
        ],
    })
    log.save()
    return log


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

    if log.is_polling:
        logger.warning("log[%s] is polling", log_pk)
    else:
        log.is_polling = True
        log.save()

    end_time = datetime.now() + POLLING_TIMEOUT

    while not log.is_finished and log.is_polling:
        time.sleep(POLLING_INTERVAL_SECONDS)
        if datetime.now() > end_time:
            break
        try:
            log = _polling_once(model, log)
        except Exception as err:
            logger.exception(err)
    model.objects.filter(pk=log_pk).update(is_polling=False)
    # 异常时，上报sentry
    if log.status != models.CommonStatus.Normal:
        initial_oper_list = [INITIAL_CHECK, INITIALIZE, SO_INITIAL, REINSTALL]
        if log_type == "ClusterInstallLog":
            if log.oper_type in initial_oper_list:
                prefix_msg = _("初始化集群失败")
            else:
                prefix_msg = _("删除集群失败")
        else:
            if log.oper_type in initial_oper_list:
                prefix_msg = _("初始化节点失败")
            else:
                prefix_msg = _("删除节点失败")
        push_sentry(log, prefix_msg)
    if (log_type == "NodeUpdateLog") and (log.status == models.CommonStatus.Normal) \
            and (log.oper_type not in [models.NodeOperType.NodeRemove]) and ('K8S' in log.cluster_id):
        return log.id, log_type


@shared_task
def chain_polling_task(log_pk, log_type):
    if not log_pk:
        return
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

    if log.is_polling:
        logger.warning("log[%s] is polling", log_pk)
    else:
        log.is_polling = True
        log.save()

    end_time = datetime.now() + POLLING_TIMEOUT

    while not log.is_finished and log.is_polling:
        time.sleep(POLLING_INTERVAL_SECONDS)
        if datetime.now() > end_time:
            break
        try:
            log = _polling_once(model, log)
        except Exception as err:
            logger.exception(err)
    model.objects.filter(pk=log_pk).update(is_polling=False)
    # 出现异常，不影响流程
    try:
        register_ns(log)
    except Exception as err:
        logger.error("Register default namespace: %s" % err)
    # TODO：待op系统上线后，下掉以下通知
    try:
        if log_type == "ClusterInstallLog" and log.oper_type in ["initialize", "reinstall"] \
                and log.status == "normal":
            send_msg_for_cluster(log)
    except Exception as err:
        logger.error("Send cluster info failed: %s" % err)
    if (log_type == "NodeUpdateLog") and (log.status == models.CommonStatus.Normal) \
            and ('K8S' in log.cluster_id):
        return log.id, log_type


def register_ns(log):
    # 添加default命名空间
    # 如果存在则跳过
    resp = paas_cc.get_cluster_namespace_list(
        log.token, log.project_id, log.cluster_id, desire_all_data=True
    )
    ns_name_list = [
        info["name"] for info in resp.get("data", {}).get("results") or [] if info.get("name")
    ]
    if "default" not in ns_name_list:
        # 获取项目编排类型，只有为k8s时，才会执行注册操作
        resp = paas_cc.get_project(log.token, log.project_id)
        data = resp.get("data", {})
        if data.get("kind") == 1:
            register_default_ns(log.token, log.operator, log.project_id, data.get("english_name"), log.cluster_id)


def send_msg_for_cluster(log):
    """发送消息(qywx + mail)
    待 OP 系统搞完后，可以去掉本部分功能
    """
    try:
        params = json.loads(log.params)
    except Exception as err:
        logger.error("Parse json failed: %s" % err)
        params = {}
    master_ips = ",".join(params.get("master_ips") or [])
    message = """集群ID: {cluster_id} \n创建者: {creator} \nMasterIP: {master_ips}
    """.format(cluster_id=log.cluster_id, creator=log.operator, master_ips=master_ips)
    title = f"[{settings.PLAT_SHOW_NAME}]集群创建成功，详细信息:"
    receiver = [settings.DEFAULT_OPER_USER]
    send_message(receiver, message, title=title, send_way='rtx')


@shared_task
def exec_bcs_task(old_log, request=None):
    """执行bcs创建集群任务
    """
    if not old_log:
        return
    # 判断是否可以执行后续
    log_pk, log_type = old_log
    model = models.log_factory(log_type)
    if not model:
        logger.error("log not found for type: %s", log_type)
        return
    log = model.objects.filter(pk=log_pk).last()
    if not log:
        logger.error("log not found for pk: %s", log_pk)
        return

    # 组装参数
    user_token = log.token
    username = log.operator
    if request:
        user_token = request.user.token.access_token
        username = request.user.username
    # 解析参数
    try:
        params = json.loads(log.params)
    except Exception:
        params = {}
    new_log = models.ClusterInstallLog.objects.create(
        project_id=log.project_id,
        cluster_id=log.cluster_id,
        token=user_token,
        status=models.CommonStatus.Initializing,
        params=log.params,
        operator=username
    )
    client = BCSClient(
        user_token, params.get("project_id"),
        params.get("cluster_id"), None
    )
    rsp = client.create_cluster(
        params.get("kind_name"), username,
        params.get("master_ips", []),
        data={
            "modules": params.get("module_list", ""),
            "appID": constants.BCS_APP_ID,
            "needNat": params.get("need_nat", True),
        }
    )
    if rsp.get("code") != ErrorCode.NoError:
        new_log.is_finished = True
        new_log.is_polling = False
        new_log.status = models.CommonStatus.InitialFailed
        # 记录错误信息到log
        new_log.log = json.dumps({
            "state": "FAILURE",
            "node_tasks": [{"state": "FAILURE", "name": rsp.get("message")}]
        })
        new_log.save()
        result = paas_cc.update_cluster(
            user_token, params.get("project_id"),
            params.get("cluster_id"),
            {"status": models.CommonStatus.InitialFailed}
        )
        # TODO: 怎样保证写入不成功时，可以再次写入
        if result.get("code") != ErrorCode.NoError:
            return
        push_sentry(new_log, _("初始化集群失败"))
        return

    data = rsp.get("data") or {}
    new_log.task_id = data.get("taskID")
    new_log.save()
    try:
        cc.host_standard_property(
            username, params.get("master_ips", []), bak_operator_flag=True
        )
    except Exception as err:
        logger.error("Request cc error, detail: %s" % err)
    # 触发新的任务
    return new_log.id


def node_ip_status(log, project_id, cluster_id, node_info):
    log.is_finished = True
    log.is_polling = False
    log.status = models.NodeStatus.InitialFailed
    # 记录错误信息到log
    log.log = json.dumps({
        "status": models.CommonStatus.InitialFailed,
        "node_tasks": [{"name": "", "state": _("调用BCS接口失败")}]
    })
    log.save()
    # 更改任务状态
    paas_cc.update_node_list(
        log.token, project_id, cluster_id,
        [
            {
                "inner_ip": ip,
                "status": models.CommonStatus.InitialFailed,
            }
            for ip in node_info.keys()
        ]
    )


@shared_task
def node_exec_bcs_task(old_log, request=None):
    """执行bcs创建节点任务
    """
    if not old_log:
        return
    log_pk, log_type = old_log
    model = models.log_factory(log_type)
    if not model:
        logger.error("log not found for type: %s", log_type)
        return
    log = model.objects.filter(pk=log_pk).last()
    if not log:
        logger.error("log not found for pk: %s", log_pk)

    # 解析参数
    try:
        params = json.loads(log.params)
    except Exception:
        params = {}
    node_info = params.get("node_info") or {}
    user_token = log.token
    username = log.operator
    project_id = log.project_id
    cluster_id = log.cluster_id
    if request:
        user_token = request.user.token.access_token
        username = request.user.username
    new_log = models.NodeUpdateLog.objects.create(  # noqa
        project_id=project_id,
        cluster_id=cluster_id,
        token=user_token,
        node_id=",".join(node_info.values()),
        params=json.dumps(params),
        operator=username,
    )
    try:
        client = BCSClient(
            user_token, project_id, cluster_id, None
        )
        rsp = client.add_cluster_node(
            params.get("kind_name"), username,
            list(node_info.keys()), params.get("cc_app_id")
        )
    except Exception as error:
        logger.error("add add_cluster_node error: %s", error)
        node_ip_status(new_log, new_log.project_id, new_log.cluster_id, node_info)
        return

    if rsp.get("code") != ErrorCode.NoError:
        node_ip_status(new_log, new_log.project_id, new_log.cluster_id, node_info)
        push_sentry(new_log, _("节点初始化失败"))
        return

    data = rsp.get("data") or {}
    taskid = data.get("taskID")
    new_log.task_id = taskid
    new_log.save()
    return new_log.id


def _polling_initial_once(model, log):
    log = model.objects.filter(pk=log.pk, oper_type=INITIAL_CHECK).last()
    if not log:
        logger.error("log not found for pk: %s", log.pk)
        return log
    rsp = jobs.get_task_result(log.task_id)
    logger.info(u"请求JOB日志: %s" % rsp)
    # 针对获取不到的情况直接返回
    if not (rsp.get("result") and rsp.get("data")):
        return log
    data = rsp["data"].get("blocks") or []
    if not data:
        return log
    step_instances = data[0].get("stepInstances") or []
    if not step_instances:
        return log
    ip_results = step_instances[0].get("stepIpResult") or []
    if not ip_results:
        return log

    # 状态
    all_ip_results = []
    has_failed = False
    # 获取日志
    for ip_log in ip_results:
        log_content = ip_log.get("tag") or ""
        result_type_text = ip_log.get("resultTypeText") or ""
        all_ip_results.append({
            "name": ip_log.get("ip"),
            "state": log_content or result_type_text
        })
        if ("Failed" in log_content) or (ip_log.get("status") not in DEFAULT_SUCCESS_STATUS):
            has_failed = True
    # 统计整个任务的状态
    task_status = models.CommonStatus.Normal
    # 判断整个业务结束
    if (rsp.get("data") or {}).get("isFinished"):
        log.is_finished = True
    else:
        task_status = models.CommonStatus.InitialChecking
    if has_failed:
        task_status = models.CommonStatus.InitialCheckFailed
    log.log = json.dumps({
        "status": task_status,
        "node_tasks": all_ip_results
    })
    log.status = task_status
    log.save()
    return log


def update_node_cluster_check_status(log, log_type, status=models.CommonStatus.InitialCheckFailed):
    """更新master or slave失败状态
    """
    if log_type == "ClusterInstallLog":
        result = paas_cc.update_cluster(
            log.token, log.project_id, log.cluster_id,
            {"status": status},
        )
    elif log_type == "NodeUpdateLog":
        try:
            params = json.loads(log.params)
        except Exception:
            params = {}
        result = paas_cc.update_node_list(
            log.token, log.project_id, log.cluster_id,
            [
                {
                    "inner_ip": ip,
                    "status": status
                }
                for ip in params.get("node_info").keys()
            ]
        )
    else:
        return
    if result.get("code") != ErrorCode.NoError:
        logger.error(u"更新配置中心状态失败，详情: %s" % result.get("message"))


@shared_task
def polling_initial_task(log_type, log_pk):
    """轮训初始化检测
    """
    model = models.log_factory(log_type)
    if not model:
        logger.error("log not found for type: %s", log_type)
        return

    log = model.objects.filter(pk=log_pk).last()
    if not log:
        logger.error("log not found for pk: %s", log_pk)
        return

    if log.is_finished:
        logger.info("log[%s] has been finished", log_pk)
        return

    if log.is_polling:
        logger.warning("log[%s] is polling", log_pk)
    else:
        log.is_polling = True
        log.save()

    end_time = datetime.now() + POLLING_TIMEOUT

    while not log.is_finished and log.is_polling:
        time.sleep(POLLING_INTERVAL_SECONDS)
        if datetime.now() > end_time:
            break
        try:
            log = _polling_initial_once(model, log)
        except Exception as err:
            logger.exception(err)
            return
    model.objects.filter(pk=log_pk).update(is_polling=False)
    if log.status in [models.CommonStatus.InitialCheckFailed]:
        push_sentry(log, _("前置检查失败"))
        # 更改node或集群状态
        update_node_cluster_check_status(log, log_type)
        return
    return log_pk, log_type


def _polling_so_initial_once(model, log):
    """轮训结果
    """
    rsp = so.get_so_task_result(log.operator, log.task_id)
    logger.info("请求SO日志: %s" % rsp)
    # 针对获取不到的请求直接返回
    if not (rsp.get("result") and rsp.get("data")):
        return log
    data = rsp["data"]
    failed_num = data.get("subjob_fail") or 0
    status_en = data.get("status_en")
    # 如果没有结束，则继续轮训
    if status_en not in ["done"]:
        return log
    # 如果任务已经结束，则判断任务是成功或者失败并记录日志
    log.is_finished = True
    log.is_polling = False
    failed_ip_list = []
    failed_num = int(failed_num)
    status = "SUCCESS"
    log_status = models.CommonStatus.Normal
    if failed_num > 0:
        log.status = models.CommonStatus.SoInitialFailed
        # 记录失败的节点
        sub_job_list = data.get("subjoblist") or []
        failed_ip_list = [info.get("ip") for info in sub_job_list if info.get("result") in ["failed"]]
        status = "FAILURE"
        node_tasks = [
            {
                "state": settings.SO_ERROR_MSG
                % (";".join(failed_ip_list), log.task_id),
                "name": _("1.SO实例化失败")
            }
        ]
        log_status = models.CommonStatus.SoInitialFailed
    else:
        node_tasks = [
            {
                "state": status,
                "name": _("1.SO初始化完成")
            }
        ]
    log.log = json.dumps({
        "status": status,
        "node_tasks": node_tasks
    })
    log.status = log_status
    log.save()
    return log


@shared_task
def polling_so_init(old_log, log_pk=None, log_type=None):
    """SO初始化
    """
    if not (old_log or (log_pk and log_type)):
        return
    if old_log:
        log_pk, log_type = old_log
    model = models.log_factory(log_type)
    if not model:
        logger.error("log not found for type: %s", log_type)
        return
    log = model.objects.filter(pk=log_pk).last()
    if not log:
        logger.error("log not found for pk: %s", log_pk)

    end_time = datetime.now() + POLLING_TIMEOUT
    while not log.is_finished and log.is_polling:
        time.sleep(POLLING_INTERVAL_SECONDS)
        if datetime.now() > end_time:
            break
        try:
            log = _polling_so_initial_once(model, log)
        except Exception as err:
            logger.exception(err)
            continue
    # model.objects.filter(pk=log_pk).update(is_polling=False)
    if log.status in [models.CommonStatus.SoInitialFailed]:
        push_sentry(log, _("SO初始化失败"))
        # 更改node或集群状态
        update_node_cluster_check_status(log, log_type, status=log.status)
        return
    return log_pk, log_type


@shared_task
def so_init(old_log, request=None):
    """SO初始化
    """
    if not old_log:
        return
    log_pk, log_type = old_log
    model = models.log_factory(log_type)
    if not model:
        logger.error("log not found for type: %s", log_type)
        return
    log = model.objects.filter(pk=log_pk).last()
    if not log:
        logger.error("log not found for pk: %s", log_pk)
    user_token = log.token
    username = log.operator
    if request:
        user_token = request.user.token.access_token
        username = request.user.username
    try:
        params = json.loads(log.params)
    except Exception:
        params = {}
    save_params = {
        "project_id": log.project_id,
        "cluster_id": log.cluster_id,
        "token": user_token,
        "status": models.CommonStatus.SoInitial,
        "params": log.params,
        "operator": username,
        "oper_type": SO_INITIAL
    }
    if log_type != "ClusterInstallLog":
        save_params["node_id"] = log.node_id
    new_log = model.objects.create(**save_params)
    # 触发初始化检查任务
    ip_list = params.get("master_ips") or params.get("node_info", {}).keys()
    resp = so.initial_host(username, ip_list or [])
    task_id = (resp.get("data") or {}).get("job_id")
    if not resp.get("result") or not task_id:
        new_log.is_finished = True
        new_log.is_polling = False
        new_log.status = models.CommonStatus.SoInitialFailed
        new_log.log = json.dumps({
            "state": "FAILURE",
            "node_tasks": [{"state": "FAILURE", "name": f"{_('1.SO初始化失败')}: {resp.get('message')}"}]
        })
        new_log.save()
        update_node_cluster_check_status(
            new_log, log_type, status=models.CommonStatus.SoInitialFailed)

        return
    new_log.task_id = task_id
    new_log.is_polling = True
    new_log.save()
    return new_log.id, log_type


def func_handler(func, name, log, *args):
    """
    """
    try:
        record_status = models.CommonStatus.Removing
        resp = func(*args)
        if not resp.get("result"):
            record_status = models.CommonStatus.RemoveFailed
            save_record_log(log, "FAILURE", name, resp.get("message"), record_status)
            update_cluster_status(log)
            log.save()
            return False
    except Exception as err:
        record_status = models.CommonStatus.RemoveFailed
        save_record_log(log, "FAILURE", name, "%s" % err, record_status)
        update_cluster_status(log)
        log.save()
        return False
    save_record_log(log, "SUCCESS", name, _("操作成功"), record_status)
    return True


def delete_handler(log):
    """
    """
    params = log.params
    try:
        params = json.loads(params)
    except Exception:
        logger.error("parse the log[%s] params error", log.pk)
        return
    # cc_app_id = params["cc_app_id"]
    # host_ips = params["host_ips"]
    # operator = log.operator
    # if not func_handler(cc.host_standard_property, _("2.修改主机备注"), log, operator, host_ips):
        # return
    # if not func_handler(cc.remove_host_lock, _("3.释放主机锁"), log, operator, host_ips):
        # return
    # 删除集群
    if not func_handler(
            paas_cc.delete_cluster, _("4.移除集群"), log, log.token, log.project_id, log.cluster_id):
        return
    log.status = models.CommonStatus.Normal
    log.save()


def save_record_log(log, status, name, message, record_status, replace=False):
    log_record_json = log.log
    if log_record_json and not replace:
        log_record = json.loads(log_record_json)
        log_record["node_tasks"].append({
            "state": message,
            "name": name,
        })
        log_record["state"] = status
        log.log = json.dumps(log_record)
    else:
        log.log = json.dumps({
            "state": status,
            "node_tasks": [{
                "state": message,
                "name": name,
            }]
        })
    log.status = record_status
    log.save()


def update_cluster_status(log, status=models.CommonStatus.RemoveFailed):
    """更新集群状态
    """
    resp = paas_cc.update_cluster(
        log.token, log.project_id, log.cluster_id,
        {"status": status}
    )
    if resp.get("code") != ErrorCode.NoError:
        log.status = models.CommonStatus.RemoveFailed
        save_record_log(log, "FAILURE", _("更新集群状态"), resp.get("message"), models.CommonStatus.RemoveFailed)
        log.save()


def _polling_host_module_once(log, step_name, task_id=None):
    """检查任务执行状态
    """
    task_id = task_id or log.task_id
    resp = cc.get_modify_result(log.operator, task_id)
    if not resp.get("result"):
        log.is_finished = True
        log.is_polling = False
        return log, True
    data = resp.get("data")
    is_finished = True
    is_polling = False
    record_status = models.CommonStatus.Removing
    if data.get("exec_result") in [0]:
        state = "SUCCESS"
        is_terminaled = False
        message = u"操作成功"
    elif data.get("exec_result") in [1000]:
        state = "SUCCESS"
        is_finished = False
        is_polling = True
        is_terminaled = False
        message = data.get("err_info")
    else:
        record_status = models.CommonStatus.RemoveFailed
        state = "FAILURE"
        is_terminaled = True
        message = data.get("err_info")
        update_cluster_status(log)
    log.is_finished = is_finished
    log.is_polling = is_polling
    save_record_log(log, state, step_name, message, record_status, replace=True)
    log.save()
    return log, is_terminaled


@shared_task
def delete_cluster_task(log_type, log_pk):
    """删除集群
    """
    model = models.log_factory(log_type)
    if not model:
        logger.error("log not found for type: %s", log_type)
        return
    log = model.objects.filter(pk=log_pk).last()
    if not log:
        logger.error("log not found for pk: %s", log_pk)
        return
    if log.is_finished:
        logger.error("log[%s] has been finished", log_pk)
        return
    if not log.is_polling:
        log.is_polling = True
        log.save()

    end_time = datetime.now() + DELETE_POLLING_TIMEOUT
    is_terminaled = False

    while not log.is_finished and log.is_polling:
        time.sleep(POLLING_INTERVAL_SECONDS)
        if datetime.now() > end_time:
            break
        try:
            log, is_terminaled = _polling_host_module_once(log, _("1.修改主机模块"))
        except Exception as err:
            logger.exception(err)
    if is_terminaled:
        return
    # 执行任务
    delete_handler(log)
    # if log.status != models.CommonStatus.Normal:
    #     push_sentry(log, _("删除集群失败"))


def common_model_handler(log_type, log_pk, task_id_flag=False):
    """针对model的统一处理
    """
    if not log_pk:
        return
    model = models.log_factory(log_type)
    if not model:
        logger.error("log not found for type: %s", log_type)
        return

    log = model.objects.filter(pk=log_pk).last()
    if not log:
        logger.error("log not found for pk: %s", log_pk)
        return

    if not log.task_id and task_id_flag:
        logger.error("task id is null for pk: %s", log_pk)
        return

    if log.is_finished:
        logger.info("log[%s] has been finished", log_pk)
        return

    if log.is_polling:
        logger.warning("log[%s] is polling", log_pk)
    else:
        log.is_polling = True
        log.save()
    return model, log


def get_host_pod(access_token, project_id, cluster_id, inner_ip_list):
    """查询k8s机器下的pod
    """
    k8s_client = k8s.K8SClient(
        access_token, project_id, cluster_id, None
    )
    resp = k8s_client.get_pod(
        host_ips=inner_ip_list, field="namespace"
    )
    return resp.get("data")


def get_host_taskgroup(access_token, project_id, cluster_id, inner_ip_list):
    """查询mesos机器下taskgroup
    """
    mesos_client = mesos.MesosClient(
        access_token, project_id, cluster_id, None
    )
    resp = mesos_client.get_taskgroup(
        inner_ip_list, fields="namespace"
    )
    return resp.get("data")


def get_pod_taskgroup_info(log):
    """查询node下pod信息为空
    """
    params = json.loads(log.params)
    kind = params.get("kind_name")
    if kind not in ["k8s", "mesos"]:
        log.status = models.CommonStatus.RemoveFailed
        log.log = json.dumps({
            "state": "remove_failed",
            "node_tasks": [{
                "state": "FAILURE",
                "name": _("获取项目信息失败")
            }]
        })
    if kind == "k8s":
        data = get_host_pod(
            log.token, log.project_id, log.cluster_id, list(params["nodes"].keys())
        )
    else:
        data = get_host_taskgroup(
            log.token, log.project_id, log.cluster_id, list(params["nodes"].keys())
        )
    if not data:
        log.is_finished = True
        log.is_polling = False
        log.status = models.CommonStatus.Normal
        log.log = json.dumps({
            "state": "normal",
            "node_tasks": [{
                "state": "SUCCESS",
                "name": _("POD/TASKGROUP重新调度成功!")
            }]
        })
        log.save()


@shared_task
def force_delete_node(log_type, log_pk):
    """强制删除节点
    """
    model, log = common_model_handler(log_type, log_pk)
    # 轮训状态
    end_time = datetime.now() + DELETE_POLLING_TIMEOUT
    while not log.is_finished and log.is_polling:
        time.sleep(POLLING_INTERVAL_SECONDS)
        if datetime.now() > end_time:
            log.is_finished = True
            log.is_polling = False
            log.status = models.CommonStatus.RemoveFailed
            log.log = json.dumps({
                "state": "remove_failed",
                "node_tasks": [{
                    "state": "FAILURE",
                    "name": _("POD/TASKGROUP重新调度超时,请手动处理!")
                }]
            })
            return None, None
        try:
            get_pod_taskgroup_info(log)
        except Exception as err:
            logger.exception(err)

    params = json.loads(log.params)
    new_log = models.NodeUpdateLog.objects.create(  # noqa
        project_id=log.project_id,
        cluster_id=log.cluster_id,
        token=log.token,
        node_id=",".join(params.get("nodes", {}).values()),
        params=json.dumps(params),
        operator=log.operator,
        oper_type=models.NodeOperType.NodeRemove,
    )
    return log_type, new_log.id


@shared_task
def delete_cluster_node(new_log):
    log_type, log_id = new_log
    if not (log_type and log_id):
        return log_type, log_id
    model = models.log_factory(log_type)
    log = model.objects.filter(id=log_id).last()
    params = json.loads(log.params)
    # 触发bcs任务
    model.objects.filter(id=log.id)
    bcs_client = BCSClient(
        log.token, log.project_id, log.cluster_id, None
    )
    resp = bcs_client.delete_cluster_node(
        params.get("kind_name"), log.operator, list(params.get("nodes", {}).keys())
    )
    if not resp.get("result"):
        log.is_finished = True
        log.is_polling = False
        log.status = models.CommonStatus.RemoveFailed
        log.log = json.dumps({
            "state": "remove_failed",
            "node_tasks": [{
                "state": "FAILURE",
                "name": resp.get("message")
            }]
        })
        log.save()
        result = paas_cc.update_node(
            log.token, log.project_id, params["node_id"],
            {"status": models.CommonStatus.RemoveFailed}
        )
        if result.get("code") != ErrorCode.NoError:
            return None, None
        return None, None

    data = resp.get("data") or {}
    taskid = data.get("taskID")
    log.task_id = taskid
    log.is_polling = True
    log.save()
    return log_type, log.id


@shared_task
def delete_cluster_node_polling(new_log):
    log_type, log_id = new_log
    if not (log_type and log_id):
        return
    model = models.log_factory(log_type)
    log = model.objects.filter(id=log_id).last()
    end_time = datetime.now() + POLLING_TIMEOUT

    while not log.is_finished and log.is_polling:
        time.sleep(POLLING_INTERVAL_SECONDS)
        if datetime.now() > end_time:
            break
        try:
            log = _polling_once(model, log)
        except Exception as err:
            logger.exception(err)
    model.objects.filter(pk=log_id).update(is_polling=False)


def push_sentry(log, prefix_msg):
    try:
        logger_sentry.error(
            "%s, project: %s, cluster: %s, params: %s, logs: %s" % (
                prefix_msg, log.project_id, log.cluster_id, log.params, log.log
            )
        )
    except Exception as err:
        logger.error("Push sentry error, detail: %s" % err)
