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
from datetime import datetime

from django.db import transaction
from rest_framework import viewsets
from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _

from backend.activity_log import client as log_client
from backend.accounts import bcs_perm
from backend.components import paas_cc
from backend.apps.network.serializers import NginxIngressSLZ, NginxIngressUpdateSLZ
from backend.bcs_k8s.app.views import AppViewBase
from backend.bcs_k8s.app.models import App
from backend.utils.views import with_code_wrapper, AccessTokenMixin, ProjectMixin
from backend.apps.network.models import K8SLoadBlance
from backend.apps.cluster.serializers import NodeLabelSLZ, NodeLabelUpdateSLZ
from backend.apps.cluster.models import NodeLabel
from backend.components.bcs.k8s import K8SClient
from backend.bcs_k8s.helm.models import ChartVersion, Chart
from backend.apps.application.utils import APIResponse
from backend.components.bcs import k8s
from backend.apps.network.utils import render_helm_values
from backend.apps.network.constants import K8S_LB_LABEL, K8S_LB_NAME
from backend.apps.cluster.constants import DEFAULT_SYSTEM_LABEL_KEYS
from backend.utils.error_codes import error_codes
from backend.utils.renderers import BKAPIRenderer

logger = logging.getLogger(__name__)


class NginxIngressBase(AccessTokenMixin, ProjectMixin, viewsets.ModelViewSet):
    renderer_classes = (BKAPIRenderer,)

    def get_ns_info(self, request, ns_id):
        result = paas_cc.get_namespace(
            request.user.token.access_token, request.project["project_id"], ns_id)
        if result.get("code") != 0:
            raise error_codes.APIError.f(result.get("message"), replace=True)

        return result["data"]

    @property
    def chart_info(self):
        chart = Chart.objects.filter(
            name=K8S_LB_NAME, repository__project_id=self.project_id
        ).order_by("defaultChartVersion")
        if not chart:
            raise error_codes.CheckFailed(_("Chart不存在"))
        return chart[0]

    @property
    def chart_version(self):
        chart = self.chart_info
        return chart.defaultChartVersion

    def create_node_label_via_bcs(self, request, project_id, cluster_id, node_id_labels={}):
        """调用BCS服务创建节点标签
        """
        client = K8SClient(
            request.user.token.access_token, project_id, cluster_id, None)
        node_list = paas_cc.get_node_list(
            request.user.token.access_token, project_id, cluster_id)
        if node_list.get("code") != 0:
            raise error_codes.APIError(_("查询节点失败，请联系管理员处理!"))
        results = node_list.get("data", {}).get("results", [])
        if not results:
            raise error_codes.APIError(_("当前集群下没有节点信息!"))
        # compose id: ip
        node_id_ip = {
            info["id"]: info["inner_ip"]
            for info in results
            if str(info["id"]) in node_id_labels.keys()
        }
        for node_id, ip in node_id_ip.items():
            k8s_resp = client.get_node_detail(ip)
            if k8s_resp.get("code") != 0:
                raise error_codes.APIError.f(k8s_resp.get("message"), replace=True)
            exist_metadata = (k8s_resp.get("data") or {}).get("metadata") or {}
            exist_labels = exist_metadata.get("labels") or {}
            if node_id_labels[str(node_id)] == "del":
                exist_labels.pop("nodetype", None)
            else:
                exist_labels.update(K8S_LB_LABEL)
            exist_labels["$patch"] = "replace"
            resp = client.create_node_labels(ip, exist_labels)
            if resp.get("code") != 0:
                raise error_codes.APIError(_("节点打标签异常,请联系管理员处理!"))

    def node_label(self, request, data, with_bcs=True):
        """节点打标签
        """
        many_data = []
        ip_info = json.loads(data["ip_info"])
        node_id_labels = {}
        existed_node_label_info = NodeLabel.objects.filter(
            node_id__in=[node_id for node_id in ip_info]
        )
        existed_node_id_list = [info.node_id for info in existed_node_label_info]
        for node_id in ip_info:
            node_id_labels[node_id] = K8S_LB_LABEL
            if int(node_id) in existed_node_id_list:
                continue
            item = {
                "project_id": data["project_id"],
                "cluster_id": data["cluster_id"],
                "node_id": node_id,
                "labels": json.dumps(K8S_LB_LABEL),
                "creator": data["creator"],
                "updator": data["updator"]
            }
            many_data.append(item)
            node_id_labels[node_id] = "add"
        # create node label via bcs
        if with_bcs:
            self.create_node_label_via_bcs(
                request, data["project_id"], data["cluster_id"], node_id_labels)

        serializer = NodeLabelSLZ(data=many_data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # 更新
        for info in existed_node_label_info:
            labels = json.loads(info.labels or '{}')
            labels.update(K8S_LB_LABEL)
            info.labels = json.dumps(labels)
            info.save()

    def get_k8s_lb_info(self, app_id):
        k8s_lbs = K8SLoadBlance.objects.filter(id=app_id, is_deleted=False)
        if not k8s_lbs:
            raise error_codes.CheckFailed(_("没有查询到LB版本信息"))
        return k8s_lbs[0]

    def get_node_labels(self, node_id_list):
        return NodeLabel.objects.filter(node_id__in=node_id_list)

    def get_k8s_bcs_app(self, ns_id, chart):
        app_instances = App.objects.filter(namespace_id=ns_id, chart=chart)
        if not app_instances:
            logger.exception('Helm app not found, ns_id: %s' % ns_id)
            return None
        return app_instances[0]

    def render_yaml(self, access_token, project_id, cluster_id, data, namespace_info):
        """渲染helm values配置
        """
        replica_count = len(json.loads(data["ip_info"]))
        return render_helm_values(
            access_token, project_id, cluster_id, data["protocol_type"], replica_count, namespace_info["name"])

    def get_cluster_id_name_map(self, access_token, project_id):
        cluster_list = paas_cc.get_all_clusters(access_token, project_id)
        data = cluster_list.get("data", {}).get("results") or []
        return {i["cluster_id"]: i for i in data}

    def get_node_info(self, access_token, project_id, cluster_id):
        node_list = paas_cc.get_node_list(access_token, project_id, cluster_id)
        if node_list.get("code") != 0:
            raise error_codes.APIError(_("查询节点失败，请联系管理员处理!"))
        results = node_list.get("data", {}).get("results", [])
        if not results:
            raise error_codes.APIError(_("当前集群下没有节点信息!"))

        return {info["id"]: info for info in results}

    def check_used_node(self, node_id_list):
        """检查节点是否被其它LB占用
        """
        k8s_lb_info = K8SLoadBlance.objects.all()
        existed_node_id_list = []
        for info in k8s_lb_info:
            ip_info = json.loads(info.ip_info)
            item = [node_id for node_id in ip_info if ip_info[node_id]]
            existed_node_id_list.extend(item)
        # diff
        diff = set(existed_node_id_list) & set(node_id_list)
        if diff:
            raise error_codes.CheckFailed(_("不允许独享节点分属不同的LB，请检查后重试"))

    def get_all_namespace(self, access_token, project_id):
        resp = paas_cc.get_namespace_list(access_token, project_id, desire_all_data=True)
        if resp.get("code") != 0:
            raise error_codes.APIError.f(resp.get("message"))
        return {item["id"]: item for item in resp.get("data", {}).get("results") or []}


@with_code_wrapper
class NginxIngressListCreateViewSet(NginxIngressBase):
    queryset = K8SLoadBlance.objects.all()
    serializer_class = NginxIngressSLZ

    def get_queryset(self):
        return super(NginxIngressListCreateViewSet, self).get_queryset().filter(is_deleted=False)

    def list(self, request, project_id):
        access_token = request.user.token.access_token
        queryset = self.get_queryset().filter(project_id=project_id)
        cluster_id = request.query_params.get("cluster_id")
        if cluster_id:
            queryset = queryset.filter(cluster_id=cluster_id)
        cluster_id_name_map = self.get_cluster_id_name_map(access_token, project_id)
        ns_id_name_map = self.get_all_namespace(access_token, project_id)
        results = []
        for info in queryset.order_by("-updated").values():
            info["cluster_name"] = cluster_id_name_map.get(info["cluster_id"], {}).get("name")
            info["environment"] = cluster_id_name_map.get(info["cluster_id"], {}).get("environment")
            info["namespace_name"] = ns_id_name_map.get(int(info["namespace_id"]), {}).get("name")
            results.append(info)
        # 添加权限
        if results:
            perm = bcs_perm.Namespace(request, project_id, bcs_perm.NO_RES)
            results = perm.hook_perms(results, ns_id_flag='namespace_id', ns_name_flag='namespace_name')
        resp = {
            "count": len(results),
            "results": results
        }
        return Response(resp)

    def create_lb_conf(self, data):
        if K8SLoadBlance.objects.filter(
                cluster_id=data["cluster_id"], namespace_id=data["namespace_id"], name=data["name"]):
            return
        serializer = NginxIngressSLZ(data=data)
        serializer.is_valid(raise_exception=True)
        # save nginx ingress controller configure
        serializer.save()

    @transaction.atomic
    def pre_create(self, request, data):
        # 1. save lb config
        self.create_lb_conf(data)
        # 2. create label for node; format is key: value is nodetype: lb
        self.node_label(request, data)
        # 3. render values.yaml file
        namespace_info = self.get_ns_info(request, data["namespace_id"])
        value_file_content = self.render_yaml(
            request.user.token.access_token, data["project_id"], data["cluster_id"], data, namespace_info)
        return value_file_content, namespace_info

    def check_namespace_used(self, cluster_id, namespace_id):
        """校验集群下命名空间是否已经被占用，如果占用则提示已经被使用
        """
        if K8SLoadBlance.objects.filter(
                cluster_id=cluster_id, namespace_id=namespace_id, name=K8S_LB_NAME).exists():
            raise error_codes.CheckFailed(_("命名空间已经被占用，请选择其他命名空间"))

    def create(self, request, project_id):
        """针对nginx的实例化，主要有下面几步:
        1. 存储用户设置的配置
        2. 根据用户选择的节点打标签
        3. 根据透露给用户的选择，渲染values.yaml文件
        4. 实例化controller相关配置
        """
        data = dict(request.data)
        data.update({
            "project_id": project_id,
            "creator": request.user.username,
            "updator": request.user.username,
            "name": K8S_LB_NAME
        })
        ns_id = data['namespace_id']
        # 检查命名空间是否被占用
        self.check_namespace_used(data['cluster_id'], ns_id)

        perm = bcs_perm.Namespace(request, project_id, ns_id)
        perm.can_use(raise_exception=True)
        # 检查节点ID是否已经存在，不允许占用独享的节点
        # ip_info = json.loads(data["ip_info"])
        # self.check_used_node(ip_info.keys())

        value_file_content, namespace_info = self.pre_create(request, data)

        user_log = log_client.ContextActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type='lb',
            resource="%s:%s" % (data["cluster_id"], data["namespace_id"]),
            extra=json.dumps(data)
        )
        # 4. helm apply
        try:
            helm_app_info = App.objects.initialize_app(
                access_token=request.user.token.access_token,
                name=K8S_LB_NAME,
                project_id=project_id,
                cluster_id=data["cluster_id"],
                namespace_id=data["namespace_id"],
                namespace=namespace_info["name"],
                chart_version=self.chart_version,
                answers=[],
                customs=[],
                valuefile=value_file_content,
                creator=request.user.username,
                updator=request.user.username
            )
        except Exception as err:
            logger.exception('Create helm app error, detail: %s' % err)
            helm_app_info = None
        if helm_app_info:
            if helm_app_info.transitioning_result:
                user_log.log_add(activity_status="succeed")
                return APIResponse({"message": _("创建成功!")})
            else:
                user_log.log_add(activity_status="failed")
                raise error_codes.CheckFailed(_("创建失败，请查看实例详情!"))
        else:
            # 5. 如果失败删除k8s lb实例
            K8SLoadBlance.objects.filter(
                cluster_id=data["cluster_id"], namespace_id=data["namespace_id"], name=data["name"]
            ).delete()

        user_log.log_add(activity_status="failed")
        raise error_codes.CheckFailed(_("创建失败，已通知管理员处理!"))


