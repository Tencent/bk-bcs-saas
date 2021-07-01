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
import subprocess
import time
from typing import List, Tuple

from .exceptions import HelmError, HelmExecutionError
from .options import Options

logger = logging.getLogger(__name__)


class HelmClient:
    """helm client，用于chart的渲染、部署、更新等"""

    def __init__(self, helm: str = "helm", kubeconfig: str = ""):
        """
        :param helm: helm所在的绝对路径
        :param kubeconfig: 连接集群的配置信息
        """
        self.helm = helm
        self.kubeconfig = kubeconfig

    def run(
        self, command: str, name: str, namespace: str, chart: str = None, options: List[str] = None
    ) -> Tuple[bytes, bytes]:
        """执行命令
        :param command: helm允许的命令，例如 install、rollback等
        :param name: 操作的release名称
        :param namespace: 操作的命名空间
        :param chart: chart路径，允许本地路径、远程url、tar包等
        :param options: helm命令允许的参数，格式: ["--set", "a=1", "--values", "/values.yaml"]
        """
        cmd_args = [self.helm, command, name, "--namespace", namespace]
        cmd_args.extend(options)
        # 针对需要chart的添加上指定的chart地址
        if chart:
            cmd_args.append(chart)
        return self._run_command_with_retry(cmd_args=cmd_args)

    # TODO: retry相关是否可以放到一个公共的地方，针对kubectl和helm以及后续的其它二进制都可以使用
    def _run_command_with_retry(self, max_retries: int = 0, *args, **kwargs) -> Tuple[bytes, bytes]:
        for i in range(max_retries + 1):
            try:
                stdout, stderr = self._run_command(*args, **kwargs)
                return stdout, stderr
            except Exception:
                if i == max_retries:
                    raise

                # retry after 0.5, 1, 1.5, ... seconds
                time.sleep((i + 1) * 0.5)
                continue

    def _run_command(self, cmd_args: List[str]) -> Tuple[bytes, bytes]:
        """Run the helm command with wrapped exceptions"""
        try:
            logger.info("Calling helm cmd, cmd: (%s)", " ".join(cmd_args))

            proc = subprocess.Popen(
                cmd_args,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={"KUBECONFIG": self.kubeconfig},
            )
            stdout, stderr = proc.communicate()

            if proc.returncode != 0:
                logger.exception("Unable to run helm command, return code: %s, output: %s", proc.returncode, stderr)
                raise HelmExecutionError(proc.returncode, stderr)

            return stdout, stderr
        except Exception as err:
            logger.exception("Unable to run helm command")
            raise HelmError("run helm command failed: {}".format(err))
