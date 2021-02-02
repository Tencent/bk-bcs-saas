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
from typing import Dict, Tuple

from celery import shared_task
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from backend.apps.application.constants import FUNC_MAP, MESOS_FUNC_MAP
from backend.apps.instance.constants import EventType, InsState
from backend.apps.instance.models import InstanceConfig, InstanceEvent, VersionInstance
from backend.celery_app.periodic_tasks import (
    PRS,
    BasePollerTaskStatus,
    BaseResultHandler,
    FinalState,
    PollResult,
    PollStatus,
)
from backend.components.bcs import k8s, mesos
from backend.utils.errcodes import ErrorCode

DEFAULT_RESPONSE = {"code": 0}
POLLING_INTERVAL_SECONDS = getattr(settings, "POLLING_INTERVAL_SECONDS", 5)
POLLING_TIMEOUT = timedelta(seconds=getattr(settings, "POLLING_TIMEOUT_SECONDS", 600))
logger = logging.getLogger(__name__)


def get_mesos_application_deploy_status(
    access_token, cluster_id, instance_name, project_id=None, category="application", field=None, namespace=None
):
    """查询mesos下application和deployment的状态"""
    mesos_client = mesos.MesosClient(access_token, project_id, cluster_id, None)
    if category == "application":
        resp = mesos_client.get_mesos_app_instances(
            app_name=instance_name,
            field=field or "data.status",
            namespace=namespace,
        )
    else:
        resp = mesos_client.get_deployment(
            name=instance_name,
            field=field or "data.status",
            namespace=namespace,
        )
    return resp


def get_k8s_category_status(
    access_token, cluster_id, instance_name, project_id=None, category="application", field=None, namespace=None
):
    """查询mesos下application和deployment的状态"""
    client = k8s.K8SClient(access_token, project_id, cluster_id, None)
    curr_func = getattr(client, FUNC_MAP[category] % "get")
    resp = curr_func(
        {
            "name": instance_name,
            "field": field or "data.status",
            "namespace": namespace,
        }
    )
    return resp


def create_instance(access_token, cluster_id, ns, data, project_id=None, category="application", kind=2):
    """创建实例"""
    if kind == 2:
        mesos_client = mesos.MesosClient(access_token, project_id, cluster_id, None)
        if category == "application":
            resp = mesos_client.create_application(ns, data)
        else:
            resp = mesos_client.create_deployment(ns, data)
    else:
        client = k8s.K8SClient(access_token, project_id, cluster_id, None)
        curr_func = getattr(client, FUNC_MAP[category] % "create")
        resp = curr_func(ns, data)
        resp = DEFAULT_RESPONSE
    return resp


def update_instance_record_status(info, oper_type, status="Running", is_bcs_success=True):
    """更新单条记录状态"""
    info.oper_type = oper_type
    info.status = status
    info.is_bcs_success = is_bcs_success
    info.save()


@shared_task
def application_polling_task(
    access_token, inst_id, cluster_id, instance_name, category, kind, ns_name, project_id, username=None, conf=None
):
    """轮训任务状态，并启动创建任务"""
    is_polling = True
    while is_polling:
        if kind == 2:
            result = get_mesos_application_deploy_status(
                access_token, cluster_id, instance_name, category=category, namespace=ns_name, project_id=project_id
            )
        else:
            result = get_k8s_category_status(
                access_token, cluster_id, instance_name, category=category, namespace=ns_name, project_id=project_id
            )
        if result.get("code") == 0 and not result.get("data"):
            is_polling = False
        time.sleep(POLLING_INTERVAL_SECONDS)
    if str(inst_id) != "0":
        # 执行创建任务
        info = InstanceConfig.objects.get(id=inst_id)
        conf = json.loads(info.config)
    resp = create_instance(
        access_token, cluster_id, ns_name, conf, category=category, kind=kind, project_id=project_id
    )
    if str(inst_id) == "0":
        return
    # 更新instance状态
    if resp.get("code") != ErrorCode.NoError:
        update_instance_record_status(info, "rebuild", status="Error", is_bcs_success=False)
        # 记录失败事件
        conf_instance_id = conf.get("metadata", {}).get("labels", {}).get("io.tencent.paas.instanceid")
        err_msg = resp.get("message") or _("实例化失败，已通知管理员!")
        logger.error("实例化失败, 实例ID: %s, 详细:%s" % (inst_id, err_msg))
        try:
            InstanceEvent(
                instance_config_id=inst_id,
                category=category,
                msg_type=EventType.REQ_FAILED.value,
                instance_id=conf_instance_id,
                msg=err_msg,
                creator=username,
                updator=username,
                resp_snapshot=json.dumps(resp),
            ).save()
        except Exception as error:
            logger.error(u"存储实例化失败消息失败，详情: %s" % error)
    else:
        update_instance_record_status(info, "rebuild", status="Running", is_bcs_success=True)


@shared_task
def instance_polling_task(access_token, inst_id, cluster_id, category=None, kind=2, ns_name=None):
    """针对实例的轮训
    1. 实例化后直接触发轮训任务
    2. 执行某个操作后，触发针对当前操作的轮训任务
    3. 返回状态通过查询db获取
    """
    pass


