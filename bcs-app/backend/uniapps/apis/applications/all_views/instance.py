# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.http import JsonResponse
from rest_framework.response import Response

from backend.components.bcs.mesos import MesosClient
from backend.uniapps.apis.applications import serializers
from backend.uniapps.apis.applications.views import BaseBatchHandleInstance
from backend.uniapps.apis.base_views import APIUser, BaseAPIViews
from backend.uniapps.apis.utils import check_user_project
from backend.uniapps.application import views as app_views
from backend.utils import FancyDict
from backend.utils.basic import getitems
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes
from backend.utils.renderers import BKAPIRenderer

DEFAULT_MSG_TYPE = "signal"


class BaseSendSignal(BaseBatchHandleInstance, app_views.BaseAPI):
    def request_signal(self, access_token, project_id, cluster_id, namespace, name, data):
        client = MesosClient(access_token, project_id, cluster_id, None)
        resp = client.send_application_signal(namespace, name, data)
        error_message_list = []
        data = resp.get("data") or []
        if data:
            error_message_list = ["taskgroup id:%s, status:%s" % (info.get("ID"), info.get("Status")) for info in data]
        return error_message_list

    def get_params(self, request, req_info):
        if request.user.project_kind in ["k8s", "tke"]:
            raise error_codes.CheckFailed.f("项目类型只能为MESOS，请检查后重试", replace=True)
        inst_id_list = req_info.get("inst_id_list") or []
        if not inst_id_list:
            raise error_codes.CheckFailed.f("实例ID不能为空", replace=True)
        signal_info = req_info.get("signal_info") or {}
        if not signal_info:
            raise error_codes.CheckFailed.f("信号信息不能为空", replace=True)
        msg_type = signal_info.get("msg_type")
        msg_type = msg_type if msg_type else DEFAULT_MSG_TYPE
        signal_info["msg_type"] = msg_type
        return inst_id_list, signal_info


class SendApplicationSignal(BaseSendSignal):
    CATEGORY = "application"

    def send_signal(self, request, cc_app_id, project_id):
        self.init_handler(request, cc_app_id, project_id, serializers.BatchScaleInstanceParamsSLZ)
        req_info = dict(request.data)
        inst_id_list, signal_info = self.get_params(request, req_info)
        batch_inst_info = self.get_batch_inst_info(inst_id_list)
        # 批量处理
        message = "ok"
        error_message_list = []
        for inst_id in inst_id_list:
            curr_inst = batch_inst_info[str(inst_id)]
            conf = self.get_common_instance_conf(curr_inst)
            metadata = conf.get("metadata") or {}
            name = metadata.get("name")
            namespace = metadata.get("namespace")
            labels = metadata.get("labels", {})
            cluster_id = labels.get("io.tencent.bcs.clusterid")
            if conf.get("kind") != self.CATEGORY:
                error_message_list.append("应用: %s::%s必须为Application类型，请确认后重试" % (namespace, name))
                continue
            req_data = {
                "name": name,
                "namespace": namespace,
                "msgtype": signal_info["msg_type"],
                "msgdata": {"processname": signal_info["process_name"], "signal": signal_info["signal"]},
            }
            error_message = self.request_signal(
                request.user.token.access_token, project_id, cluster_id, namespace, name, req_data
            )
            if error_message:
                error_message_list.append(
                    "应用:%s::%s有操作失败情况，详细taskgroup信息:%s" % (namespace, name, ";".join(error_message))
                )
        if error_message_list:
            message = ";".join(error_message_list)
            return JsonResponse({"code": 400, "message": message})
        return JsonResponse({"code": 0, "message": message})


