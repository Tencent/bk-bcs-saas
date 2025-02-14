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
import json
import logging
from datetime import datetime

from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response

from backend.bcs_web.audit_log import client as log_client
from backend.components.bcs.k8s import K8SClient
from backend.container_service.clusters.base import utils as cluster_utils
from backend.container_service.clusters.base.models import CtxCluster
from backend.container_service.clusters.models import NodeLabel
from backend.container_service.clusters.serializers import NodeLabelSLZ
from backend.helm.app.models import App
from backend.helm.helm.models import ChartVersion
from backend.resources.namespace import Namespace
from backend.resources.namespace import utils as ns_utils
from backend.uniapps.application.utils import APIResponse
from backend.uniapps.network import constants, serializers
from backend.uniapps.network.constants import K8S_LB_CHART_NAME, K8S_LB_LABEL, K8S_LB_NAMESPACE
from backend.uniapps.network.models import K8SLoadBlance
from backend.uniapps.network.serializers import NginxIngressSLZ, UpdateK8SLoadBalancerSLZ
from backend.uniapps.network.views.charts.releases import HelmReleaseMixin
from backend.utils.error_codes import error_codes
from backend.utils.renderers import BKAPIRenderer

logger = logging.getLogger(__name__)


class NginxIngressBase(viewsets.ModelViewSet):
    renderer_classes = (BKAPIRenderer,)

    def get_chart_version(self, project_id, version):
        try:
            chart_version = ChartVersion.objects.get(
                name=K8S_LB_CHART_NAME,
                chart__repository__project_id=project_id,
                version=version,
                chart__repository__name="public-repo",
            )
        except ChartVersion.DoesNotExist:
            raise error_codes.ResNotFoundError(_("没有查询到chart版本: {}").format(version))
        return chart_version

    def create_node_label_via_bcs(self, request, project_id, cluster_id, node_id_labels={}):
        """调用BCS服务创建节点标签"""
        nodes = cluster_utils.get_cluster_nodes(request.user.token.access_token, project_id, cluster_id)
        # compose id: ip
        node_id_ip = {info["id"]: info["inner_ip"] for info in nodes if str(info["id"]) in node_id_labels.keys()}
        client = K8SClient(request.user.token.access_token, project_id, cluster_id, None)
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
        """节点打标签"""
        many_data = []
        ip_info = json.loads(data["ip_info"])
        node_id_labels = {}
        existed_node_label_info = NodeLabel.objects.filter(node_id__in=[node_id for node_id in ip_info])
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
                "updator": data["updator"],
            }
            many_data.append(item)
            node_id_labels[node_id] = "add"
        # create node label via bcs
        if with_bcs:
            self.create_node_label_via_bcs(request, data["project_id"], data["cluster_id"], node_id_labels)

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

    def get_cluster_id_name_map(self, access_token, project_id):
        cluster_list = cluster_utils.get_clusters(access_token, project_id)
        return {i["cluster_id"]: i for i in cluster_list}

    def get_nodes_id_ip(self, access_token, project_id, cluster_id):
        nodes = cluster_utils.get_cluster_nodes(access_token, project_id, cluster_id)
        return {info["id"]: info for info in nodes}


