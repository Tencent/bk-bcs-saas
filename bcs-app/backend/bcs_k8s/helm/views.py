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

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from backend.utils.error_codes import error_codes
from backend.utils.views import ActionSerializerMixin, FilterByProjectMixin, with_code_wrapper
from .models.chart import (Chart, ChartVersion, ChartVersionSnapshot)
from .models.repo import Repository
from .serializers import (
    ChartSLZ, ChartVersionSLZ, ChartDetailSLZ,
    CreateRepoSLZ, RepoSLZ, MinimalRepoSLZ, ChartVersionTinySLZ, RepositorySyncSLZ)
from backend.bcs_k8s.authtoken.authentication import TokenAuthentication
from .providers.repo_provider import add_repo, add_plain_repo
from .tasks import sync_helm_repo
from backend.apps.whitelist_bk import enabled_force_sync_chart_repo
from backend.utils.renderers import BKAPIRenderer
from backend.bcs_k8s.app.models import App
from backend.components.helm_chart import delete_chart_version

logger = logging.getLogger(__name__)


# for debug purpose
# from rest_framework.authentication import SessionAuthentication
# class CsrfExemptSessionAuthentication(SessionAuthentication):
    # def enforce_csrf(self, request):
        # return  # To not perform the csrf check previously happening


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class LargeResultsSetPagination(PageNumberPagination):
    # 用于不需要分页的场景
    page_size = 10000000
    page_size_query_param = 'page_size'
    max_page_size = 1000000


@with_code_wrapper
class ChartView(ActionSerializerMixin, viewsets.ModelViewSet):
    queryset = Chart.objects.filter(deleted=False)
    serializer_class = ChartSLZ
    # pagination_class = StandardResultsSetPagination
    pagination_class = None
    lookup_field = 'pk'
    lookup_url_kwarg = "chart_id"

    action_serializers = {
        'retrieve': ChartDetailSLZ,
    }

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        queryset = self.queryset.filter(repository__project_id=project_id).order_by("-changed_at")

        repo_id = self.kwargs.get('repo_id')
        if repo_id is not None:
            queryset = queryset.filter(repository__id=repo_id)

        return queryset


@with_code_wrapper
class ChartVersionView(ActionSerializerMixin, viewsets.ModelViewSet):
    queryset = ChartVersion.objects.all().order_by("-created")
    serializer_class = ChartVersionSLZ
    pagination_class = LargeResultsSetPagination
    lookup_field = "pk"
    lookup_url_kwarg = "version_id"

    action_serializers = {
        'list': ChartVersionTinySLZ,
    }

    def get_queryset(self):
        queryset = self.queryset
        chart_id = self.request.parser_context["kwargs"].get("chart_id")
        if chart_id is not None:
            queryset = queryset.filter(chart__id=chart_id)
        else:
            repo_id = self.request.parser_context["kwargs"].get("repo_id")
            if repo_id is not None:
                queryset = queryset.filter(chart__repo__id=repo_id)
        return queryset


@with_code_wrapper
class RepositoryView(FilterByProjectMixin, viewsets.ModelViewSet):
    """Viewset for helm chart repository management
    """
    serializer_class = RepoSLZ
    queryset = Repository.objects.all()

    def get_queryset(self):
        project_id = self.request.parser_context["kwargs"]["project_id"]
        queryset = super(RepositoryView, self).get_queryset()
        queryset = queryset.filter(project_id=project_id)
        return queryset

    def list_detailed(self, request, *args, **kwargs):
        """List all repositories
        """
        serializer = RepoSLZ(self.get_queryset(), many=True)
        return Response({
            'count': self.get_queryset().count(),
            'results': serializer.data
        })

    def list_minimal(self, request, *args, **kwargs):
        """List all repositories minimally
        """
        serializer = MinimalRepoSLZ(self.get_queryset(), many=True)
        return Response({
            'count': self.get_queryset().count(),
            'results': serializer.data
        })

    def retrieve(self, request, project_id, *args, **kwargs):
        """Retrieve certain Chart Repository
        """
        repo_id = kwargs.get('repo_id')
        serializer = RepoSLZ(self.queryset.get(project_id=project_id, id=repo_id))
        return Response(data=serializer.data)

    def destroy(self, request, project_id, *args, **kwargs):
        """Destroy Chart Repository
        """
        repo_id = kwargs.get('repo_id')
        try:
            self.queryset.get(project_id=project_id, id=repo_id).delete()
        except Exception as e:
            raise error_codes.CheckFailed.f("Delete Chart Repo failed: {}".format(e))
        return Response(status=status.HTTP_204_NO_CONTENT)


@with_code_wrapper
class RepositoryCreateView(FilterByProjectMixin, viewsets.ViewSet):
    """Viewset for creating helm chart repository management
    """
    serializer_class = CreateRepoSLZ

    def create(self, request, project_id, *args, **kwargs):
        """Create Repository (support all kind of repo create)
        """
        serializer = CreateRepoSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.data
        new_chart_repo = add_repo(
            project_id,
            provider_name=data.get('provider'),
            user=self.request.user,
            name=data["name"],
            url=data.get("url")
        )

        return Response(
            status=status.HTTP_201_CREATED,
            data=RepoSLZ(new_chart_repo).data
        )


