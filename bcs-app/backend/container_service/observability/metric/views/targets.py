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
import itertools
import logging
import re
from urllib import parse

from django.conf import settings
from django.http import HttpResponseRedirect
from rest_framework import viewsets
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response

from backend.components import prometheus
from backend.utils.renderers import BKAPIRenderer

logger = logging.getLogger(__name__)


class TargetsViewSet(viewsets.ViewSet):
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