class NginxIngressListCreateViewSet(NginxIngressBase, HelmReleaseMixin):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)
    queryset = K8SLoadBlance.objects.all()
    serializer_class = NginxIngressSLZ

    def get_queryset(self):
        return super(NginxIngressListCreateViewSet, self).get_queryset().filter(is_deleted=False)

    def get_ns_id_name(self, access_token, project_id):
        ns_list = ns_utils.get_cc_namespaces(access_token, project_id)
        return {ns["id"]: ns["name"] for ns in ns_list}

    def _set_lb_namespace(self, lb, ns_id_name):
        """更新lb中namespace
        兼容逻辑，后续可以删除
        如果lb中namespace为空，则通过namespace id查询到namespace，然后更新namespace
        """
        namespace = lb["namespace"]
        if not lb["namespace"]:
            namespace = ns_id_name.get(lb["namespace_id"])
            lb["namespace"] = namespace
        lb["namespace_name"] = namespace

    def list(self, request, project_id):
        access_token = request.user.token.access_token
        queryset = self.get_queryset().filter(project_id=project_id)
        cluster_id = request.query_params.get("cluster_id")
        if cluster_id:
            queryset = queryset.filter(cluster_id=cluster_id)
        cluster_id_name_map = self.get_cluster_id_name_map(access_token, project_id)
        results = []
        ns_id_name = self.get_ns_id_name(access_token, project_id)

        for lb in queryset.order_by("-updated").values():
            lb["cluster_name"] = cluster_id_name_map.get(lb["cluster_id"], {}).get("name")
            lb["environment"] = cluster_id_name_map.get(lb["cluster_id"], {}).get("environment")
            self._set_lb_namespace(lb, ns_id_name)
            release = self.get_helm_release(
                cluster_id, K8S_LB_CHART_NAME, namespace_id=lb["namespace_id"], namespace=lb["namespace"]
            )
            lb["chart"] = {"name": K8S_LB_CHART_NAME, "version": release.get_current_version() if release else ""}
            results.append(lb)
        # TODO: 后续添加权限相关
        resp = {"count": len(results), "results": results}
        return Response(resp)

    def create_lb_conf(self, data):
        if K8SLoadBlance.objects.filter(
            cluster_id=data["cluster_id"], namespace_id=data["namespace_id"], name=data["name"]
        ):
            return
        serializer = NginxIngressSLZ(data=data)
        serializer.is_valid(raise_exception=True)
        # save nginx ingress controller configure
        serializer.save()

    def get_or_create_namespace(self, request, project_id, cluster_id):
        """创建bcs-system命名空间，如果不存在，则创建；如果存在，则直接返回数据"""
        ctx_cluster = CtxCluster.create(token=request.user.token.access_token, id=cluster_id, project_id=project_id)
        return Namespace(ctx_cluster).get_or_create_cc_namespace(K8S_LB_NAMESPACE, request.user.username)

    @transaction.atomic
    def pre_create(self, request, data):
        # 1. 创建bcs-system命名空间
        ns_info = self.get_or_create_namespace(request, data["project_id"], data["cluster_id"])
        data.update({"namespace": ns_info["name"], "namespace_id": ns_info["namespace_id"]})
        # 2. save lb config
        self.create_lb_conf(data)
        # 3. create label for node; format is key: value is nodetype: lb
        self.node_label(request, data)

        return {"ns_info": ns_info}

    def validate_lb(self, cluster_id):
        """校验集群下是否有LB，如果已经存在，现阶段不允许再次创建"""
        if K8SLoadBlance.objects.filter(cluster_id=cluster_id, name=K8S_LB_CHART_NAME).exists():
            raise ValidationError(_("集群下已存在LB，不允许再次创建"))

    def create(self, request, project_id):
        """针对nginx的实例化，主要有下面几步:
        1. 存储用户设置的配置
        2. 根据用户选择的节点打标签
        3. 根据透露给用户的选择，渲染values.yaml文件
        4. 实例化controller相关配置
        """
        slz = serializers.CreateK8SLoadBalancerSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        data.update(
            {
                "project_id": project_id,
                "creator": request.user.username,
                "updator": request.user.username,
                "name": K8S_LB_CHART_NAME,
                "ip_info": json.dumps(data["ip_info"]),
            }
        )
        # 检查命名空间是否被占用
        self.validate_lb(data["cluster_id"])

        created_data = self.pre_create(request, data)
        ns_info = created_data["ns_info"]

        user_log = log_client.ContextActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type='lb',
            resource="%s:%s" % (data["cluster_id"], data["namespace_id"]),
            extra=json.dumps(data),
        )
        # 4. helm apply
        try:
            access_token = request.user.token.access_token
            sys_variables = self.collect_system_variable(access_token, project_id, ns_info["namespace_id"])
            helm_app_info = App.objects.initialize_app(
                access_token=access_token,
                name=K8S_LB_CHART_NAME,
                project_id=project_id,
                cluster_id=data["cluster_id"],
                namespace_id=ns_info["namespace_id"],
                namespace=ns_info["name"],
                chart_version=self.get_chart_version(project_id, data["version"]),
                answers=[],
                customs=[],
                cmd_flags=[],
                valuefile=data["values_content"],
                creator=request.user.username,
                updator=request.user.username,
                sys_variables=sys_variables,
            )
        except Exception as err:
            logger.exception('Create helm app error, detail: %s' % err)
            helm_app_info = None
        if helm_app_info:
            if helm_app_info.transitioning_result:
                user_log.log_add(activity_status="succeed")
                return Response()
            else:
                user_log.log_add(activity_status="failed")
                raise error_codes.APIError(helm_app_info.transitioning_message)
        else:
            # 5. 如果失败删除k8s lb实例
            K8SLoadBlance.objects.filter(
                cluster_id=data["cluster_id"], namespace_id=data["namespace_id"], name=data["name"]
            ).delete()

        user_log.log_add(activity_status="failed")
        raise error_codes.APIError(_("创建LB失败！"))


