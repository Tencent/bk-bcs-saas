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
import copy
import json
import logging
from datetime import datetime

from django.utils.translation import ugettext_lazy as _

from backend.celery_app.tasks.application import update_create_error_record
from backend.kube_core.hpa.utils import get_mesos_deployment_hpa
from backend.templatesets.legacy_apps.configuration.models import Template
from backend.templatesets.legacy_apps.instance.constants import InsState
from backend.templatesets.legacy_apps.instance.models import (
    InstanceConfig,
    InstanceEvent,
    MetricConfig,
    VersionInstance,
)
from backend.uniapps.application import utils
from backend.uniapps.application.constants import (
    DELETE_INSTANCE,
    FUNC_MAP,
    RESUME_INSTANCE,
    REVERSE_CATEGORY_MAP,
    SOURCE_TYPE_MAP,
    UNNORMAL_STATUS,
)
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes

logger = logging.getLogger(__name__)


class GetNamespace(object):
    def get_ns_app_info(self, ns_id_list, inst_name):
        """获取命名空间下的应用列表"""
        all_info = (
            InstanceConfig.objects.filter(
                namespace__in=ns_id_list, is_deleted=False, category__in=["application", "deployment"]
            )
            .exclude(ins_state=InsState.NO_INS.value)
            .order_by("-updated")
        )
        if inst_name:
            all_info = all_info.filter(name=inst_name)
        ret_data = {}
        ns_inst = {}
        create_error = {}
        for info in all_info:
            if info.namespace in ret_data:
                ret_data[info.namespace] += 1
            else:
                ret_data[info.namespace] = 1
            key = int(info.namespace)
            app_flag = "%s:%s" % (info.category, info.name)
            if key in ns_inst:
                ns_inst[key].append(app_flag)
            else:
                ns_inst[key] = [app_flag]
            if not info.is_bcs_success:
                if key in create_error:
                    create_error[key] += 1
                else:
                    create_error[key] = 1

        return ret_data, ns_inst, create_error

    def compose_cluster_ns_inst(self, ns_map, ns_inst):
        """组装集群、命名空间、实例"""
        ret_data = {}
        for key, val in ns_map.items():
            if not ns_inst.get(key[0]):
                continue
            inst_info = ns_inst[key[0]]
            cluster_id = val["cluster_id"]
            for item_info in inst_info:
                app_id = "%s:%s" % (val["name"], item_info)
                if cluster_id in ret_data:
                    ret_data[cluster_id].append(app_id)
                else:
                    ret_data[cluster_id] = [app_id]
        return ret_data

    def get_ns_inst_error_count(self, func, request, project_id, kind, ns_name_list, inst_name, cluster_id_list):
        """获取实例异常数量"""
        # 针对deployment，需要获取application的状态
        ret_data = {}
        all_data = {}
        exist_ns_app = []
        # 1. 先处理deployment
        for cluster_id in set(cluster_id_list):
            application_deployment_map = {}
            # app_ns_list = []
            # if "deployment" in info:
            flag, resp = func(
                request,
                project_id,
                cluster_id,
                instance_name=inst_name,
                category="deployment",
                project_kind=kind,
                namespace=",".join(set(ns_name_list)),
                field="data.status,resourceName,namespace,data.application,data.application_ext",
            )
            if not flag:
                logger.error("请求storage接口出现异常，详情: %s" % resp)
                continue
            data = resp.get("data") or []

            for item in data:
                ns_name = item.get("namespace")
                data_info = item.get("data") or {}
                application_data = data_info.get("application") or {}
                application_data_ext = data_info.get("application_ext") or {}
                if application_data.get("name"):
                    application_deployment_map[(ns_name, application_data["name"])] = item.get("resourceName")
                if application_data_ext.get("name"):
                    application_deployment_map[(ns_name, application_data_ext["name"])] = item.get("resourceName")

            flag, resp = func(
                request,
                project_id,
                cluster_id,
                instance_name=inst_name,
                category="application",
                project_kind=kind,
                namespace=",".join(set(ns_name_list)),
                field="data.status,resourceName,namespace",
            )
            if not flag:
                logger.error("请求storage接口出现异常，详情: %s" % resp)
                continue
            app_name_status = {}
            for info in resp.get("data") or []:
                ns_name = info.get("namespace")
                resource_name = info.get("resourceName")
                if (ns_name, resource_name) not in exist_ns_app:
                    exist_ns_app.append((ns_name, resource_name))
                    if (cluster_id, ns_name) in all_data:
                        all_data[(cluster_id, ns_name)] += 1
                    else:
                        all_data[(cluster_id, ns_name)] = 1
                app_name_status[(info["namespace"], info["resourceName"])] = (info.get("data") or {}).get(
                    "status"
                ) or "Deploying"
            # 进行application和deployment的适配
            exist_name = []
            for ns_inst, status in app_name_status.items():
                if ns_inst in application_deployment_map and application_deployment_map[ns_inst] in exist_name:
                    continue
                if application_deployment_map.get(ns_inst):
                    exist_name.append(application_deployment_map[ns_inst])
                if status in UNNORMAL_STATUS:
                    if (cluster_id, ns_inst[0]) in ret_data:
                        ret_data[(cluster_id, ns_inst[0])] += 1
                    else:
                        ret_data[(cluster_id, ns_inst[0])] = 1
        return ret_data, all_data

    def get(self, request, ns_id_list, ns_map, project_id, kind, func, inst_name, ns_name_list, cluster_id_list):
        ns_app_info, ns_inst, create_error = self.get_ns_app_info(ns_id_list, inst_name)
        ns_inst_error_count, all_ns_inst_count = self.get_ns_inst_error_count(
            func, request, project_id, kind, ns_name_list, inst_name, cluster_id_list
        )
        return ns_app_info, ns_inst_error_count, create_error, all_ns_inst_count


