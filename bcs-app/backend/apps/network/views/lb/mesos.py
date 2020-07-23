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
import datetime
import copy
import logging
import json
from itertools import groupby

from rest_framework import serializers, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _

from backend.accounts import bcs_perm
from backend.utils.errcodes import ErrorCode
from backend.apps.application.utils import APIResponse
from backend.apps.application.base_views import BaseAPI
from backend.apps.configuration.models import Template, Application, VersionedEntity, Service, ShowVersion, K8sService
from backend.components import paas_cc
from backend.components.bcs import k8s, mesos
from backend.apps import constants
from backend.apps.network.constants import LB_STATUS_DICT, LB_DEFAULT_STATUS, MESOS_LB_NAMESPACE_NAME
from backend.apps.network.utils import (handle_lb, get_lb_status, delete_lb_by_bcs, get_namespace_name)
from backend.apps.instance.constants import (LABLE_TEMPLATE_ID, LABLE_INSTANCE_ID, SEVICE_SYS_CONFIG,
                                             ANNOTATIONS_CREATOR, ANNOTATIONS_UPDATOR, ANNOTATIONS_CREATE_TIME,
                                             ANNOTATIONS_UPDATE_TIME, ANNOTATIONS_WEB_CACHE, K8S_SEVICE_SYS_CONFIG,
                                             PUBLIC_LABELS, PUBLIC_ANNOTATIONS, SOURCE_TYPE_LABEL_KEY)
from backend.apps.instance.generator import (handel_service_db_config, handel_k8s_service_db_config, get_bcs_context,
                                             handle_webcache_config, remove_key, handle_k8s_api_version)
from backend.apps.instance.utils_pub import get_cluster_version
from backend.apps.configuration.serializers import ServiceCreateOrUpdateSLZ, K8sServiceCreateOrUpdateSLZ
from backend.apps.instance.drivers import get_scheduler_driver
from backend.apps.instance.funutils import update_nested_dict, render_mako_context
from backend.apps.instance.models import InstanceConfig
from backend.utils.exceptions import ComponentError
from backend.activity_log import client as activity_client
from backend.apps.application.constants import DELETE_INSTANCE
from backend.apps.network.serializers import (
    BatchResourceSLZ, LoadBalancesSLZ, UpdateLoadBalancesSLZ, GetLoadBalanceSLZ
)
from backend.apps.network.models import MesosLoadBlance
from backend.utils.error_codes import error_codes
from backend.apps.application.constants import SOURCE_TYPE_MAP

logger = logging.getLogger(__name__)
DEFAULT_ERROR_CODE = ErrorCode.UnknownError


