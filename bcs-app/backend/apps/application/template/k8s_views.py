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

from backend.apps.application import constants
from backend.apps.configuration.models import VersionedEntity

CATEGORY_MAP = constants.CATEGORY_MAP


class K8STemplateSet(object):
    def get_template(self, tmpl_set_id_list, category):
        version_info = VersionedEntity.objects.filter(template_id__in=tmpl_set_id_list, is_deleted=False).order_by(
            "-updated", "-created"
        )
        # 存储模板
        tmpl = {}
        # 存储最新版本
        newest_version_tmpl = {}
        for info in version_info:
            entity = info.get_entity()
            if not entity:
                continue
            tmpl_ids = entity.get(CATEGORY_MAP[category])
            if not tmpl_ids:
                continue
            tmpl_id_list = tmpl_ids.split(",")
            if info.template_id in tmpl:
                if tmpl_id_list:
                    tmpl[info.template_id] = tmpl[info.template_id].union(set(tmpl_id_list))
            else:
                tmpl[info.template_id] = set([])
                newest_version_tmpl[info.template_id] = set([])

                if tmpl_id_list:
                    tmpl[info.template_id] = tmpl[info.template_id].union(set(tmpl_id_list))
                    newest_version_tmpl[info.template_id] = newest_version_tmpl[info.template_id].union(
                        set(tmpl_id_list)
                    )
        return tmpl, newest_version_tmpl