class SendDeploymentSignal(BaseSendSignal):
    CATEGORY = "deployment"

    def get_rc_name_by_deployment(self, request, project_id, cluster_id, namespace, name, project_kind=2):
        """根据deployment获取到application name"""
        flag, resp = self.get_application_deploy_info(
            request,
            project_id,
            cluster_id,
            name,
            category="deployment",
            project_kind=project_kind,
            field="data.application,data.application_ext",
            namespace=namespace,
        )
        if not flag:
            raise error_codes.APIError.f(resp.data.get("message"), replace=True)
        ret_data = []
        for info in resp.get("data") or []:
            application = (info.get("data") or {}).get("application") or {}
            application_ext = (info.get("data") or {}).get("application") or {}
            if application:
                ret_data.append(application.get("name"))
            if application_ext:
                ret_data.append(application_ext.get("name"))

        return ret_data

    def send_signal(self, request, cc_app_id, project_id):
        self.init_handler(request, cc_app_id, project_id, serializers.BatchScaleInstanceParamsSLZ)
        req_info = dict(request.data)
        inst_id_list, signal_info = self.get_params(request, req_info)
        batch_inst_info = self.get_batch_inst_info(inst_id_list)
        # 批量处理
        message = "ok"
        error_message_list = []
        for inst_id in inst_id_list:
            curr_inst = batch_inst_info[str(inst_id)]
            conf = self.get_common_instance_conf(curr_inst)
            metadata = conf.get("metadata") or {}
            name = metadata.get("name")
            namespace = metadata.get("namespace")
            labels = metadata.get("labels", {})
            cluster_id = labels.get("io.tencent.bcs.clusterid")
            if conf.get("kind") != self.CATEGORY:
                error_message_list.append("应用: %s::%s必须为Application类型，请确认后重试" % (namespace, name))
                continue
            app_name_list = self.get_rc_name_by_deployment(request, project_id, cluster_id, namespace, name)
            for app_name in app_name_list:
                req_data = {
                    "name": name,
                    "namespace": namespace,
                    "msgtype": signal_info["msg_type"],
                    "msgdata": {"processname": signal_info["process_name"], "signal": signal_info["signal"]},
                }
                error_message = self.request_signal(
                    request.user.token.access_token, project_id, cluster_id, namespace, name, req_data
                )
                if error_message:
                    error_message_list.append(
                        "应用:%s::%s有操作失败情况，详细taskgroup信息:%s" % (namespace, name, ";".join(error_message))
                    )
        if error_message_list:
            message = ";".join(error_message_list)
            return JsonResponse({"code": 400, "message": message})
        return JsonResponse({"code": 0, "message": message})


class BaseInstanceAPI(app_views.BaseAPI, BaseAPIViews):
    def init_handler(self, request, cc_app_id, project_id):
        self.project_kind, self.app_code, self.project_info = check_user_project(
            self.data["access_token"], project_id, cc_app_id, self.jwt_info(request), is_orgin_project=True
        )
        request.user = APIUser
        request.user.token.access_token = self.data["access_token"]
        request.user.username = self.app_code
        request.user.project_kind = self.project_kind
        # 添加project信息，方便同时处理提供给apigw和前台页面使用
        request.project = FancyDict(self.project_info)
        if request.project["kind"] != 2:
            raise error_codes.CheckFailed.f("现阶段只允许操作Mesos类型")

    def get_config_detail(self, conf):
        metadata = conf.get("metadata") or {}
        self.name = metadata.get("name")
        self.namespace = metadata.get("namespace")
        labels = metadata.get("labels", {})
        self.cluster_id = labels.get("io.tencent.bcs.clusterid")