class LoadBalances(viewsets.ViewSet, BaseAPI):
    lb_data = {}

    def merge_data(self, data, namespace):
        merge_data = []
        for info in data:
            ns_id = info.pop('namespace_id')
            ns_name = namespace.get(ns_id) or MESOS_LB_NAMESPACE_NAME
            info['ns_id_list'] = [ns_id]
            info['ns_name_list'] = [ns_name]
            merge_data.append(info)
        return merge_data

    def handle_lb_dtail_data(self, request, access_token, project_id, merge_data, cluster, namespace, cluster_envs):
        # 按前端需要二次处理数据
        for i in merge_data:
            i['constraints'] = json.loads(i['data'])
            i['ip_list'] = json.loads(i['ip_list'])
            i['cluster_name'] = cluster.get(i['cluster_id'], i['cluster_id'])
            i['environment'] = cluster_envs.get(i['cluster_id'], '')
            i.pop('data', None)

            # 处理新添加的字段
            data_dict = i['data_dict']
            if data_dict:
                data_dict = json.loads(data_dict)
            else:
                data_dict = {}
            ns = data_dict.get('namespace_id') or data_dict.get('namespace')
            if ns and str(ns).isdigit():
                ns = int(ns)
            ns_name = namespace.get(ns) or MESOS_LB_NAMESPACE_NAME
            i['namespace'] = ns
            i['namespace_name'] = ns_name
            i['network_mode'] = data_dict.get('networkMode')
            i['network_type'] = data_dict.get('networkType')
            i['custom_value'] = data_dict.get('custom_value')
            i['image_url'] = data_dict.get('image_url')
            i['image_version'] = data_dict.get('image_version')
            i['forward_mode'] = data_dict.get('forward_mode')
            i['resources'] = data_dict.get('resources')
            i['instance'] = data_dict.get('instance')
            i['host_port'] = data_dict.get('host_port')
            i['eth_value'] = data_dict.get('eth_value', 'eth1')
            i["use_custom_image_url"] = data_dict.get("use_custom_image_url", False)
            i.pop('data_dict', None)

            status = i.get('status') or LB_DEFAULT_STATUS
            if status == LB_DEFAULT_STATUS:
                i['status'] = status
                i['status_name'] = [LB_STATUS_DICT.get(status)]
                i['status_tips'] = [LB_STATUS_DICT.get(status)]
            else:
                # 已经创建的应用需要查询 bcs 的状态
                lb_res, status_dict = get_lb_status(access_token, project_id, i['name'],
                                                    i['cluster_id'], ns_name, lb_id=i['id'])
                deployment_status = status_dict.get('deployment_status')
                # 用户执行过删除操作
                if status == 'deleted' and not deployment_status:
                    i['status'] = status
                    i['status_name'] = [LB_STATUS_DICT.get(status)]
                    i['status_tips'] = [LB_STATUS_DICT.get(status)]
                else:
                    i['status'] = deployment_status

                    status_name = []
                    status_tips = []
                    status_name.append('deployment:%s' % (
                        status_dict.get('deployment_status') or '--'))
                    status_name.append('application:%s' % (
                        status_dict.get('application_status') or '--'))
                    status_tips.append('deployment:%s' % (
                        status_dict.get('deployment_status_message') or '--'))
                    status_tips.append('application:%s' % (
                        status_dict.get('application_status_message') or '--'))
                    i['status_name'] = status_name
                    i['status_tips'] = status_tips
                    # 停用后，如果不是 deleting 状态，方便前端轮询则需要添加一个中间状态
                    if status == 'deleted' and deployment_status != 'Deleting':
                        i['status'] = 'before_deleting'

            # 可以调用 bcs 删除lb 的情况
            is_delete_lb = True if i['status'] in [
                'Deploying', 'Running', 'Update', 'UpdatePaused', 'UpdateSuspend'] else False
            i['is_delete_lb'] = is_delete_lb

        # 检查是否有集群的相关权限
        if merge_data:
            perm = bcs_perm.Cluster(request, project_id, bcs_perm.NO_RES)
            merge_data = perm.hook_perms(request, project_id, merge_data)
        return merge_data

    def get_project_lb(self, project_id, lb_id=None, cluster_id=None):
        """获取mesos下的所有LB
        """
        lb_info = MesosLoadBlance.objects.filter(
            is_deleted=False, project_id=project_id
        ).order_by('-updated')
        if cluster_id:
            lb_info = lb_info.filter(cluster_id=cluster_id)
        if lb_id:
            lb_info = lb_info.filter(id=lb_id)
        return lb_info.values(
            "id", "project_id", "cluster_id", "namespace_id", "name", "linked_namespace_ids",
            "ip_list", "data", "data_dict", "status", "updated", "created"
        )

    def get_cluster_names_and_envs(self, access_token, project_id):
        """获取集群下名称和环境对应关系
        """
        cluster = paas_cc.get_all_clusters(access_token, project_id, desire_all_data=True)
        cluster = cluster.get('data', {}).get('results') or []
        cluster_names = {i['cluster_id']: i['name'] for i in cluster}
        cluster_envs = {i['cluster_id']: i['environment'] for i in cluster}
        return cluster_names, cluster_envs

    def get_namespace_id_name(self, access_token, project_id):
        """获取命名空间ID和名称对应关系
        """
        namespace = paas_cc.get_namespace_list(access_token, project_id, desire_all_data=True)
        namespace = namespace.get('data', {}).get('results') or []
        namespace = {i['id']: i['name'] for i in namespace}
        return namespace

    def get_lb_list(self, request, project_id, limit=None, offset=None):
        access_token = request.user.token.access_token

        cluster_names, cluster_envs = self.get_cluster_names_and_envs(access_token, project_id)
        namespace = self.get_namespace_id_name(access_token, project_id)

        data = self.get_project_lb(project_id, cluster_id=request.query_params.get("cluster_id"))
        data = [n for n in data if n.get('id')]
        merge_data = self.merge_data(data, namespace)

        total = len(merge_data)
        # 分页查询
        if limit is not None and offset is not None:
            end = offset + limit
            merge_data = merge_data[offset:end]

        # 按前端需要二次处理数据
        merge_data = self.handle_lb_dtail_data(
            request, access_token, project_id, merge_data, cluster_names, namespace, cluster_envs)
        return merge_data, total

    def list(self, request, project_id):
        """获取LB列表
        """
        merge_data, total = self.get_lb_list(request, project_id)
        return Response({
            "code": 0,
            "permissions": {'create': True},
            "data": merge_data
        })

    def list_by_paging(self, request, project_id):
        """lb列表分页查询
        """
        slz = GetLoadBalanceSLZ(data=request.GET)
        slz.is_valid(raise_exception=True)
        data = slz.data

        merge_data, total = self.get_lb_list(
            request, project_id, data['limit'], data['offset'])
        return Response({
            "code": 0,
            "count": total,
            "next": None,
            "previous": None,
            "results": merge_data
        })

    def get_detail(self, request, project_id, lb_id):
        access_token = request.user.token.access_token
        data = self.get_project_lb(project_id, lb_id=lb_id)
        namespace = paas_cc.get_namespace_list(
            access_token, project_id, limit=constants.ALL_LIMIT)
        namespace = namespace.get('data', {}).get('results') or []
        namespace = {i['id']: i['name'] for i in namespace}

        merge_data = self.merge_data(data, namespace)

        # 获取集群名称
        cluster_id = merge_data[0].get('cluster_id')
        cls_res = paas_cc.get_cluster(access_token, project_id, cluster_id)
        cluster_data = cls_res.get('data', {})
        cluster_name = cluster_data.get('name') or cluster_id
        cluster_dict = {cluster_id: cluster_name}
        cluster_envs = {cluster_id: cluster_data.get('environment', '')}

        # 按前端需要二次处理数据
        data = self.handle_lb_dtail_data(
            request, access_token, project_id, merge_data, cluster_dict, namespace, cluster_envs)
        return Response({
            "code": 0,
            "results": data[0]
        })

    def handle_data(self, slz_data):
        """将新增的数据都存储到 data 字段中
        """
        data = {
            'namespace': slz_data['namespace'],
            'namespace_id': slz_data['namespace_id'],
            'networkMode': slz_data['network_mode'],
            'networkType': slz_data['network_type'],
            'custom_value': slz_data['custom_value'],
            'resources': slz_data['resources'],
            'image_url': slz_data['image_url'],
            'image_version': slz_data['image_version'],
            'forward_mode': slz_data['forward_mode'],
            'instance': slz_data['instance'],
            'eth_value': slz_data['eth_value'],
            'host_port': slz_data['host_port'],
            "use_custom_image_url": slz_data.get("use_custom_image_url", False)
        }
        return data

    def can_use_perm(self, request, project_id, cluster_id):
        """检查使用是否有集群的使用权限
        """
        perm = bcs_perm.Cluster(request, project_id, cluster_id)
        perm.can_use(raise_exception=True)

    def create(self, request, project_id):
        slz = LoadBalancesSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.data
        creator = request.user.username

        # 针对mesos，权限相关放大到集群即可
        self.can_use_perm(request, project_id, data['cluster_id'])

        handled_data = self.handle_data(data)
        with activity_client.ContextActivityLogClient(
            project_id=project_id,
            user=creator,
            resource_type="lb",
            resource_id=data["cluster_id"],
            resource=data['name'],
            description=_("创建LoadBalance"),
            extra=json.dumps(data),
        ).log_add() as ual_client:
            MesosLoadBlance.objects.create(
                project_id=project_id,
                cluster_id=data['cluster_id'],
                namespace_id=data['namespace_id'],
                namespace=data['namespace'],
                name=data['name'],
                creator=creator,
                updator=creator,
                ip_list=json.dumps(data['ip_list']),
                data=json.dumps(data['constraints']),
                data_dict=json.dumps(handled_data)
            )

            ual_client.update_log(activity_status='succeed')
        return Response({"code": 0, "message": "ok"})

    def get(self, request, project_id, lb_id):
        access_token = request.user.token.access_token
        data_list = self.get_project_lb(project_id, lb_id=lb_id)
        if not data_list:
            raise error_codes.CheckFailed(_("记录不存在!"), replace=True)
        data = data_list[0]
        ip_list = json.loads(data.get('ip_list', '[]'))
        cluster_id = data.get('cluster_id')
        constraints = json.loads(data.get('data'))
        # 获取集群名称
        cls_res = paas_cc.get_cluster(access_token, project_id, cluster_id)
        cluster_data = cls_res.get('data') or {}
        cluster_name = cluster_data.get('name') or cluster_id
        ret_data = {
            'name': data.get('name'),
            'ip_list': ip_list,
            'cluster_name': cluster_name,
            'constraints': constraints
        }
        return Response({"code": 0, "data": ret_data})

    def update(self, request, project_id, lb_id):
        slz = UpdateLoadBalancesSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.data
        updater = request.user.username

        # 检查是否有命名空间的使用权限
        self.can_use_perm(request, project_id, data['cluster_id'])

        handled_data = self.handle_data(data)
        with activity_client.ContextActivityLogClient(
            project_id=project_id,
            user=updater,
            resource_type="lb",
            resource=data['name'],
            resource_id=data['cluster_id'],
            description=_("更新LoadBalance"),
            extra=json.dumps(data),
        ).log_modify() as ual_client:
            MesosLoadBlance.objects.filter(id=lb_id).update(
                project_id=project_id,
                cluster_id=data['cluster_id'],
                namespace_id=data['namespace_id'],
                namespace=data['namespace'],
                name=data['name'],
                updator=updater,
                ip_list=json.dumps(data['ip_list']),
                data=json.dumps(data['constraints']),
                data_dict=json.dumps(handled_data)
            )

            ual_client.update_log(activity_status="succeed")
        return Response({"code": 0, "message": "ok"})

    def validate_lb(self, request, project_id, lb_id, type, is_check_use=True):
        data = self.get_project_lb(project_id, lb_id=lb_id)
        if not data:
            return False, {
                "code": 0,
                "message": _("LoadBalance[id:{}]不存在").format(lb_id)
            }
        merge_data = self.merge_data(data, {})
        if not merge_data:
            return False, {
                "code": 0,
                "message": _("LoadBalance[id:{}]已经被删除").format(lb_id),
                "data": merge_data
            }
        self.lb_data = merge_data[0]
        self.lb_data.pop('updated', None)
        self.lb_data.pop('created', None)
        cur_status = self.lb_data.get('status') or LB_DEFAULT_STATUS

        # 检查是否有命名空间的使用权限
        data_dict = self.lb_data.get('data_dict')
        if data_dict:
            data_dict = json.loads(data_dict)
        else:
            data_dict = {}
        if is_check_use:
            self.can_use_perm(request, project_id, self.lb_data.get('cluster_id'))
        # 查询 taskgroup
        if type in ['get_taskgroup', 'delete_by_bcs']:
            if cur_status in [LB_DEFAULT_STATUS, 'deleted']:
                return False, {
                    "code": 0,
                    "message": _("LoadBalance[id:{}]还未创建").format(lb_id),
                    "data": []
                }
            return True, {}
        # 创建、删除操作
        if cur_status not in [LB_DEFAULT_STATUS, 'deleted']:
            lb_name = self.lb_data.get('name')
            msg = _("不能被删除") if type == 'delete' else _("不能被重复创建")
            return False, {
                "code": 400,
                "message": _("LoadBalance[{}]已经在后台创建，{}").format(lb_name, msg),
                "data": []
            }
        return True, {}

    def delete(self, request, project_id, lb_id):
        # 判断 lb 的状态
        validate_res, validate_msg = self.validate_lb(
            request, project_id, lb_id, "delete")
        if not validate_res:
            return Response(validate_msg)
        username = request.user.username
        with activity_client.ContextActivityLogClient(
            project_id=project_id,
            user=username,
            resource_type="lb",
            resource=lb_id,
            resource_id=lb_id,
        ).log_modify() as ual_client:
            lb_info = MesosLoadBlance.objects.filter(id=lb_id)
            lb_info.update(
                is_deleted=True,
                deleted_time=datetime.datetime.now(),
                name="%s:deleted:%s" % (lb_id, lb_info[0].name)
            )
            ual_client.update_log(
                activity_status='succeed',
                description=_("LB[{}]删除成功").format(lb_id),
            )
        return Response({
            "code": 0,
            "message": "删除成功!",
        })

    def create_by_bcs(self, request, project_id, lb_id):
        # 判断 lb 的状态
        validate_res, validate_msg = self.validate_lb(
            request, project_id, lb_id, "create")
        if not validate_res:
            return Response(validate_msg)
        # 调用 bcs API 创建lb
        username = request.user.username
        access_token = request.user.token.access_token
        with activity_client.ContextActivityLogClient(
            project_id=project_id,
            user=username,
            resource_type="lb",
            resource=self.lb_data.get('name'),
            resource_id=lb_id,
            extra=json.dumps(self.lb_data)
        ).log_start() as ual_client:
            cc_app_id = request.project['cc_app_id']
            # 添加是否自定义镜像
            params = {"use_custom_image_url": self.lb_data.get("use_custom_image_url", False)}
            result, error_msg = handle_lb(
                username, access_token, project_id, self.lb_data, cc_app_id, **params)
            ual_client.update_log(
                activity_status='succeed' if result else 'failed',
                description=_("启动LoadBalance：{}").format(error_msg or _("已下发配置")),
            )
        if result:
            # 创建成功则更新配置中心的lb状态
            MesosLoadBlance.objects.filter(id=lb_id).update(status="created")
            return Response({
                "code": 0,
                "message": "ok",
                "data": {}
            })
        # 失败则返回错误信息
        msg = u"创建失败:%s" % (error_msg)
        return Response({
            "code": 500,
            "message": msg,
            "data": {'is_update': False}
        })

    def delete_by_bcs(self, request, project_id, lb_id):
        # 判断 lb 的状态
        validate_res, validate_msg = self.validate_lb(
            request, project_id, lb_id, "delete_by_bcs")
        if not validate_res:
            return Response(validate_msg)
        # 根据 lb 获取 Deployment的信息
        lb_name = self.lb_data.get("name")
        cluster_id = self.lb_data.get('cluster_id')

        # 查询 namespace
        data_dict = self.lb_data.get('data_dict')
        if data_dict:
            data_dict = json.loads(data_dict)
        else:
            data_dict = {}
        # 兼容已存在的数据
        namespace = get_namespace_name(request.user.token.access_token, project_id, data_dict)

        username = request.user.username
        access_token = request.user.token.access_token
        # enforce delete flag, 1: enforce delete 0: not enforce
        enforce = request.query_params.get('enforce', 0)
        with activity_client.ContextActivityLogClient(
            project_id=project_id,
            user=username,
            resource_type="lb",
            resource=lb_name,
            resource_id=lb_id,
            extra=json.dumps(self.lb_data)
        ).log_stop() as ual_client:
            result = delete_lb_by_bcs(
                access_token, project_id, cluster_id, namespace, lb_name, lb_id, enforce=enforce)
            ual_client.update_log(
                activity_status='succeed' if result.get('result') else 'failed',
                description=_("停止LoadBalance：{}").format(result.get('message')),
            )
        return Response(result)

    def get_filed(self, project_kind):
        field_list = [
            "data.metadata.name",
            "data.containerStatuses.status",
            "data.containerStatuses.image",
            "data.containerStatuses.name",
            "data.status",
            "data.containerStatuses.containerID",
            "data.message",
            "data.startTime",
            "data.hostIP",
            "data.podIP"
        ]
        if project_kind == 2:
            field = ','.join(field_list)
        else:
            field = ""

        return field

    def get_taskgroup(self, request, project_id, lb_id):
        # 判断 lb 的状态
        validate_res, validate_msg = self.validate_lb(
            request, project_id, lb_id, "get_taskgroup", is_check_use=False)
        if not validate_res:
            return Response(validate_msg)

        # 获取kind
        flag, project_kind = self.get_project_kind(request, project_id)
        if not flag:
            return project_kind
        # 根据 lb 获取 Deployment的信息
        name = self.lb_data.get("name")
        cluster_id = self.lb_data.get('cluster_id')
        data_dict = self.lb_data.get('data_dict')
        # 查询 namespace
        if data_dict:
            data_dict = json.loads(data_dict)
        else:
            data_dict = {}
        namespace = get_namespace_name(request.user.token.access_token, project_id, data_dict)
        # 获取taskgroup或者group
        field = self.get_filed(project_kind)
        rc_names = self.get_rc_name_by_deployment_base(
            request, project_id, cluster_id, name,
            project_kind=project_kind, namespace=namespace
        )
        rc_names = list(set(rc_names)) or ["None"]
        flag, resp = self.get_pod_or_taskgroup(
            request, project_id, cluster_id,
            field=field,
            app_name=",".join(rc_names),
            ns_name=namespace,
        )
        if not flag:
            return resp
        if project_kind == 2:
            ret_data = self.get_task_group_info_base(resp, namespace=namespace)
        else:
            ret_data = []
        # 处理数据方便前台使用
        return APIResponse({
            "data": ret_data
        })
