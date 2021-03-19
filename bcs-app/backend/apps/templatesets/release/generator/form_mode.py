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
from typing import List

from backend.apps.configuration import models as config_models
from backend.apps.instance.utils import get_ns_variable
from backend.apps.templatesets.models import ResourceData


class FormtoResourceList:
    """表单模板集资源转换生成List[ResourceData]"""

    # TODO 重构apps/instance模块, 挪到当前templatesets模块下
    def generate(self, *args, **kwargs) -> List[ResourceData]:
        """
        先复用apps/instance/utils.generate_namespace_config中的大部分逻辑，完成resource_list的生成
        传入的params结构{
            "instance_id": "",
            "version": version,
            "version_id": version_id,
            "show_version_id": show_version_id,
            "template_id": template_id,
            "project_id": project_id,
            "access_token": access_token,
            "username": username,
            "lb_info": lb_info,
            "variable_dict": variable_dict,
            "is_preview": True, # 可选
        }
        """
        instance_entity = kwargs.get("instance_entity", {})
        namespace_id = kwargs.get("namespace_id", 0)
        params = kwargs.get("params", {})

        show_version_id = params.get('show_version_id')
        show_version_name = config_models.ShowVersion.objects.get(id=show_version_id).name

        # 查询命名空间相关的参数, 系统变量等保存在context中
        has_image_secret, cluster_version, context = get_ns_variable(
            params.get('access_token'), params.get('project_id'), namespace_id
        )
        params.update(
            {
                'version': show_version_name,
                'has_image_secret': has_image_secret,
                'cluster_version': cluster_version,
                'context': context,
            }
        )

        for entity in instance_entity:
            pass

        # for item in instance_entity:
        #     item_id_list = instance_entity[item]
        #     item_config = []
        #     for item_id in item_id_list:
        #         generator = GENERATOR_DICT.get(item)(item_id, namespace_id, is_validate, **params)
        #         file_content = generator.get_config_profile()
        #         file_name = generator.resource_show_name
        #
        #         try:
        #             show_config = json.loads(file_content)
        #         except Exception:
        #             show_config = file_content

        return ["1"]
