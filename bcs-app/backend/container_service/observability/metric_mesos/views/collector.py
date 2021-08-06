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
import logging

from django.utils.translation import ugettext as _
from rest_framework import viewsets
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response

from backend.accounts import bcs_perm
from backend.apps.constants import ALL_LIMIT, ProjectKind
from backend.components import paas_cc
from backend.container_service.observability.metric_mesos import serializers, tasks
from backend.container_service.observability.metric_mesos.models import Metric as MetricModel
from backend.container_service.observability.metric_mesos.utils import get_metric_instances
from backend.templatesets.legacy_apps.configuration.models import POD_RES_LIST
from backend.templatesets.legacy_apps.instance.constants import InsState
from backend.templatesets.legacy_apps.instance.models import InstanceConfig
from backend.utils.error_codes import error_codes
from backend.utils.renderers import BKAPIRenderer
from backend.utils.response import BKAPIResponse

try:
    from backend.container_service.observability.datalog.data_collect import (
        apply_dataid_by_metric,
        create_prometheus_data_flow,
        get_metric_data_name,
    )
except ImportError:
    from backend.container_service.observability.datalog_ce.data_collect import (
        apply_dataid_by_metric,
        create_prometheus_data_flow,
        get_metric_data_name,
    )

logger = logging.getLogger(__name__)
PAUSE = 'pause'


class Metric(viewsets.ViewSet):
    """metric列表"""

    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def list(self, request, project_id):
        """获取metric列表"""
        refs = MetricModel.objects.filter(project_id=project_id).order_by('-updated')
        data = [i.to_json() for i in refs]

        # 过滤有使用权限的命名空间
        perm_can_use = request.GET.get('perm_can_use')
        if perm_can_use == '1':
            perm_can_use = True
        else:
            perm_can_use = False
        perm = bcs_perm.Metric(request, project_id, bcs_perm.NO_RES)
        data = perm.hook_perms(data, perm_can_use)

        # 返回是否有创建权限
        can_create = perm.can_create(raise_exception=False)

        return BKAPIResponse(data, message=_('获取metric列表成功'), permissions={'create': can_create})

    def create(self, request, project_id):
        """创建metric"""
        cc_app_id = request.project.get('cc_app_id')
        if not cc_app_id:
            raise error_codes.APIError(_('必须绑定业务'))

        serializer = serializers.CreateMetricSLZ(
            data=request.data, context={'request': request, 'project_id': project_id}
        )
        serializer.is_valid(raise_exception=True)

        # 校验权限
        perm = bcs_perm.Metric(request, project_id, bcs_perm.NO_RES)
        perm.can_create(raise_exception=True)

        dataset = get_metric_data_name(serializer.data['name'], project_id)

        metric_type = serializer.data['metric_type']
        if metric_type == 'prometheus':
            # prometheus 申请dataid的时候同时配置默认的清洗规则
            username = request.user.username
            english_name = request.project.english_name
            is_ok, data_id = create_prometheus_data_flow(username, project_id, cc_app_id, english_name, dataset)
            err_msg = data_id
        else:
            is_ok, data_id = apply_dataid_by_metric(cc_app_id, dataset, request.user.username)
            err_msg = _('申请data_id失败')

        if not is_ok:
            raise error_codes.APIError(err_msg)

        ref = MetricModel(
            creator=request.user.username,
            updator=request.user.username,
            data_id=data_id,
            project_id=project_id,
            **serializer.data
        )
        ref.save()

        # 创建资源
        perm.register(ref.id, ref.name)

        return BKAPIResponse({'metric_id': ref.pk}, message=_('创建metric成功'))


