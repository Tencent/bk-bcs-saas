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
import contextlib
import json
import logging
import os
import shutil
import stat
import subprocess
import tempfile
import time
from dataclasses import asdict
from typing import List

from django.conf import settings
from django.template.loader import render_to_string

from .exceptions import HelmError, HelmExecutionError, HelmMaxTryError
from .options import Options

logger = logging.getLogger(__name__)


class HelmClient:
    """helm client
    用于helm命令，例如: helm template, helm install, helm upgrade 等
    更详细可以参考 helm -h
    """

    def __init__(self, helm_bin: str = "helm", kubeconfig: str = ""):
        """
        :params helm_bin: helm 二进制文件路径
        :params kubeconfig: 连接集群需要的config
        """
        self.helm = helm_bin
        self.kubeconfig = kubeconfig

    def _run_command_with_retry(self, max_retries: int = 1, *args, **kwargs):
        for i in range(max_retries + 1):
            try:
                stdout, stderr = self._run_command(*args, **kwargs)
                return stdout, stderr
            except Exception:
                if i == max_retries:
                    raise

                # 沿用重试等待时间
                # retry after 0.5, 1, 1.5, ... seconds
                time.sleep((i + 1) * 0.5)
                continue

        raise HelmMaxTryError(f"max retries {max_retries} fail")

    def _run_command(self, cmd_args: List):
        """Run the helm command with wrapped exceptions"""
        try:
            logger.info("Calling helm cmd, cmd: (%s)", " ".join(cmd_args))

            proc = subprocess.Popen(
                cmd_args,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={"KUBECONFIG": self.kubeconfig},  # 添加连接集群配置信息
            )
            stdout, stderr = proc.communicate()

            if proc.returncode != 0:
                logger.exception("Unable to run helm command, return code: %s, output: %s", proc.returncode, stderr)
                raise HelmExecutionError(proc.returncode, stderr)

            return stdout, stderr
        except Exception as err:
            logger.exception("Unable to run helm command")
            raise HelmError("run helm command failed: {}".format(err))
