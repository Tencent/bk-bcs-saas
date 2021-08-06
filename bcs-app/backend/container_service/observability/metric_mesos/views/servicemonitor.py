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
import itertools
import logging
import re
from datetime import timedelta
from typing import List, Tuple
from urllib import parse

import arrow
import semantic_version
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response

from backend.accounts import bcs_perm
from backend.apps.constants import ALL_LIMIT, ProjectKind
from backend.bcs_web.audit_log import client as activity_client
from backend.components import paas_cc, prometheus
from backend.components.bcs import k8s, mesos
from backend.container_service.observability.metric_mesos import serializers
from backend.utils.error_codes import error_codes
from backend.utils.renderers import BKAPIRenderer

logger = logging.getLogger(__name__)

# 不返回给前端的字段
FILTERED_METADATA = [
    "annotations",
    "selfLink",
    "uid",
    "resourceVersion",
    "initializers",
    "generation",
    "deletionTimestamp",
    "deletionGracePeriodSeconds",
    "clusterName",
]


class ServiceMonitor(viewsets.ViewSet):
    """集群ServiceMonitor"""

    serializer_class = serializers.ServiceMonitorCreateSLZ
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    DEFAULT_ENDPOINT_PATH = "/metrics"
    DEFAULT_ENDPOINT_INTERVAL = 30
    NO_PERM_NS = ["thanos"]
    NO_PERM_MAP = {
        "view": True,
        "use": False,
        "edit": False,
        "delete": False,
        "view_msg": "",
        "edit_msg": _("不允许操作系统命名空间"),
        "use_msg": _("不允许操作系统命名空间"),
        "delete_msg": _("不允许操作系统命名空间"),
    }

    SERVICE_NAME_LABEL = "io.tencent.bcs.service_name"
    TIME_DURATION_PATTERN = re.compile(r"^((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?$")

    def _get_client(self, request, project_id, cluster_id):
        if request.project.kind == ProjectKind.MESOS.value:
            client = mesos.MesosClient(request.user.token.access_token, project_id, cluster_id, env=None)
        else:
            client = k8s.K8SClient(request.user.token.access_token, project_id, cluster_id, env=None)
        return client

    def get_duration(self, duration, default=None):
        """解析普罗米修斯时间范围"""
        if not duration:
            return default

        match = self.TIME_DURATION_PATTERN.match(duration)
        if not match:
            return default

        total_seconds = timedelta(**{k: int(v) for k, v in match.groupdict().items() if v}).total_seconds()

        return int(total_seconds)

    def _handle_endpoints(self, endpoints, readonly=True):
        for endpoint in endpoints:
            endpoint.setdefault("path", self.DEFAULT_ENDPOINT_PATH)
            endpoint["interval"] = self.get_duration(endpoint.get("interval"), self.DEFAULT_ENDPOINT_INTERVAL)
        return endpoints

    def _handle_items(self, cluster_id, cluster_map, namespace_map, manifest):
        items = manifest.get("items") or []
        new_items = []

        for item in items:
            try:
                labels = item["metadata"].get("labels") or {}
                item["metadata"] = {k: v for k, v in item["metadata"].items() if k not in FILTERED_METADATA}
                item["cluster_id"] = cluster_id
                item["namespace"] = item["metadata"]["namespace"]
                item["namespace_id"] = namespace_map.get((cluster_id, item["metadata"]["namespace"]))
                item["name"] = item["metadata"]["name"]
                item["instance_id"] = f"{item['namespace']}/{item['name']}"
                item["service_name"] = labels.get(self.SERVICE_NAME_LABEL)
                item["cluster_name"] = cluster_map[cluster_id]["name"]
                item["environment"] = cluster_map[cluster_id]["environment"]
                item["metadata"]["service_name"] = labels.get(self.SERVICE_NAME_LABEL)
                item["create_time"] = (
                    arrow.get(item["metadata"]["creationTimestamp"])
                    .to(settings.TIME_ZONE)
                    .format("YYYY-MM-DD HH:mm:ss")
                )
                if isinstance(item["spec"].get("endpoints"), list):
                    item["spec"]["endpoints"] = self._handle_endpoints(item["spec"]["endpoints"])
                new_items.append(item)
            except Exception as err:
                logger.error("handle item error, %s, %s", err, item)

        new_items = sorted(new_items, key=lambda x: x["create_time"], reverse=True)
        return new_items

    def filter_no_perm(self, data):
        for d in data:
            d["permissions"]["delete"] = d["permissions"]["edit"]
            d["permissions"]["delete_msg"] = d["permissions"]["edit_msg"]
            if d["namespace"] not in self.NO_PERM_NS:
                continue
            d["permissions"] = self.NO_PERM_MAP

    def _validate_namespace_use_perm(self, request, project_id: str, cluster_namespace_list: List[Tuple]) -> None:
        """
        检查是否有命名空间的使用权限

        :param request: Django Request
        :param project_id: 项目 ID
        :param cluster_namespace_list: 集群-命名空间列表，格式：[(cluster_id, namespace)]
        :return:
        """
        namespace_map = self._get_namespace_map(project_id)
        for cluster_id, namespace in cluster_namespace_list:
            if namespace in self.NO_PERM_NS:
                raise error_codes.APIError(_("namespace operation is not allowed"))

            namespace_id = namespace_map.get((cluster_id, namespace))
            # 检查是否有命名空间的使用权限
            perm = bcs_perm.Namespace(request, project_id, namespace_id)
            perm.can_use(raise_exception=True)

    def _activity_log(self, project_id, username, resource_name, description, status):
        """操作记录"""
        client = activity_client.ContextActivityLogClient(
            project_id=project_id, user=username, resource_type="metric", resource=resource_name
        )
        if status is True:
            client.log_delete(activity_status="succeed", description=description)
        else:
            client.log_delete(activity_status="failed", description=description)

    def _get_cluster_map(self, project_id):
        """获取集群dict"""
        resp = paas_cc.get_all_clusters(self.request.user.token.access_token, project_id, desire_all_data=1)
        data = resp.get("data") or {}
        cluster_list = data.get("results") or []
        cluster_map = {i["cluster_id"]: i for i in cluster_list}
        return cluster_map

    def _get_namespace_map(self, project_id):
        """获取命名空间dict"""
        resp = paas_cc.get_namespace_list(self.request.user.token.access_token, project_id, limit=ALL_LIMIT)
        namespace_list = resp.get("data", {}).get("results") or []
        namespace_map = {(i["cluster_id"], i["name"]): i["id"] for i in namespace_list}
        return namespace_map

    def list(self, request, project_id, cluster_id):
        cluster_map = self._get_cluster_map(project_id)
        namespace_map = self._get_namespace_map(project_id)
        data = []

        if cluster_id not in cluster_map:
            raise error_codes.APIError(_("cluster_id not valid"))

        client = self._get_client(request, project_id, cluster_id)

        items = self._handle_items(cluster_id, cluster_map, namespace_map, client.list_service_monitor())
        data.extend(items)

        perm = bcs_perm.Namespace(request, project_id, bcs_perm.NO_RES)
        data = perm.hook_perms(data, ns_id_flag="namespace_id")
        self.filter_no_perm(data)

        return Response(data)

    def create(self, request, project_id, cluster_id=None):
        slz = self.serializer_class(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        if cluster_id is None:
            cluster_id = data["cluster_id"]

        endpoints = [
            {
                "path": data["path"],
                "interval": data["interval"],
                "port": data["port"],
                "params": data.get("params", {}),
            }
        ]

        spec = {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "ServiceMonitor",
            "metadata": {
                "labels": {
                    "release": "po",
                    "io.tencent.paas.source_type": "bcs",
                    "io.tencent.bcs.service_name": data["service_name"],
                },
                "name": data["name"],
                "namespace": data["namespace"],
            },
            "spec": {
                "endpoints": endpoints,
                "selector": {"matchLabels": data["selector"]},
                "sampleLimit": data["sample_limit"],
            },
        }

        client = self._get_client(request, project_id, cluster_id)

        result = client.create_service_monitor(data["namespace"], spec)
        if result.get("status") == "Failure":
            message = _("创建Metrics:{}失败, [命名空间:{}], {}").format(
                data["name"], data["namespace"], result.get("message", "")
            )
            self._activity_log(project_id, request.user.username, data["name"], message, False)
            raise error_codes.APIError(result.get("message", ""))

        message = _("创建Metrics:{}成功, [命名空间:{}]").format(data["name"], data["namespace"])
        self._activity_log(project_id, request.user.username, data["name"], message, True)
        return Response(result)

    def get(self, request, project_id, cluster_id, namespace, name):
        """获取单个serviceMonitor"""
        client = self._get_client(request, project_id, cluster_id)
        result = client.get_service_monitor(namespace, name)
        if result.get("status") == "Failure":
            raise error_codes.APIError(result.get("message", ""))

        labels = result["metadata"].get("labels") or {}
        result["metadata"] = {k: v for k, v in result["metadata"].items() if k not in FILTERED_METADATA}
        result["metadata"]["service_name"] = labels.get(self.SERVICE_NAME_LABEL)

        if isinstance(result["spec"].get("endpoints"), list):
            result["spec"]["endpoints"] = self._handle_endpoints(result["spec"]["endpoints"], readonly=False)

        return Response(result)

    def delete(self, request, project_id, cluster_id, namespace, name):
        """删除servicemonitor"""
        self._validate_namespace_use_perm(request, project_id, [(cluster_id, namespace)])
        client = self._get_client(request, project_id, cluster_id)
        result = client.delete_service_monitor(namespace, name)
        if result.get("status") == "Failure":
            message = _("删除Metrics:{}失败, [命名空间:{}], {}").format(name, namespace, result.get("message", ""))
            self._activity_log(project_id, request.user.username, name, message, False)
            raise error_codes.APIError(result.get("message", ""))

        message = _("删除Metrics:{}成功, [命名空间:{}]").format(name, namespace)
        self._activity_log(project_id, request.user.username, name, message, True)
        return Response(result)

    def _merge_spec(self, spec, validated_data):
        spec["metadata"]["labels"]["release"] = "po"
        spec["spec"]["selector"] = {"matchLabels": validated_data["selector"]}
        spec["spec"]["sampleLimit"] = validated_data["sample_limit"]
        spec["spec"]["endpoints"] = [
            {
                "path": validated_data["path"],
                "interval": validated_data["interval"],
                "port": validated_data["port"],
                "params": validated_data.get("params", {}),
            }
        ]
        spec["metadata"] = {k: v for k, v in spec["metadata"].items() if k not in FILTERED_METADATA}

        return spec

    def update(self, request, project_id, cluster_id, namespace, name):
        slz = serializers.ServiceMonitorUpdateSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        client = self._get_client(request, project_id, cluster_id)
        result = client.get_service_monitor(namespace, name)
        if result.get("status") == "Failure":
            message = _("更新Metrics:{}失败, [命名空间:{}], {}").format(name, namespace, result.get("message", ""))
            self._activity_log(project_id, request.user.username, name, message, False)
            raise error_codes.APIError(result.get("message", ""))

        spec = self._merge_spec(result, data)

        # 更新会合并selector，所有是先删除, 再创建
        result = client.delete_service_monitor(namespace, name)
        if result.get("status") == "Failure":
            message = _("更新Metrics:{}失败, [命名空间:{}], {}").format(name, namespace, result.get("message", ""))
            self._activity_log(project_id, request.user.username, name, message, False)
            raise error_codes.APIError(result.get("message", ""))

        result = client.create_service_monitor(namespace, spec)
        if result.get("status") == "Failure":
            message = _("更新Metrics:{}失败, [命名空间:{}], {}").format(name, namespace, result.get("message", ""))
            self._activity_log(project_id, request.user.username, name, message, False)
            raise error_codes.APIError(result.get("message", ""))

        message = _("更新Metrics:{}成功, [命名空间:{}]").format(name, namespace)
        self._activity_log(project_id, request.user.username, name, message, True)
        return Response(result)

    def batch_delete(self, request, project_id, cluster_id):
        """批量删除"""
        slz = serializers.ServiceMonitorBatchDeleteSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        svc_monitors = slz.validated_data["servicemonitors"]

        ns_list = [(cluster_id, i["namespace"]) for i in svc_monitors]
        self._validate_namespace_use_perm(request, project_id, ns_list)

        client = self._get_client(request, project_id, cluster_id)
        successes = []
        for monitor in svc_monitors:
            result = client.delete_service_monitor(monitor["namespace"], monitor["name"])
            if result.get("status") == "Failure":
                message = _("删除Metrics:{}失败, [命名空间:{}], {}").format(
                    monitor["name"], monitor["namespace"], result.get("message", "")
                )
                self._activity_log(project_id, request.user.username, monitor["name"], message, False)
                raise error_codes.APIError(result.get("message", ""))
            else:
                successes.append(monitor)

        names = ",".join(i["name"] for i in successes)
        message = _("删除Metrics:{}成功, [命名空间:{}]").format(names, ",".join(i["namespace"] for i in successes))
        self._activity_log(project_id, request.user.username, names, message, True)
        return Response({"successes": successes})


class Targets(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    filtered_annotation_pattern = re.compile(r"__meta_kubernetes_\w+_annotation")
    job_pattern = re.compile(r"^(?P<namespace>[\w-]+)/(?P<name>[\w-]+)/(?P<port_idx>\d+)$")

    def _filter_targets(self, data, namespace, name, show_discovered):
        """servicemonitor通过job名称过滤"""

        res = []
        for d in data:
            targets = d.get("targets") or {}
            active_targets = targets.get("activeTargets") or []
            for t in active_targets:
                raw_job = t["discoveredLabels"]["job"]
                job = self.job_pattern.match(raw_job)
                if not job:
                    continue

                # 按namespace和name过滤
                job_dict = job.groupdict()
                if namespace and job_dict["namespace"] != namespace:
                    continue
                if name and job_dict["name"] != name:
                    continue

                if show_discovered:
                    t["discoveredLabels"] = {
                        k: v for k, v in t["discoveredLabels"].items() if not self.filtered_annotation_pattern.match(k)
                    }
                else:
                    t.pop("discoveredLabels")
                t["instance_id"] = f"{job_dict['namespace']}/{job_dict['name']}"
                t["discovered_job"] = raw_job
                t["job"] = t["labels"]["job"]
                res.append(t)
        return res

    def _filter_jobs(self, data, namespace, name):
        targets = self._filter_targets(data, namespace, name)
        jobs = set()
        for target in targets:
            labels = target.get("labels") or {}
            job = labels.get("job")
            if job:
                jobs.add(job)
        return jobs

    def list(self, request, project_id, cluster_id, namespace=None, name=None):
        """获取targets列表"""
        show_discovered = request.GET.get("show_discovered") == "1"
        result = prometheus.get_targets(project_id, cluster_id).get("data") or []
        targets = self._filter_targets(result, namespace, name, show_discovered)
        return Response(targets)

    def list_instance(self, request, project_id, cluster_id):
        """targets列表, 按instance_id聚合"""
        show_discovered = request.GET.get("show_discovered") == "1"
        result = prometheus.get_targets(project_id, cluster_id).get("data") or []
        targets = self._filter_targets(result, None, None, show_discovered)
        targets_dict = {}
        for instance_id, t in itertools.groupby(
            sorted(targets, key=lambda x: x["instance_id"]), key=lambda x: x["instance_id"]
        ):
            t = [i for i in t]
            jobs = set([i["job"] for i in t])
            if jobs:
                jobs = "|".join(jobs)
                expr = f'{{cluster_id="{cluster_id}",job=~"{jobs}"}}'
                params = {"project_id": project_id, "expr": expr}
                query = parse.urlencode(params)
                graph_url = f"{settings.DEVOPS_HOST}/console/monitor/{request.project.project_code}/metric?{query}"
            else:
                graph_url = None
            targets_dict[instance_id] = {
                "targets": t,
                "graph_url": graph_url,
                "total_count": len(t),
                "health_count": len([i for i in t if i["health"] == "up"]),
            }

        return Response(targets_dict)

    def graph(self, request, project_id, cluster_id, namespace, name):
        """获取下面所有targets的job, 跳转到容器监控"""
        result = prometheus.get_targets(project_id, cluster_id).get("data") or []
        jobs = self._filter_jobs(result, namespace, name)

        if jobs:
            jobs = "|".join(jobs)
            expr = f'{{cluster_id="{cluster_id}",job=~"{jobs}"}}'
        else:
            expr = f'{{cluster_id="{cluster_id}"}}'
        params = {"project_id": project_id, "expr": expr}
        query = parse.urlencode(params)

        redirect_url = f"{settings.DEVOPS_HOST}/console/monitor/{request.project.project_code}/metric?{query}"

        return HttpResponseRedirect(redirect_url)


class Services(viewsets.ViewSet):
    """可监控的services"""

    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    filtered_label_prefix = [
        "io_tencent_bcs_",
        "io.tencent.paas.",
        "io.tencent.bcs.",
        "io.tencent.bkdata.",
        "io.tencent.paas.",
    ]

    def _filter_label(self, label_key):
        if label_key in ["io.tencent.bcs.controller.name"]:
            return True

        for prefix in self.filtered_label_prefix:
            if label_key.startswith(prefix):
                return False

        return True

    def _filter_service(self, service_list):
        for service in service_list:
            service["data"]["metadata"] = {
                k: v for k, v in service["data"]["metadata"].items() if k not in FILTERED_METADATA
            }

            labels = service["data"]["metadata"].get("labels")
            if not labels:
                continue

            service["data"]["metadata"]["labels"] = dict(
                sorted([(k, v) for k, v in labels.items() if self._filter_label(k)])
            )
        return service_list

    def list(self, request, project_id, cluster_id):
        """获取targets列表"""
        access_token = request.user.token.access_token

        if request.project.kind == ProjectKind.MESOS.value:
            client = mesos.MesosClient(access_token, project_id, cluster_id, env=None)
            resp = client.get_services({"env": "mesos"})
        else:
            client = k8s.K8SClient(access_token, project_id, cluster_id, env=None)
            resp = client.get_service({"env": "k8s"})

        data = self._filter_service(resp.get("data") or [])

        return Response(data)


class PrometheusUpdate(viewsets.ViewSet):
    """可监控的services"""

    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def _get_version(self, image):
        version = image.rsplit(":", 1)[1]
        if version.startswith("v"):
            version = version[1:]
        return version

    def get(self, request, project_id, cluster_id):
        """是否需要更新 thano-sidecar 版本
        Deprecated 已经统一升级到 v2.5.0 版本
        """
        data = {"need_update": False, "update_tooltip": ""}
        return Response(data)

    def _activity_log(self, project_id, username, resource_name, description, status):
        """操作记录"""
        client = activity_client.ContextActivityLogClient(
            project_id=project_id, user=username, resource_type="metric", resource=resource_name
        )
        if status is True:
            client.log_delete(activity_status="succeed", description=description)
        else:
            client.log_delete(activity_status="failed", description=description)

    def update(self, request, project_id, cluster_id):
        access_token = request.user.token.access_token
        client = k8s.K8SClient(access_token, project_id, cluster_id, env=None)
        resp = client.get_prometheus("thanos", "po-prometheus-operator-prometheus")
        spec = resp.get("spec")
        if not spec:
            raise error_codes.APIError(_("Prometheus未安装, 请联系管理员解决"))

        need_update = False
        # 获取原来的值不变，覆盖更新
        for container in spec["containers"]:
            if container["name"] not in settings.PROMETHEUS_VERSIONS:
                continue

            image = settings.PROMETHEUS_VERSIONS[container["name"]]
            if semantic_version.Version(self._get_version(image)) <= semantic_version.Version(
                self._get_version(container["image"])
            ):
                continue

            need_update = True
            container["image"] = image

        if not need_update:
            raise error_codes.APIError(_("已经最新版本, 不需要升级"))

        patch_spec = {"spec": {"containers": spec["containers"]}}
        resp = client.update_prometheus("thanos", "po-prometheus-operator-prometheus", patch_spec)
        message = _("更新Metrics: 升级 thanos-sidecar 成功")
        self._activity_log(project_id, request.user.username, "update thanos-sidecar", message, True)
        return Response(resp)
