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
import logging
import re
from urllib import parse

from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response

from backend.apps.metric import serializers
from backend.components import paas_cc, prometheus
from backend.components.bcs import k8s
from backend.utils.error_codes import error_codes
from backend.utils.renderers import BKAPIRenderer

logger = logging.getLogger(__name__)


class ServiceMonitor(viewsets.ViewSet):
    """集群ServiceMonitor
    """

    serializer_class = serializers.ServiceMonitorSLZ
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    # 不返回给前端的字段
    filtered_metadata = [
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

    DEFAULT_ENDPOINT_PATH = "/metrics"
    DEFAULT_ENDPOINT_INTERVAL = "30s"

    def _handle_endpoints(self, endpoints):
        for endpoint in endpoints:
            endpoint.setdefault("path", self.DEFAULT_ENDPOINT_PATH)
            endpoint.setdefault("interval", self.DEFAULT_ENDPOINT_INTERVAL)
        return endpoints

    def _handle_items(self, cluster_id, cluster_map, manifest):
        items = manifest.get("items") or []
        for item in items:
            item["metadata"] = {k: v for k, v in item["metadata"].items() if k not in self.filtered_metadata}
            item["cluster_id"] = cluster_id
            item["namespace"] = item["metadata"]["namespace"]
            item["name"] = item["metadata"]["name"]
            item["cluster_name"] = cluster_map[cluster_id]["name"]
            if isinstance(item["spec"].get("endpoints"), list):
                item["spec"]["endpoints"] = self._handle_endpoints(item["spec"]["endpoints"])
        return items

    def _get_cluster_map(self, project_id):
        """获取集群列表
        """
        resp = paas_cc.get_all_clusters(self.request.user.token.access_token, project_id, desire_all_data=1)
        data = resp.get("data") or {}
        cluster_list = data.get("results") or []
        cluster_map = {i["cluster_id"]: i for i in cluster_list}
        return cluster_map

    def list(self, request, project_id, cluster_id=None):
        access_token = request.user.token.access_token
        cluster_map = self._get_cluster_map(project_id)
        data = []

        if cluster_id:
            if cluster_id not in cluster_map:
                raise error_codes.APIError(_("cluster_id not valid"))
            client = k8s.K8SClient(access_token, project_id, cluster_id, env=None)
            items = self._handle_items(cluster_id, cluster_map, client.list_service_monitor())
            data.extend(items)
        else:
            for cluster in cluster_map.values():
                cluster_id = cluster["cluster_id"]
                cluster_env = cluster.get("environment")
                client = k8s.K8SClient(access_token, project_id, cluster_id, env=cluster_env)
                items = self._handle_items(cluster_id, cluster_map, client.list_service_monitor())
                data.extend(items)

        return Response(data)

    def create(self, request, project_id, cluster_id=None):
        slz = self.serializer_class(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        if cluster_id is None:
            cluster_id = data["cluster_id"]

        spec = {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "ServiceMonitor",
            "metadata": {"labels": {"release": "po"}, "name": data["name"], "namespace": data["namespace"]},
            "spec": {
                "endpoints": [{"path": data["path"], "interval": data["interval"]}],
                "selector": {"matchLabels": data["selector"]},
                "sampleLimit": data["sample_limit"],
            },
        }

        client = k8s.K8SClient(request.user.token.access_token, project_id, cluster_id, env=None)
        result = client.create_service_monitor(data["namespace"], spec)
        return Response(result)

    def get(self, request, project_id, cluster_id, namespace, name):
        """获取单个serviceMonitor
        """
        access_token = request.user.token.access_token
        client = k8s.K8SClient(access_token, project_id, cluster_id, env=None)
        result = client.get_service_monitor(namespace, name)
        if result.get("status") == "Failure":
            raise error_codes.APIError(result.get("message", ""))

        if result.get("metadata"):
            result["metadata"] = {k: v for k, v in result["metadata"].items() if k not in self.filtered_metadata}
        return Response(result)

    def delete(self, request, project_id, cluster_id, namespace, name):
        """删除servicemonitor
        """
        access_token = request.user.token.access_token
        client = k8s.K8SClient(access_token, project_id, cluster_id, env=None)
        result = client.delete_service_monitor(namespace, name)
        if result.get("status") == "Failure":
            raise error_codes.APIError(result.get("message", ""))
        return Response(result)

    def _merge_spec(self, spec, validated_data):
        spec["metadata"]["labels"]["release"] = "po"
        spec["spec"]["selector"] = validated_data["selector"]
        spec["spec"]["sampleLimit"] = validated_data["sample_limit"]
        endpoints = spec["spec"].get("endpoints") or []
        for endpoint in endpoints:
            if endpoint["path"] != validated_data["path"]:
                continue
            endpoint["interval"] = validated_data["interval"]
        spec["endpoints"] = endpoints
        return spec

    def update(self, request, project_id, cluster_id, namespace, name):
        access_token = request.user.token.access_token

        slz = serializers.ServiceMonitorUpdateSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        client = k8s.K8SClient(access_token, project_id, cluster_id, env=None)
        result = client.get_service_monitor(namespace, name)
        if result.get("status") == "Failure":
            raise error_codes.APIError(result.get("message", ""))

        spec = self.merge_spec(result, data)
        result = client.update_service_monitor(namespace, name, spec)
        return Response(result)


class Targets(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    filtered_annotation_pattern = re.compile(r"__meta_kubernetes_\w+_annotation")

    def _filter_targets(self, data, namespace, name):
        """servicemonitor通过job名称过滤
        """
        matcher = re.compile(r"{namespace}/{name}/\d".format(namespace=namespace, name=name))
        res = []
        for d in data:
            targets = d.get("targets") or {}
            active_targets = targets.get("activeTargets") or []
            for t in active_targets:
                if matcher.match(t["discoveredLabels"]["job"]):
                    t["discoveredLabels"] = {
                        k: v for k, v in t["discoveredLabels"].items() if not self.filtered_annotation_pattern.match(k)
                    }
                    res.append(t)
        return res

    def _filter_jobs(self, data, namespace, name):
        targets = self._filter_targets(data, namespace, name)
        jobs = []
        for target in targets:
            labels = target.get("labels") or {}
            job = labels.get("job")
            if job:
                jobs.append(job)
        return jobs

    def list(self, request, project_id, cluster_id, namespace, name):
        """获取targets列表
        """
        result = prometheus.get_targets(project_id, cluster_id).get("data") or []
        targets = self._filter_targets(result, namespace, name)
        return Response(targets)

    def graph(self, request, project_id, cluster_id, namespace, name):
        """获取下面所有targets的job, 跳转到容器监控
        """
        result = prometheus.get_targets(project_id, cluster_id).get("data") or []
        jobs = self._filter_jobs(result, namespace, name)

        if jobs:
            jobs = "|".join(jobs)
            expr = f'{{cluster_id="{cluster_id}, job=~"{jobs}"}}'
        else:
            expr = f'{{cluster_id="{cluster_id}"}}'
        params = {"project_id": project_id, "expr": expr}
        query = parse.urlencode(params)

        redirect_url = f"{settings.DEVOPS_HOST}/console/monitor/{request.project.project_code}/metric?{query}"

        return HttpResponseRedirect(redirect_url)
