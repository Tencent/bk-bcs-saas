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
from rest_framework.response import Response

from backend.bcs_web import viewsets

from .permissions.apply_url import ApplyURLGenerator
from .permissions.client import IAMClient
from .permissions.request import ActionResourcesRequest
from .request_maker import make_res_request
from .serializers import ResourceActionSLZ, ResourceMultiActionsSLZ


class UserPermsViewSet(viewsets.SystemViewSet):
    def get_perms(self, request):
        """查询多个 action_id 的权限"""
        validated_data = self.params_validate(ResourceMultiActionsSLZ)

        client = IAMClient()

        resource_type = validated_data.get('resource_type')
        if not resource_type:  # 资源实例无关
            perms = client.resource_type_multi_actions_allowed(request.user.username, validated_data['action_ids'])
            return Response({'perms': perms})

        # 资源实例相关
        res_request = make_res_request(
            resource_type, validated_data['resource_id'], **validated_data['iam_path_attrs']
        )
        perms = client.resource_inst_multi_actions_allowed(
            request.user.username, validated_data['action_ids'], res_request
        )
        return Response({'perms': perms})

    def get_perm_by_action_id(self, request, action_id):
        """查询指定 action_id 的权限"""
        validated_data = self.params_validate(ResourceActionSLZ, action_id=action_id)

        client = IAMClient()

        resource_type = validated_data.get('resource_type')
        if resource_type:  # 资源实例相关
            res_request = make_res_request(
                resource_type, validated_data['resource_id'], **validated_data['iam_path_attrs']
            )
            is_allowed = client.resource_inst_allowed(request.user.username, action_id, res_request)
        else:  # 资源实例无关
            is_allowed = client.resource_type_allowed(request.user.username, action_id)

        perms = {action_id: is_allowed}
        # 无权限时，带上权限申请跳转链接
        if not is_allowed:
            perms['apply_url'] = ApplyURLGenerator.generate_apply_url(
                request.user.username,
                action_request_list=[
                    ActionResourcesRequest(
                        action_id=action_id,
                        resource_type=resource_type,
                        resources=[validated_data['resource_id']] if resource_type else None,
                    )
                ],
            )

        return Response({'perms': perms})