class MetricDetail(viewsets.ViewSet):
    """单个metric操作"""

    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def get(self, request, project_id, metric_id):
        """获取metric"""
        ref = MetricModel.objects.filter(project_id=project_id, pk=metric_id).first()
        if not ref:
            raise error_codes.ResNotFoundError(_('metric不存在'))

        # 校验权限
        perm = bcs_perm.Metric(request, project_id, metric_id, ref.name)
        perm.can_use(raise_exception=True)

        return BKAPIResponse(ref.to_json(), message=_('获取metric成功'))

    def put(self, request, project_id, metric_id):
        """更新put"""
        serializer = serializers.UpdateMetricSLZ(
            data=request.data, context={'request': request, 'project_id': project_id}
        )
        serializer.is_valid(raise_exception=True)

        queryset = MetricModel.objects.filter(project_id=project_id, pk=metric_id)
        ref = queryset.first()
        if not ref:
            raise error_codes.ResNotFoundError(_('metric不存在'))

        # metric_type 不可变，创建是已经申请了dataid，编辑时不能编辑dataid的属性
        if ref.metric_type != serializer.data.get('metric_type', ''):
            raise error_codes.APIError(_('Metric 类型不可更改'))

        # 校验权限
        perm = bcs_perm.Metric(request, project_id, metric_id, ref.name)
        perm.can_edit(raise_exception=True)

        # 更新version
        queryset.update(updator=request.user.username, version=ref.update_version(), **serializer.data)

        # 异步下发metric
        tasks.set_metric.delay(request.user.token.access_token, project_id, request.project['kind'], metric_id)

        return BKAPIResponse({}, message=_('修改metric成功'))

    def get_metric_info(self, project_id, metric_id):
        """获取metric信息"""
        resource = MetricModel.objects.filter(project_id=project_id, pk=metric_id).first()
        if not resource:
            raise error_codes.ResNotFoundError(_('metric 不存在'))

        return resource

    def delete(self, request, project_id, metric_id):
        """删除
        注意: 添加一个暂停的操作，这个暂停的含义包含
        1. 调用接口删除metric
        2. 更新记录状态为pause状态
        """
        ref = self.get_metric_info(project_id, metric_id)

        # 校验权限
        perm = bcs_perm.Metric(request, project_id, metric_id, ref.name)
        perm.can_delete(raise_exception=True)

        data = dict(request.data)
        op_type = data.get('op_type')
        ns_id_list = data.get('ns_id_list') or []
        tasks.delete_metric.delay(
            request.user.token.access_token,
            project_id,
            request.project['kind'],
            metric_id,
            op_type=op_type,
            ns_id_list=ns_id_list,
        )
        # 针对暂停操作，添加 op_type 参数
        if op_type == PAUSE:
            ref.update_status(PAUSE)
        else:
            ref.soft_delete()
            perm.delete()

        return BKAPIResponse({}, message=_('删除metric成功'))

    def recreate(self, request, project_id, metric_id):
        """重新创建
        1. 有操作权限
        2. 检查状态为pause
        3. 重新下发配置
        """
        ref = self.get_metric_info(project_id, metric_id)
        # 校验权限
        perm = bcs_perm.Metric(request, project_id, bcs_perm.NO_RES)
        perm.can_create(raise_exception=True)
        # 状态校验
        if ref.status != PAUSE:
            raise error_codes.APIError(_('metric不为暂停状态，不允许操作!'))
        else:
            ref.update_status('normal')
        if not request.project['cc_app_id']:
            raise error_codes.APIError(_('项目没有绑定业务，不允许操作!'))

        # 重新下发配置
        tasks.set_metric.delay(
            request.user.token.access_token,
            project_id,
            request.project['kind'],
            metric_id,
            ns_id_list=request.data.get('ns_id_list', []),
        )

        return BKAPIResponse({'metric_id': ref.pk}, message=_('创建metric成功'))


class MetricIns(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def get_instance(self, request, project_id, metric_id):
        """查询Metric实例化的详细信息"""
        ref = MetricModel.objects.filter(project_id=project_id, pk=metric_id).first()
        if not ref:
            raise error_codes.ResNotFoundError(_('metric不存在'))

        metric_name = ref.name

        # 查询项目下的所有集群id列表
        access_token = request.user.token.access_token
        cluster_data = paas_cc.get_all_clusters(access_token, project_id).get('data') or {}
        cluster_list = cluster_data.get('results') or []

        cluster_dict = {}
        for _n in cluster_list:
            _env = _n['environment']
            if _env in cluster_dict:
                cluster_dict[_env].append(_n['cluster_id'])
            else:
                cluster_dict[_env] = [_n['cluster_id']]

        # 查询项目下的命名空间列表
        access_token = request.user.token.access_token
        result = paas_cc.get_namespace_list(access_token, project_id, with_lb=0, limit=ALL_LIMIT)
        ns_list = result.get('data', {}).get('results') or []
        ns_dict = {}
        for _n in ns_list:
            ns_dict[_n['name']] = _n['id']

        if request.project.kind == ProjectKind.MESOS.value:
            # mesos
            category_list = ['application', 'deployment']
        else:
            category_list = POD_RES_LIST

        instance_info = InstanceConfig.objects.filter(is_deleted=False, category__in=category_list).exclude(
            ins_state=InsState.NO_INS.value
        )

        data = []
        # 根据集群的环境不同调用不同环境的storageAPI
        for env, cluster_id_list in cluster_dict.items():
            metric_instance_list = get_metric_instances(
                access_token, project_id, metric_name, env, cluster_id_list, ns_dict, instance_info
            )
            data.extend(metric_instance_list)

        return Response(data)
