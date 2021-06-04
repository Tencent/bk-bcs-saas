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
import base64
from typing import Dict, List

import yaml

from backend.utils.basic import getitems

from ..constants import BCS_INJECT_UPDATER_ANNOTATIONS


class ReleaseParser:
    def __init__(self, release: Dict):
        self.release = release

    @property
    def metadata(self) -> Dict:
        """获取release的基本信息"""
        return {
            "name": self.release["name"],
            "namespace": self.release["namespace"],
            "version": self.release["version"],
            **self.release["info"],
        }

    @property
    def notes(self) -> Dict:
        return getitems(self.release, ["info", "notes"], "")

    @property
    def values(self) -> Dict:
        """获取release使用的values"""
        # 如果有使用--values指定values内容，则需要在config中获取values，否则，使用chart中的values内容
        config = self.release.get("config", "")
        if not config:
            config = getitems(self.release, ["chart", "values"], "")
        # 如果为空直接返回
        if not config:
            return config
        # 如果存在，则转换为yaml
        return yaml.safe_dump(config)

    @property
    def manifest_list(self) -> List:
        """获取manifest"""
        return list(filter(lambda m: m.strip("-\t\n "), self.release.split("---\n")))

    @property
    def chart_metadata(self) -> Dict:
        """获取 release 使用的chart的基本信息"""
        return self.release["chart"]["metadata"]

    @property
    def chart_files(self) -> Dict:
        """获取release使用的chart下文件"""
        chart = self.release["chart"]
        templates = chart.get("templates") or []
        # chart模板中非values.yaml和Chart.yaml的文件
        files = chart.get("files") or []

        # 处理文件内容
        files = [{"name": file["name"], "data": base64.b64decode(file["data"]).decode("utf-8")} for file in files]
        files.extend(
            [
                {"name": template["name"], "data": base64.b64decode(template["data"]).decode("utf-8")}
                for template in templates
            ]
        )

        return files

    @property
    def release_updater(self) -> str:
        """获取release的更新者"""
        if not self.manifest_list:
            return ""
        # 以第一个资源的metadata的annotations中的io.tencent.paas.updater为release的更新者
        for field in BCS_INJECT_UPDATER_ANNOTATIONS:
            updater = getitems(self.manifest_list[0], ["metadata", "annotations", field], "")
            if updater:
                return updater
        return updater