class NginxIngressRetrieveUpdateViewSet(NginxIngressBase, HelmReleaseMixin):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)
    queryset = K8SLoadBlance.objects.all()
    serializer_class = NginxIngressSLZ

    def get_release_info(self, project_id, cluster_id, namespace_id=None, namespace=None):
        release = self.get_helm_release(cluster_id, K8S_LB_CHART_NAME, namespace_id=namespace_id, namespace=namespace)
        if not release:
            return {}
        return {"version": release.get_current_version(), "values_content": release.get_valuefile()}

    def retrieve(self, request, project_id, pk):
        details = self.queryset.filter(id=pk, project_id=project_id, is_deleted=False).values()
        if not details:
            raise error_codes.ResNotFoundError(_("没有查询到实例信息！"))
        data = details[0]

        access_token = request.user.token.access_token
        cluster_id_name_map = self.get_cluster_id_name_map(access_token, project_id)
        data["cluster_name"] = cluster_id_name_map[data["cluster_id"]]["name"]
        ip_info = json.loads(data["ip_info"])
        nodes_id_ip = self.get_nodes_id_ip(access_token, project_id, data["cluster_id"])
        render_ip_info = []
        for node_id in ip_info:
            item = {"id": node_id, "inner_ip": nodes_id_ip[int(node_id)]["inner_ip"], "unshared": ip_info[node_id]}
            render_ip_info.append(item)
        data["ip_info"] = json.dumps(render_ip_info)

        # 添加release对应的版本及values内容
        data.update(
            self.get_release_info(
                project_id, data["cluster_id"], namespace_id=data["namespace_id"], namespace=data["namespace"]
            )
        )
        return Response(data)

    def get_update_node_info(self, request, data):
        """比较先前和现在节点的获取要添加和删除的节点信息"""
        lb_conf = self.get_k8s_lb_info(data["id"])
        pre_ip_info = json.loads(lb_conf.ip_info)
        update_ip_info = data["ip_info"]
        common_node_id_set = set([node_id for node_id in pre_ip_info if node_id in update_ip_info])
        # 要删除的节点
        delete_node_id_list = list(set(pre_ip_info.keys()) - common_node_id_set)
        add_node_id_list = list(set(update_ip_info.keys()) - common_node_id_set)
        return lb_conf, delete_node_id_list, add_node_id_list

    def update_node_label_list(self, request, node_labels, op="add"):
        """通过op参数判断是添加还是删除label"""
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
        instance.ip_info = json.dumps(ip_info)
        instance.protocol_type = protocol_type
        instance.updator = updator
        instance.save()

    def delete_node_label(self, request, delete_node_id_list, project_id, lb_conf):
        """删除节点标签"""
        delete_node_instances = self.get_node_labels(delete_node_id_list)
        node_id_labels = self.update_node_label_list(request, delete_node_instances, op="del")
        self.create_node_label_via_bcs(request, project_id, lb_conf.cluster_id, node_id_labels)

    def add_node_label(self, request, add_node_id_list, project_id, lb_conf):
        save_label_data = {
            "project_id": project_id,
            "cluster_id": lb_conf.cluster_id,
            "creator": request.user.username,
            "updator": request.user.username,
            "ip_info": json.dumps(add_node_id_list),
        }
        self.node_label(request, save_label_data)
        add_node_instances = self.get_node_labels(add_node_id_list)
        node_id_labels = self.update_node_label_list(request, add_node_instances, op="add")
        self.create_node_label_via_bcs(request, project_id, lb_conf.cluster_id, node_id_labels)

    @transaction.atomic
    def update(self, request, project_id, pk):
        """
        更新LB配置，包含下面几种场景
        1. 增加/减少LB协议类型
        2. 增加/减少节点数量(标签+replica)
        """
        serializer = UpdateK8SLoadBalancerSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        username = request.user.username
        data.update({"id": pk, "updator": username})
        lb_conf, delete_node_id_list, add_node_id_list = self.get_update_node_info(request, data)

        # 判断调整的节点是否已经存在，并且是独享的
        # self.update_check_node_id(lb_conf, data)

        # 删除节点配置
        if delete_node_id_list:
            self.delete_node_label(request, delete_node_id_list, project_id, lb_conf)
        # 添加节点配置
        if add_node_id_list:
            self.add_node_label(request, add_node_id_list, project_id, lb_conf)

        # 更新lb
        self.update_lb_conf(lb_conf, data["ip_info"], data["protocol_type"], username)
        release = self.get_helm_release(lb_conf.cluster_id, lb_conf.name, namespace_id=lb_conf.namespace_id)
        if not release:
            raise error_codes.ResNotFoundError(_("没有查询到对应的release信息"))

        data["namespace_id"] = lb_conf.namespace_id
        user_log = log_client.ContextActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type='lb',
            resource="%s:%s" % (lb_conf.cluster_id, lb_conf.namespace_id),
            resource_id=pk,
            extra=json.dumps(data),
        )
        # release 对应的版本为"(current-unchanged) v1.1.2"
        version = data["version"].split(constants.RELEASE_VERSION_PREFIX)[-1].strip()
        chart_version = self.get_chart_version(project_id, version)
        access_token = request.user.token.access_token
        sys_variables = self.collect_system_variable(access_token, project_id, data["namespace_id"])
        updated_instance = release.upgrade_app(
            access_token=access_token,
            chart_version_id=chart_version.id,
            answers=[],
            customs=[],
            valuefile=data["values_content"],
            updator=username,
            sys_variables=sys_variables,
        )
        if updated_instance.transitioning_result:
            user_log.log_modify(activity_status="succeed")
            return Response()
        user_log.log_modify(activity_status="failed")
        raise error_codes.APIError(updated_instance.transitioning_message)

    def delete_lb_conf(self, lb_conf):
        """标识此条记录被删除"""
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

        # 标识LB被删除
        self.delete_lb_conf(lb_conf)
        # 删除节点标签
        delete_node_id_list = [node_id for node_id in json.loads(lb_conf.ip_info)]
        self.delete_node_label(request, delete_node_id_list, project_id, lb_conf)
        # 删除helm release
        release = self.get_helm_release(
            lb_conf.cluster_id, K8S_LB_CHART_NAME, namespace_id=lb_conf.namespace_id, namespace=lb_conf.namespace
        )
        if not release:
            return Response()

        user_log = log_client.ContextActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type='lb',
            resource="%s:%s" % (lb_conf.cluster_id, lb_conf.namespace_id),
            resource_id=pk,
        )
        release.destroy(username=request.user.username, access_token=request.user.token.access_token)

        user_log.log_delete(activity_status="succeed")
        return Response()


class NginxIngressListNamespaceViewSet(NginxIngressBase):
    def list(self, request, project_id, cluster_id):
        used_ns_id_list = K8SLoadBlance.objects.filter(
            project_id=project_id, cluster_id=cluster_id, is_deleted=False
        ).values("namespace_id")
        return APIResponse({"data": [info["namespace_id"] for info in used_ns_id_list]})
