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
from backend.apps.instance import models


class DeployController:
    def __init__(self, manifests):
        self.manifests = manifests

    def apply(self):
        models.VersionInstance.objects.create()

        # class VersionInstance(BaseModel):
        #     """版本实例化信息
        #     instance_entity 字段内容如下：表名：记录ID
        #     {
        #         'application': 'ApplicationID1,ApplicationID2,ApplicationID3',
        #         'service': 'ServiceID1,ServiceID2',
        #         ...
        #     }
        #     from backend.apps.configuration.models import MODULE_DICT
        #     MODULE_DICT 记录 `表名` 和  `model` 的对应关系，并且所有的 `model` 都定义了 `get_name` 方法来查看名称
        #     """
        #     version_id = models.IntegerField(u"关联的VersionedEntity ID")
        #     instance_entity = models.TextField(u"需要实例化的资源", help_text=u"json格式数据")
        #     is_start = models.BooleanField(
        #         default=False, help_text=u"false:生成配置文件；true:生成配置文件，调用bsc api实例化配置信息")
        #     # add by 应用更新操作
        #     ns_id = models.IntegerField(u"命名空间ID")
        #     template_id = models.IntegerField(u"关联的模板 ID", help_text=u"该字段只在db中查看使用")
        #     history = models.TextField(u"历史变更数据", help_text=u"以json格式存储")
        #     is_bcs_success = models.BooleanField(u"调用BCS API 是否成功", default=True)
        #     # 添加用户可见版本
        #     show_version_id = models.IntegerField(u"用户可见版本ID", default=0)
        #     show_version_name = models.CharField(
        #         u"用户可见版本Name", max_length=255, default='')

    def delete(self):
        pass