@with_code_wrapper
class RepositorySyncView(FilterByProjectMixin, viewsets.ViewSet):
    """RepositorySyncView call sync_helm_repo directly
    """
    serializer_class = RepositorySyncSLZ

    def create(self, request, project_id, repo_id, *args, **kwargs):
        """Sync Chart Repository
        """

        sync_helm_repo(repo_id, True)

        data = {
            "code": 0,
            "message": "repo sync success"
        }

        return Response(
            status=status.HTTP_200_OK,
            data=data
        )


@with_code_wrapper
class RepositorySyncByProjectView(FilterByProjectMixin, viewsets.ViewSet):
    """RepositorySyncByProjectView call sync_helm_repo directly
    """
    serializer_class = RepositorySyncSLZ

    def create(self, request, project_id, *args, **kwargs):
        """Sync Chart Repository
        """
        id_name_list = list(Repository.objects.filter(project_id=project_id).values_list("id", "name"))
        # 白名单控制强制同步项目仓库，不强制同步公共仓库
        force_sync_repo = False
        if enabled_force_sync_chart_repo(project_id):
            force_sync_repo = True

        for repo_id, repo_name in id_name_list:
            # 如果是公共仓库，不允许强制同步
            if repo_name == 'public-repo':
                sync_helm_repo(repo_id, False)
            else:
                sync_helm_repo(repo_id, force_sync_repo)

        data = {
            "code": 0,
            "message": "success sync %s repositories" % len(id_name_list)
        }

        return Response(
            status=status.HTTP_200_OK,
            data=data
        )


class RepositorySyncByProjectAPIView(RepositorySyncByProjectView):
    authentication_classes = []
    permission_classes = []

    def create(self, request, sync_project_id, *args, **kwargs):
        project_id = sync_project_id
        return super(RepositorySyncByProjectAPIView, self).create(
            request, project_id, *args, **kwargs)


@with_code_wrapper
class PlainChartMuseumProviderCreateView(FilterByProjectMixin, viewsets.ViewSet):
    """Viewset for plain chart repository, this kind of repo don't provide chartmuseum
    """
    serializer_class = CreateRepoSLZ

    def create(self, request, project_id, *args, **kwargs):
        """Create Chart Repository
        """
        serializer = CreateRepoSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.data
        new_chart_repo = add_plain_repo(project_id=project_id, name=data["name"], url=data["url"])

        return Response(
            status=status.HTTP_200_OK,
            data=RepoSLZ(new_chart_repo).data
        )


class ChartVersionViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def get_chart_versions(self, chart_id, version_id):
        if version_id:
            chart_versions = ChartVersion.objects.filter(id=version_id)
        else:
            chart_versions = ChartVersion.objects.filter(chart__id=chart_id)
        if not chart_versions:
            raise ValidationError(_("没有查询到chart对应的版本信息"))
        return chart_versions

    def get_release_queryset(self, chart_id, version_id):
        # 获取chart version
        chart_versions = self.get_chart_versions(chart_id, version_id)
        # 因为是同一个chart，所以通过第一个version信息获取
        chart = chart_versions[0].chart
        version_list = [info.version for info in chart_versions]
        # 根据version和chart_name, 过滤相应的release
        return App.objects.filter(version__in=version_list, chart=chart)

    def release_list(self, request, project_id, chart_id):
        """查询chart下的release
        如果有传递version id，则查询version id对应的信息
        """
        # version id
        version_id = request.query_params.get("version_id")
        release_qs = self.get_release_queryset(chart_id, version_id)
        data = release_qs.values(
            "id", "name", "cluster_id", "namespace", "namespace_id"
        )

        return Response(data)

    def delete(self, request, project_id, chart_id):
        """删除chart或指定的chart版本
        """
        version_id = request.query_params.get("version_id")
        release_qs = self.get_release_queryset(chart_id, version_id)
        # 如果release不为空，则不能进行删除
        if release_qs.exists():
            raise ValidationError(_("chart下存在release，请先删除release"))
        # 如果指定version id，则只删除指定的version，否则删除所有version及chart
        chart_versions = self.get_chart_versions(chart_id, version_id)
        for info in chart_versions:
            repo_info = info.chart.repository
            auth = repo_info.plain_auths
            # 如果auth为空，则赋值为空
            if not auth:
                username = pwd = ""
            else:
                credentials = auth[0]["credentials"]
                username = credentials["username"]
                pwd = credentials["password"]
            # 删除repo中chart版本记录
            delete_chart_version(repo_info.url, info.chart.name, info.version, username, pwd)
            # 处理digest不变动的情况
            ChartVersionSnapshot.objects.filter(digest=info.digest).delete()
            # 删除db中记录
            info.delete()

        # 如果chart下没有版本了，则删除chart，否则如果默认版本删除了，调整chart的对应的默认版本
        chart_all_versions = ChartVersion.objects.filter(chart__id=chart_id)
        chart = Chart.objects.filter(id=chart_id)
        if chart.first().defaultChartVersion is None:
            chart.update(defaultChartVersion=chart_all_versions.order_by("-created")[0])
        elif not chart_all_versions:
            chart.delete()

        # 设置commit id为空，以防出现相同版本digest不变动的情况
        Repository.objects.filter(
            project_id=project_id
        ).exclude(name="public-repo").update(commit=None)

        return Response()