class SendCommand(BaseInstanceAPI):
    SLZ = serializers.SendInstanceCommandParamsSLZ
    renderer_classes = (BKAPIRenderer,)

    def get_data(self, request):
        data_slz = self.SLZ(data=request.data)
        data_slz.is_valid(raise_exception=True)
        self.data = data_slz.data

    def compose_request_data(self, env_list, image_path):
        self.request_conf = {
            "apiVersion": "v4",
            "kind": "Command",
            "spec": {
                "CommandTargetRef": {
                    "kind": self.category.capitalize(),
                    "name": self.name,
                    "namespace": self.namespace,
                    "image": image_path,
                },
                "Taskgroups": [],
                "Command": self.data.get("command") or [],
                "Env": env_list,
                "User": self.data.get("username"),
                "WorkingDir": self.data.get("work_dir"),
                "Privileged": self.data.get("privileged"),
                "ReserveTime": self.data.get("reserve_time"),
            },
        }

    def get_image_path(self, env_list):
        """获取image path"""
        image_path = ""
        # 传递image的key的标识
        image_env_name = "image"
        # env_list 格式: ["image=test123:v1", "env1=123"]
        for info in env_list:
            info_list = info.split("=")
            if image_env_name not in info_list:
                continue
            image_path = info_list[-1]
            env_list.remove(info)
            break
        return image_path

    def send_cmd(self, request, cc_app_id, project_id, instance_id):
        self.get_data(request)
        self.init_handler(request, cc_app_id, project_id)
        inst_info = self.get_instance_info(instance_id)[0]
        self.category = inst_info.category
        conf = self.get_common_instance_conf(inst_info)
        self.get_config_detail(conf)
        # 获取image
        env_list = self.data.get("env") or []
        image_path = self.get_image_path(env_list)

        self.compose_request_data(env_list, image_path)

        client = MesosClient(self.data["access_token"], project_id, self.cluster_id, None)
        resp = client.send_command(self.category, self.namespace, self.name, self.request_conf)
        if resp.get("code") != ErrorCode.NoError:
            raise error_codes.APIError.f(resp.get("message"))
        return Response({"task_id": resp.get("data")})


class GetCommandStatus(BaseInstanceAPI):
    SLZ = serializers.GetCommandStatusSLZ
    SUCCESS_STATUS = ["finish"]
    SUCCESS_EXIT_CODE = [0]
    renderer_classes = (BKAPIRenderer,)

    def get_data(self, request):
        data_slz = self.SLZ(data=request.query_params)
        data_slz.is_valid(raise_exception=True)
        self.data = data_slz.data

    def status(self, request, cc_app_id, project_id, instance_id):
        self.get_data(request)
        self.init_handler(request, cc_app_id, project_id)
        inst_info = self.get_instance_info(instance_id)[0]
        self.category = inst_info.category
        conf = self.get_common_instance_conf(inst_info)
        self.get_config_detail(conf)

        client = MesosClient(self.data["access_token"], project_id, self.cluster_id, None)
        resp = client.get_command_status(self.category, self.namespace, self.name, {"id": self.data["task_id"]})
        if resp.get("code") != ErrorCode.NoError:
            raise error_codes.APIError.f(resp.get("message"))
        resp_data = resp.get("data") or {}
        if not resp_data:
            raise error_codes.CheckFailed.f("请求BCS接口返回为空，请联系管理员处理")
        # 由于流水线现在仅维护，不调整逻辑，只能中间层兼容去掉返回中的多余字段
        cmd_target_ref = getitems(resp_data, ["spec", "commandTargetRef"], default={})
        if cmd_target_ref:
            cmd_target_ref.pop("image", None)
            resp_data["spec"]["commandTargetRef"] = cmd_target_ref

        return Response(resp_data)

    def delete_command(self, request, cc_app_id, project_id, instance_id):
        self.get_data(request)
        self.init_handler(request, cc_app_id, project_id)
        inst_info = self.get_instance_info(instance_id)[0]
        self.category = inst_info.category
        conf = self.get_common_instance_conf(inst_info)
        self.get_config_detail(conf)

        client = MesosClient(self.data["access_token"], project_id, self.cluster_id, None)
        resp = client.delete_command(self.category, self.namespace, self.name, {"id": self.data["task_id"]})
        if resp.get("code") != ErrorCode.NoError:
            raise error_codes.APIError.f(resp.get("message"))
        return Response()