@shared_task
def delete_instance_task(access_token, inst_id_list, project_kind):
    """后台更新删除实例是否被删除成功"""
    # 通过instance id获取到相应的记录，然后查询mesos/k8s的实例状态
    inst_info = InstanceConfig.objects.filter(id__in=inst_id_list)
    is_polling = True
    all_count = len(inst_info)
    end_time = datetime.now() + POLLING_TIMEOUT
    while is_polling:
        deleted_id_list = []
        time.sleep(POLLING_INTERVAL_SECONDS)
        for info in inst_info:
            inst_conf = json.loads(info.config)
            metadata = inst_conf.get("metadata") or {}
            labels = metadata.get("labels") or {}
            cluster_id = labels.get("io.tencent.bcs.clusterid")
            namespace = labels.get("io.tencent.bcs.namespace")
            project_id = labels.get("io.tencent.paas.projectid")
            category = info.category
            name = metadata.get("name")
            # 根据类型获取查询
            if project_kind == 1:
                client = k8s.K8SClient(access_token, project_id, cluster_id, None)
                curr_func = getattr(client, FUNC_MAP[category] % "get")
                resp = curr_func({"name": name, "namespace": namespace})
            else:
                client = mesos.MesosClient(access_token, project_id, cluster_id, None)
                curr_func = getattr(client, MESOS_FUNC_MAP[category])
                if category == "deployment":
                    name_key = "name"
                else:
                    name_key = "app_name"
                resp = curr_func(**{"%s" % name_key: name, "namespace": namespace})
            if not resp.get("data"):
                deleted_id_list.append(info.id)
                # 删除名称+命名空间+类型
                InstanceConfig.objects.filter(name=info.name, namespace=info.namespace, category=info.category).update(
                    is_deleted=True, deleted_time=datetime.now()
                )

        if len(deleted_id_list) == all_count or datetime.now() > end_time:
            is_polling = False


@shared_task
def update_create_error_record(id_list):
    records = InstanceConfig.objects.filter(id__in=id_list)
    records.update(ins_state=InsState.INS_SUCCESS.value, is_bcs_success=True)
    # 更新version instance
    version_instance_id_list = records.values_list("instance_id", flat=True)
    VersionInstance.objects.filter(id__in=version_instance_id_list).update(is_bcs_success=True)


class MesosDeleteAppStatusPoller(BasePollerTaskStatus):
    """Mesos删除应用后，轮训删除资源的状态"""

    default_retry_delay_seconds = 5
    overall_timeout_seconds = 3600 * 24 * 2  # 超时时间设置为2天

    def query_app_status(self):
        params = self.params
        mesos_client = mesos.MesosClient(params["access_token"], params["project_id"], params["cluster_id"], None)
        name, namespace = params["name"], params["namespace"]
        search_field = "data.status"
        if params["kind"] == "application":
            return mesos_client.get_mesos_app_instances(app_name=name, field=search_field, namespace=namespace)
        return mesos_client.get_deployment(name=name, field=search_field, namespace=namespace)

    def query_status(self):
        # 查询mesos deployment或application对应的状态
        resp = self._query_status()
        # 当查询不到时，认为已经删除，轮训结束
        status = PRS.DOING.value
        if resp.get("code") == ErrorCode.NoError and not resp.get("data"):
            status = PRS.DONE.value

        return PollStatus(status=status, result=None)


class MesosCreateAppHandler(BaseResultHandler):
    def final_result_handler(self, poll_result: PollResult) -> bool:
        # 非正常结束轮训，直接返回
        if poll_result.code != FinalState.FINISHED.value:
            return False
        # mesos需要从db中获取执行app的配置记录
        params = self.params
        instance_id = str(params["instance_id"])
        from_platform = self._from_platform(instance_id)
        # 获取资源的配置信息
        manifest = self.get_manifest(instance_id, from_platform, manifest=params["manifest"])
        # 下发配置
        resp = self.create_app(
            params["access_token"],
            params["project_id"],
            params["cluster_id"],
            params["namespace"],
            manifest,
            params["kind"],
        )
        # 处理创建资源的状态
        status, is_bcs_success = self.get_status(resp.get("code"))
        self.update_db_record(instance_id, from_platform, status, is_bcs_success)
        return True

    def create_app(
        self, access_token: str, project_id: str, cluster_id: str, namespace: str, manifest: dict, kind: str
    ) -> Dict:
        mesos_client = mesos.MesosClient(access_token, project_id, cluster_id, None)
        if kind == "application":
            return mesos_client.create_application(namespace, manifest)
        return mesos_client.create_deployment(namespace, manifest)

    def get_status(self, code: str = ErrorCode.NoError) -> Tuple[str, bool]:
        status = "Running"
        is_bcs_success = True
        if code != ErrorCode.NoError:
            status = "Error"
            is_bcs_success = False
        return (status, is_bcs_success)

    def _from_platform(self, instance_id: str) -> bool:
        """判断是否通过平台创建的资源"""
        # NOTE: 现阶段非平台创建的应用，ID 用 0 标识
        if instance_id == "0":
            return False
        return True

    def get_manifest(self, instance_id: str, from_platform: bool, manifest: Dict = None) -> Dict:
        if not from_platform:
            return manifest

        instance = InstanceConfig.objects.get(id=instance_id)
        # 获取instance的配置
        manifest = json.loads(instance.config)
        return manifest

    def update_db_record(self, instance_id: str, from_platform: bool, status: str, is_bcs_success: bool):
        if not from_platform:
            return

        InstanceConfig.objects.filter(id=instance_id).update(
            oper_type="rebuild", status=status, is_bcs_success=is_bcs_success
        )