@with_code_wrapper
class NginxIngressRetrieveUpdateViewSet(NginxIngressBase):
    queryset = K8SLoadBlance.objects.all()
    serializer_class = NginxIngressSLZ

    def retrieve(self, request, project_id, pk):
        details = self.queryset.filter(id=pk, project_id=project_id, is_deleted=False).values()
        if not details:
            raise error_codes.CheckFailed(_("没有查询到实例信息，请联系管理员处理"))
        data = details[0]

        perm = bcs_perm.Namespace(request, project_id, data["namespace_id"])
        perm.can_use(raise_exception=True)

        access_token = request.user.token.access_token
        cluster_id_name_map = self.get_cluster_id_name_map(access_token, project_id)
        data["cluster_name"] = cluster_id_name_map[data["cluster_id"]]["name"]
        ip_info = json.loads(data["ip_info"])
        node_id_info_map = self.get_node_info(access_token, project_id, data["cluster_id"])
        render_ip_info = []
        for info in ip_info:
            item = {
                "id": info,
                "inner_ip": node_id_info_map[int(info)]["inner_ip"],
                "unshared": ip_info[info]
            }
            render_ip_info.append(item)
        data["ip_info"] = json.dumps(render_ip_info)
        return Response(data)

    def get_update_node_info(self, request, data):
        """比较先前和现在节点的获取要添加和删除的节点信息
        """
        lb_conf = self.get_k8s_lb_info(data["id"])
        pre_ip_info = json.loads(lb_conf.ip_info)
        update_ip_info = json.loads(data["ip_info"])
        common_node_id_set = set([
            node_id
            for node_id in pre_ip_info
            if node_id in update_ip_info
        ])
        # 要删除的节点
        delete_node_id_list = list(set(pre_ip_info.keys()) - common_node_id_set)
        add_node_id_list = list(set(update_ip_info.keys()) - common_node_id_set)
        return lb_conf, delete_node_id_list, add_node_id_list

    def update_node_label_list(self, request, node_labels, op="add"):
        """通过op参数判断是添加还是删除label
        """
        username = request.user.username
        node_id_labels = {}
        for info in node_labels:
            labels = json.loads(info.labels or '{}')
            if op == "del":
                labels.pop("nodetype", None)
            else:
                labels.update(K8S_LB_LABEL)
            info.labels = json.dumps(labels)
            info.updator = username
            info.save()
            node_id_labels[str(info.node_id)] = op
        return node_id_labels

    def update_lb_conf(self, instance, ip_info, protocol_type, updator):
        instance.ip_info = ip_info
        instance.protocol_type = protocol_type
        instance.updator = updator
        instance.save()

    def delete_node_label(self, request, delete_node_id_list, project_id, lb_conf):
        """删除节点标签
        """
        delete_node_instances = self.get_node_labels(delete_node_id_list)
        node_id_labels = self.update_node_label_list(request, delete_node_instances, op="del")
        self.create_node_label_via_bcs(request, project_id, lb_conf.cluster_id, node_id_labels)

    def add_node_label(self, request, add_node_id_list, project_id, lb_conf):
        save_label_data = {
            "project_id": project_id,
            "cluster_id": lb_conf.cluster_id,
            "creator": request.user.username,
            "updator": request.user.username,
            "ip_info": json.dumps(add_node_id_list)
        }
        self.node_label(request, save_label_data)
        add_node_instances = self.get_node_labels(add_node_id_list)
        node_id_labels = self.update_node_label_list(request, add_node_instances, op="add")
        self.create_node_label_via_bcs(request, project_id, lb_conf.cluster_id, node_id_labels)

    def update_check_node_id(self, lb_conf, data):
        existed_ip_info = json.loads(lb_conf.ip_info).keys()
        req_ip_info = data.get("ip_info", {}).keys()
        if req_ip_info:
            diff = list(set(req_ip_info) - set(existed_ip_info))
            self.check_used_node(diff)

    @transaction.atomic
    def update(self, request, project_id, pk):
        """
        更新LB配置，包含下面几种场景
        1. 增加/减少LB协议类型
        2. 增加/减少节点数量(标签+replica)
        """
        req_data = dict(request.data)
        req_data.update({"id": pk, "updator": request.user.username})
        serializer = NginxIngressUpdateSLZ(data=req_data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        lb_conf, delete_node_id_list, add_node_id_list = self.get_update_node_info(request, data)

        perm = bcs_perm.Namespace(request, project_id, lb_conf.namespace_id)
        perm.can_use(raise_exception=True)
        # 判断调整的节点是否已经存在，并且是独享的
        # self.update_check_node_id(lb_conf, data)

        # 删除节点配置
        if delete_node_id_list:
            self.delete_node_label(request, delete_node_id_list, project_id, lb_conf)
        # 添加节点配置
        if add_node_id_list:
            self.add_node_label(request, add_node_id_list, project_id, lb_conf)

        # 更新lb
        self.update_lb_conf(lb_conf, data["ip_info"], data["protocol_type"], request.user.username)
        app_instance = self.get_k8s_bcs_app(lb_conf.namespace_id, self.chart_info)
        if not app_instance:
            return APIResponse({"code": 400, "message": _("没有查询到应用信息")})

        data["namespace_id"] = lb_conf.namespace_id
        namespace_info = self.get_ns_info(request, data["namespace_id"])
        valuefile = self.render_yaml(
            request.user.token.access_token, project_id, lb_conf.cluster_id, data, namespace_info)
        user_log = log_client.ContextActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type='lb',
            resource="%s:%s" % (lb_conf.cluster_id, lb_conf.namespace_id),
            resource_id=pk,
            extra=json.dumps(data)
        )
        updated_instance = app_instance.upgrade_app(
            access_token=request.user.token.access_token,
            chart_version_id=self.chart_version.id,
            answers=[], customs=[],
            valuefile=valuefile,
            updator=request.user.username
        )
        if updated_instance.transitioning_result:
            user_log.log_modify(activity_status="succeed")
            return APIResponse({"message": "更新成功!"})
        user_log.log_modify(activity_status="failed")
        return APIResponse({"code": 400, "message": updated_instance.transitioning_message})

    def delete_lb_conf(self, lb_conf):
        """标识此条记录被删除
        """
        lb_conf.is_deleted = True
        lb_conf.deleted_time = datetime.now()
        # 删除的名称格式为id:deleted
        lb_conf.name = "%s:deleted" % lb_conf.id
        lb_conf.save()

    @transaction.atomic
    def destroy(self, request, project_id, pk):
        """删除nginx ingress
        1. 标识LB配置
        2. 删除节点标签nodetype
        3. 删除helm记录
        """
        lb_conf = self.get_object()

        perm = bcs_perm.Namespace(request, project_id, lb_conf.namespace_id)
        perm.can_use(raise_exception=True)

        # 标识LB被删除
        self.delete_lb_conf(lb_conf)
        # 删除节点标签
        delete_node_id_list = [node_id for node_id in json.loads(lb_conf.ip_info)]
        self.delete_node_label(request, delete_node_id_list, project_id, lb_conf)
        # 删除helm
        app_instance = self.get_k8s_bcs_app(lb_conf.namespace_id, self.chart_info)
        if not app_instance:
            return APIResponse({"message": _("删除成功")})

        user_log = log_client.ContextActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type='lb',
            resource="%s:%s" % (lb_conf.cluster_id, lb_conf.namespace_id),
            resource_id=pk
        )
        app_instance.destroy(
            username=request.user.username,
            access_token=request.user.token.access_token
        )
        # 因为是helm中是异步过程，因此，放到后台处理
        # if App.objects.filter(id=app_instance.id).exists():
        #     user_log.log_delete(activity_status="failed")
        #     return APIResponse({"code": 400, "message": app_instance.transitioning_message})
        user_log.log_delete(activity_status="succeed")
        return APIResponse({"message": _("任务下发成功!")})


class NginxIngressListNamespceViewSet(NginxIngressBase):

    def list(self, request, project_id, cluster_id):
        used_ns_id_list = K8SLoadBlance.objects.filter(
            project_id=project_id, cluster_id=cluster_id, is_deleted=False
        ).values("namespace_id")
        return APIResponse({"data": [info["namespace_id"] for info in used_ns_id_list]})