class GetInstances(object):
    def get_muster_info(self, tmpl_id):
        tmpl_info = Template.objects.filter(id=tmpl_id).first()
        if not tmpl_info:
            return None
        return tmpl_info.name

    def get_insts(self, ns_id, inst_name):
        """获取实例"""
        category = ["application", "deployment"]
        all_inst_list = (
            InstanceConfig.objects.filter(namespace=ns_id, is_deleted=False, category__in=category)
            .exclude(ins_state=InsState.NO_INS.value)
            .order_by("-updated")
        )
        if inst_name:
            all_inst_list = all_inst_list.filter(name=inst_name)
        return all_inst_list

    def compose_inst_info(self, all_inst_list, cluster_env_map):
        """组装实例信息"""
        ret_data = {}
        category_data = {"application": {}, "deployment": {}}
        for info in all_inst_list:
            conf = json.loads(info.config)
            metadata = conf.get("metadata", {})
            key_name = (metadata.get("namespace"), metadata.get("name"))
            labels = metadata.get("labels") or {}
            item = {
                "name": metadata.get("name"),
                "namespace": metadata.get("namespace"),
                "cluster_id": labels.get("io.tencent.bcs.clusterid"),
            }

            if info.category == "application":
                category_data["application"][key_name] = item
            else:
                category_data["deployment"][key_name] = item
            backend_status = "BackendNormal"
            oper_type_flag = ""
            if not info.is_bcs_success:
                if info.oper_type == "create":
                    backend_status = "BackendError"
                else:
                    oper_type_flag = info.oper_type
            cluster_id = labels.get("io.tencent.bcs.clusterid")
            muster_id = labels.get("io.tencent.paas.templateid")
            cluster_name_env_map = cluster_env_map.get(cluster_id) or {}
            ret_data[key_name] = {
                "from_platform": True,
                "id": info.id,
                "name": metadata.get("name"),
                "namespace": metadata.get("namespace"),
                "namespace_id": info.namespace,
                "create_at": info.created,
                "update_at": info.updated,
                "backend_status": backend_status,
                "backend_status_message": _("请求失败，已通知管理员!"),
                "application_status": "Deploying",
                "deployment_status": "Deploying",
                "application_status_message": "",
                "deployment_status_message": "",
                "creator": info.creator,
                "category": info.category,
                "oper_type": info.oper_type,
                "oper_type_flag": oper_type_flag,
                "cluster_id": cluster_id,
                "cluster_name": cluster_name_env_map.get("cluster_name"),
                "cluster_env": cluster_name_env_map.get("cluster_env"),
                "environment": cluster_name_env_map.get("cluster_env_str"),
                "task_group_count": "0/0",
                "build_instance": 0,
                "instance": 0,
                "muster_id": muster_id,
                "muster_name": self.get_muster_info(muster_id),
            }
            annotations = metadata.get("annotations") or {}
            ret_data[key_name].update(utils.get_instance_version(annotations, labels))
        return ret_data, category_data

    def get_cluster_namespace_inst(self, instance_info):
        """获取集群、命名空间和deployment"""
        ret_data = {}
        for id, info in instance_info.items():
            if info["cluster_id"] in ret_data:
                ret_data[info["cluster_id"]]["inst_list"].append(info["name"])
                ret_data[info["cluster_id"]]["ns_list"].append(info["namespace"])
            else:
                ret_data[info["cluster_id"]] = {
                    "inst_list": [info["name"]],
                    "ns_list": [info["namespace"]],
                }
        return ret_data

    def get_cluster_namespace_deployment(self, instance_info, deploy_app_info):
        """针对deployment组装请求taskgroup信息"""
        ret_data = {}
        for key, info in instance_info.items():
            app_name = deploy_app_info.get((info["namespace"], info["name"]), [])
            if info["cluster_id"] in ret_data:
                ret_data[info["cluster_id"]]["inst_list"].extend(app_name)
                ret_data[info["cluster_id"]]["ns_list"].append(info["namespace"])
            else:
                ret_data[info["cluster_id"]] = {"inst_list": [], "ns_list": [info["namespace"]]}
                ret_data[info["cluster_id"]]["inst_list"].extend(app_name)
        return ret_data

    def get_application_by_deployment(
        self, request, cluster_id, kind=2, project_id=None, func=None, ns_name=None, inst_name=None
    ):
        """通过deployment获取application"""
        ret_data = {}
        flag, resp = func(
            request,
            project_id,
            cluster_id,
            inst_name,
            category="deployment",
            project_kind=kind,
            namespace=ns_name,
            field="data.application,data.application_ext,data.metadata",
        )
        if not flag:
            raise error_codes.APIError.f(resp.data.get("message"))
        for val in resp.get("data") or []:
            metadata = val.get("data", {}).get("metadata", {})
            key_name = (metadata.get("namespace"), metadata.get("name"))
            application = val.get("data", {}).get("application", {})
            application_ext = val.get("data", {}).get("application_ext", {})
            if key_name not in ret_data:
                ret_data[key_name] = []
            if application:
                ret_data[key_name].append(application.get("name"))
            if application_ext:
                ret_data[key_name].append(application_ext.get("name"))
        return ret_data

    def get_application_status(
        self,
        request,
        cluster_id,
        project_id=None,
        category="application",
        kind=2,
        func=None,
        ns_name=None,
        inst_name=None,
    ):
        """获取application的状态"""
        ret_data = {}
        flag, resp = func(
            request,
            project_id,
            cluster_id,
            inst_name,
            category=category,
            project_kind=kind,
            namespace=ns_name,
            field="data.metadata.name,data.metadata.namespace,data.status,data.message,data.buildedInstance,data.instance,updateTime,createTime,data.metadata.labels",  # noqa
        )

        if not flag:
            raise error_codes.APIError.f(resp.data.get("message"))

        for val in resp.get("data", []):
            data = val.get("data", {})
            metadata = data.get("metadata", {})
            key_name = (metadata.get("namespace"), metadata.get("name"))
            build_instance = data.get("buildedInstance") or 0
            instance = data.get("instance") or 0
            labels = metadata.get("labels", {})
            source_type = labels.get("io.tencent.paas.source_type") or "other"
            annotations = metadata.get('annotations') or {}
            ret_data[key_name] = {
                "name": metadata.get("name"),
                "namespace": metadata.get("namespace"),
                "backend_status": "BackendNormal",
                "backend_status_message": _("请求失败，已通知管理员!"),
                "category": category,
                "application_status": data.get("status"),
                "application_status_message": data.get("message"),
                "task_group_count": "%s/%s" % (build_instance, instance),
                "build_instance": build_instance,
                "instance": instance,
                "deployment_status": "",
                "deployemnt_status_message": "",
                "update_time": val.get("updateTime"),
                "create_time": val.get("updateTime"),
                "source_type": SOURCE_TYPE_MAP.get(source_type),
                "version": utils.get_instance_version_name(annotations, labels),
                'hpa': False,  # Application 默认都是未绑定
            }
        return ret_data

    def get_deployment_status(
        self,
        request,
        cluster_id,
        project_id=None,
        category="deployment",
        kind=2,
        func=None,
        ns_name=None,
        inst_name=None,
    ):
        """获取deployment的状态"""
        ret_data = {}
        flag, resp = func(
            request, project_id, cluster_id, inst_name, category=category, project_kind=kind, namespace=ns_name
        )
        if not flag:
            raise error_codes.APIError.f(resp.data.get("message"))

        # 添加HPA绑定信息
        hpa_list = get_mesos_deployment_hpa(request, project_id, cluster_id, ns_name)

        for val in resp.get("data", []):
            data = val.get("data", {})
            metadata = data.get("metadata", {})
            key_name = (metadata.get("namespace"), metadata.get("name"))
            labels = metadata.get("labels", {})
            annotations = metadata.get('annotations') or {}
            ret_data[key_name] = {
                "backend_status": "BackendNormal",
                "backend_status_message": _("请求失败，已通知管理员!"),
                "category": category,
                "deployment_status": data.get("status"),
                "deployemnt_status_message": data.get("message"),
                "source_type": labels.get("io.tencent.paas.source_type"),
                "version": utils.get_instance_version_name(annotations, labels),
                "hpa": True if key_name in hpa_list else False,
            }
        return ret_data

    def update_inst_label(self, inst_id_list):
        """更新删除的实例标识"""
        all_inst_conf = InstanceConfig.objects.filter(id__in=inst_id_list)
        all_inst_conf.update(is_deleted=True, deleted_time=datetime.now(), status="Deleted")
        # 更新metric config状态
        inst_ns = {info.instance_id: info.namespace for info in all_inst_conf}
        inst_ver_ids = inst_ns.keys()
        inst_ns_ids = inst_ns.values()
        try:
            MetricConfig.objects.filter(instance_id__in=inst_ver_ids, namespace__in=inst_ns_ids).update(
                ins_state=InsState.INS_DELETED.value
            )
        except Exception as err:
            logger.error(u"更新metric删除状态失败，详情: %s" % err)

    def compose_data(self, request, instance_info, all_status, cluster_id, ns_id, cluster_env_map, ns_name_id):
        """组装返回数据"""
        # 默认时间
        default_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update_create_error_id_list = []
        for key, val in all_status.items():
            if key in instance_info:
                if instance_info[key].get("backend_status") in ["BackendError"]:
                    instance_info[key]["backend_status"] = "BackendNormal"
                    update_create_error_id_list.append(instance_info[key]["id"])
                val.pop("version", None)
                instance_info[key].update(val)
            else:
                val['namespace_id'] = ns_name_id.get(val.get('namespace'))
                val["id"] = 0
                val["from_platform"] = False
                val["oper_type"] = "create"
                instance_info[key] = val
                # NOTE: 兼容通过storage查询不到数据的情况，默认取当前时间
                val["create_at"] = val.get("create_time") or default_time
                val["update_at"] = val.get("update_time") or default_time
            cluster_name_env_map = cluster_env_map.get(cluster_id) or {}
            instance_info[key].update(
                {
                    "namespace_id": ns_id,
                    "cluster_id": cluster_id,
                    "cluster_name": cluster_name_env_map.get("cluster_name"),
                    "cluster_env": cluster_name_env_map.get("cluster_env"),
                    "environment": cluster_name_env_map.get("cluster_env_str"),
                }
            )
            val.pop("create_time", None)
            val.pop("update_time", None)
        if update_create_error_id_list:
            update_create_error_record.delay(update_create_error_id_list)

    def inst_count_handler(self, instance_info, app_status):
        instance_list = list(instance_info.values())
        ret_data = {
            "error_num": 0,
        }
        instance_list = list(instance_list)
        inst_list_copy = copy.deepcopy(instance_list)
        for val in inst_list_copy:
            if (
                (val["backend_status"] in UNNORMAL_STATUS)
                or (val.get("application_status") in UNNORMAL_STATUS)
                or (val.get("deployment_status") in UNNORMAL_STATUS)
            ):
                if app_status in [2, "2", None]:
                    ret_data["error_num"] += 1
                else:
                    instance_list.remove(val)
            else:
                if app_status not in [1, "1", None]:
                    instance_list.remove(val)
        ret_data.update({"total_num": len(instance_list), "instance_list": instance_list})
        return ret_data

    def get(
        self,
        request,
        project_id,
        ns_id,
        project_kind,
        func_app,
        func_deploy,
        inst_name,
        app_status,
        cluster_env_map,
        cluster_id,
        ns_name,
        ns_name_id,
    ):
        """获取命名空间下的实例"""
        all_status = {}
        deploy_application_info = self.get_application_by_deployment(
            request,
            cluster_id,
            kind=project_kind,
            project_id=project_id,
            func=func_deploy,
            ns_name=ns_name,
            inst_name=inst_name,
        )
        deployment_status = self.get_deployment_status(
            request,
            cluster_id,
            project_id=project_id,
            kind=project_kind,
            func=func_app,
            ns_name=ns_name,
            inst_name=inst_name,
        )
        if deploy_application_info and inst_name:
            inst_name = ",".join(list(deploy_application_info.values())[-1])
        application_status = self.get_application_status(
            request,
            cluster_id,
            project_id=project_id,
            kind=project_kind,
            func=func_app,
            ns_name=ns_name,
            inst_name=inst_name,
        )
        # 整合状态
        copy_application_status = copy.deepcopy(application_status)
        if deploy_application_info:
            for deploy, deploy_val in deployment_status.items():
                app_name = deploy_application_info.get(deploy, [])
                for name in app_name:
                    key_name = (deploy[0], name)
                    app_status_info = application_status.get(key_name, {})
                    copy_application_status.pop(key_name, None)
                    app_status_info.pop("category", None)
                    app_status_info.pop("deployment_status", None)
                    app_status_info.pop("deployment_status_message", None)
                    # APP重新赋值HPA
                    app_status_info['hpa'] = deploy_val['hpa']
                    # NOTE: 滚动升级时，中间态可能会存在两个application(会有名称差异，如添加上版本)，为防止出现中间态时匹配不正确问题，名称强制更改为instance的名称
                    # 其中，deploy的格式为元组(命名空间, 实例名称)
                    app_status_info["name"] = deploy[-1]
                    deploy_val.update(app_status_info)
        all_status.update(deployment_status)
        all_status.update(copy_application_status)

        all_inst_list = self.get_insts(ns_id, inst_name)
        instance_info, category_data = self.compose_inst_info(all_inst_list, cluster_env_map)
        self.compose_data(request, instance_info, all_status, cluster_id, ns_id, cluster_env_map, ns_name_id)
        ret_data = instance_info.values()
        # 根据状态统计总数量及异常数量
        # 如果传递了,则要计算数量
        inst_count_label = request.GET.get("with_count")
        if inst_count_label:
            ret_data = self.inst_count_handler(instance_info, app_status)
        return ret_data
