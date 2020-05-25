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
import json
import logging

from django.conf import settings

from backend.components.utils import http_delete
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


def delete_chart_version(prefix_path, chart_name, version, username, pwd):
    url = f"{prefix_path}/api/charts/{chart_name}/version"
    resp = http_delete(url, auth=(username, pwd), raise_for_status=False)
    # 返回{"deleted" : True} 或 {"error" : "remove xxx failed: no such file or directory"}
    if not (resp.get("deleted") or "no such file or directory" in resp.get("error", "")):
        raise error_codes.APIError(_("删除chart失败,{}").format(resp))
    return resp
