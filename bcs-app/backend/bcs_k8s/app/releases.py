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
from rest_framework import viewsets, response
from rest_framework.renderers import BrowsableAPIRenderer

from backend.utils.renderers import BKAPIRenderer
from backend.bcs_k8s.app import utils as release_utils
from backend.bcs_k8s.helm.utils import repo as repo_utils
from backend.bcs_k8s.app.serializers import UpdateAndPreviewParamsSLZ, preview_parse
from backend.bcs_k8s.app.utils import get_release_manifest, get_repo_chart_version
from backend.bcs_k8s.helm.bcs_variable import get_valuefile_with_bcs_variable_injected
from backend.bcs_k8s.app.deployer import ReleaseDeployer


class HelmReleaseViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def retrieve(self, request, project_id, cluster_id, namespace, release_name):
        # 获取release
        access_token = request.user.token.access_token
        params = {
            "namespace": namespace,
            "filter_release": (namespace, release_name),
            "compose_data_func": release_utils.compose_release_with_chart
        }
        releases = list(release_utils.get_helm_releases(access_token, project_id, cluster_id, **params))
        return response.Response(releases[0])

    def _get_manifest(self, request, project_id, cluster_id, namespace, version_url, repo_info, data):
        files = repo_utils.parse_chart_version_files(version_url, repo_info[1], repo_info[2])
        data.update({"files": files})
        return get_release_manifest(request, project_id, cluster_id, namespace, **data)[0]

    def preview(self, request, project_id, cluster_id, namespace, release_name):
        slz = UpdateAndPreviewParamsSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        # 通过version获取对应的chart信息
        repo_info = repo_utils.get_repo_info(project_id)
        # 获取chart version对应的下载地址
        chart_version_info = get_repo_chart_version(data["chart_name"], data["update_version"], repo_info)
        # 格式: {"urls": [xxxx]}，现阶段只有一个url
        version_url = chart_version_info["urls"][0]
        manifest = self._get_manifest(request, project_id, cluster_id, namespace, version_url, repo_info, data)
        content = preview_parse(manifest, namespace)
        resp_data = {
            "content": content,
            "new_content": manifest
        }
        # 获取release的版本对应的yaml
        release_version_url = f"{version_url.rsplit('/', 1)[0]}/{data['chart_name']}-{data['release_version']}.tgz"
        old_content = self._get_manifest(request, project_id, cluster_id, namespace, release_version_url, repo_info, data)
        resp_data["old_content"] = old_content
        return response.Response(resp_data)

    def update(self, request, project_id, cluster_id, namespace, release_name):
        """版本更新
        """
        slz = UpdateAndPreviewParamsSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        # 通过version获取对应的chart信息
        repo_info = repo_utils.get_repo_info(project_id)
        # 获取chart version对应的下载地址
        chart_version_info = get_repo_chart_version(data["chart_name"], data["update_version"], repo_info)
        # 格式: {"urls": [xxxx]}，现阶段只有一个url
        version_url = chart_version_info["urls"][0]
        chart_files = repo_utils.parse_chart_version_files(version_url, repo_info[1], repo_info[2])
        # 下发命令
        deployer = ReleaseDeployer(
            operator=request.user.username,
            access_token=request.user.token.access_token,
            project_id=project_id,
            cluster_id=cluster_id,
            namespace=namespace,
            name=release_name,
            version=data["update_version"]
        )
        deployer.run_with_helm(data["valuefile"], chart_files, cmd_flags=data.get("cmd_flags"))
        return response.Response()


class ReleaseUpdateVersionsViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def list(self, request, project_id, chart_name):
        release_version = request.query_params.get("version")
        chart_versions = release_utils.get_repo_chart_versions(project_id, chart_name)
        # 匹配对应的chart版本
        data = [{"version": f"(current-unchanged) {release_version}"}]
        data.extend([{"version": version}for version in chart_versions])

        return response.Response(data)
