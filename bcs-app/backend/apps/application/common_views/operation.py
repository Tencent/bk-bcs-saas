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
import json

from rest_framework import response, viewsets
from rest_framework.renderers import BrowsableAPIRenderer
from django.utils.translation import ugettext_lazy as _

from backend.activity_log import client
from backend.utils.basic import getitems
from backend.utils.renderers import BKAPIRenderer
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes
from backend.apps.application.base_views import InstanceAPI
from backend.apps.application import constants as app_constants
from backend.apps.instance.constants import InsState

logger = logging.getLogger(__name__)


class RollbackPreviousVersion(InstanceAPI, viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def get_config(self, config):
        try:
            return json.loads(config)
        except Exception as err:
            logger.error("解析实例配置异常，配置: %s，错误详情: %s", config, err)
            return {}

    def from_template(self, instance_id):
        if not self._from_template(instance_id):
            raise error_codes.CheckFailed(_("非模板集实例化的应用不允许进行回滚操作"))

    def get_last_config(self, instance_detail):
        last_config = self.get_config(instance_detail.last_config)
        last_config = last_config.get('old_conf') or {}
        if not last_config:
            raise error_codes.CheckFailed(_("请确认已经执行过更新或滚动升级"))
        return last_config

    def get_current_config(self, instance_detail):
        current_config = self.get_config(instance_detail.config)
        if not current_config:
            raise error_codes.CheckFailed(_("获取实例配置为空"))

        return current_config

    def get(self, request, project_id, instance_id):
        # 检查是否是模板集创建
        self.from_template(instance_id)
        # 校验权限
        self.can_use_instance(request, project_id, instance_id)
        instance_detail = self.get_instance_info(instance_id).first()
        # 获取实例的config
        current_config = self.get_current_config(instance_detail)
        last_config = self.get_last_config(instance_detail)

        data = {
            'current_config': current_config,
            'current_config_yaml': self.json2yaml(last_config),
            'last_config': last_config,
            'last_config_yaml': self.json2yaml(last_config)
        }

        return response.Response(data)

    def update_resource(self, request, project_id, cluster_id, namespace, config, instance_detail):
        resp = self.update_deployment(
            request, project_id, cluster_id, namespace, config,
            kind=request.project.kind, category=instance_detail.category, app_name=instance_detail.name
        )
        is_bcs_success = True if resp.data.get('code') == ErrorCode.NoError else False
        # 更新状态
        instance_detail.oper_type = app_constants.ROLLING_UPDATE_INSTANCE
        instance_detail.is_bcs_success = is_bcs_success
        if not is_bcs_success:
            # 出异常时，保存一次；如果正常，最后保存；减少save次数
            instance_detail.save()
            raise error_codes.APIError(_("回滚上一版本失败，{}").format(resp.data.get('message')))
        # 更新配置
        instance_last_config = json.loads(instance_detail.last_config)
        instance_last_config['old_conf'] = json.loads(instance_detail.config)
        instance_detail.last_config = json.dumps(instance_last_config)
        instance_detail.config = json.dumps(config)
        instance_detail.save()

    def update(self, request, project_id, instance_id):
        """回滚上一版本，只有模板集实例化的才会
        1. 判断当前实例允许回滚
        2. 对应实例的配置
        3. 下发更新操作
        """
        # 检查是否来源于模板集
        self.from_template(instance_id)
        # 校验权限
        self.can_use_instance(request, project_id, instance_id)
        instance_detail = self.get_instance_info(instance_id).first()
        # 获取实例的config
        current_config = self.get_current_config(instance_detail)
        last_config = self.get_last_config(instance_detail)
        # 兼容annotation和label
        cluster_id = getitems(current_config, ['metadata', 'annotations', 'io.tencent.bcs.cluster'], '')
        if not cluster_id:
            cluster_id = getitems(current_config, ['metadata', 'labels', 'io.tencent.bcs.cluster'], '')
        namespace = getitems(current_config, ['metadata', 'namespace'], '')
        desc = _("集群:{}, 命名空间:{}, 应用:[{}] 回滚上一版本").format(cluster_id, namespace, instance_detail.name)
        # 下发配置
        with client.ContextActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type="instance",
            resource=instance_detail.name,
            resource_id=instance_id,
            description=desc
        ).log_modify():
            self.update_resource(request, project_id, cluster_id, namespace, last_config, instance_detail)

        return response.Response()
