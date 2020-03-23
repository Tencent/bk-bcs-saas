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
"""
this is the operations for helm cli

required: helm 2.9.1
"""

import os
import time
import subprocess
import logging
import tempfile
import shutil

from django.conf import settings

from .exceptions import HelmError, HelmExecutionError

from backend.apps.whitelist_bk import enable_helm_v3

logger = logging.getLogger(__name__)


def write_files(temp_dir, files):
    for name, content in files.items():
        path = os.path.join(temp_dir, name)
        base_path = os.path.dirname(path)
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        with open(path, "w") as f:
            f.write(content)

    for name, _ in files.items():
        parts = name.split("/")
        if len(parts) > 0:
            return os.path.join(temp_dir, parts[0])

    return temp_dir


class KubeHelmClient:
    """
    render the templates with values.yaml / answers.yaml
    NOTE: helm3 和 helm2的命令执行参数不同
    """

    def __init__(self, helm_bin="helm", kubeconfig=""):
        self.helm_bin = helm_bin
        self.kubeconfig = kubeconfig

    def _make_answers_to_args(self, answers):
        """
        {"a": 1, "b": 2, "c": "3"} => ["--set", "a=1,b=2", "--set-string", "3"]
        """
        if not answers:
            return []
        set_values = ','.join(["{k}={v}".format(k=k, v=v) for k, v in answers.items() if not isinstance(v, str)])
        set_stirng_values = ','.join(["{k}={v}".format(k=k, v=v) for k, v in answers.items() if isinstance(v, str)])
        return ["--set", set_values, "--set-string", set_stirng_values]

    def _get_cmd_args_for_template(self, root_dir, app_name, namespace, cluster_id):
        if enable_helm_v3(cluster_id):
            return [
                settings.HELM3_BIN,
                "template",
                app_name,
                root_dir,
                "--namespace",
                namespace
            ]

        return [
            settings.HELM_BIN,
            "template",
            root_dir,
            "--name",
            app_name,
            "--namespace",
            namespace,
        ]

    # def template(self, release, namespace: str):
    def template(self, files, name, namespace: str, parameters: dict, valuefile: str, cluster_id=None):
        """
        helm template {dir} --name {name} --namespace {namespace} --set k1=v1,k2=v2,k3=v3 --values filename
        """
        app_name = name or "default"

        temp_dir = tempfile.mkdtemp()
        valuefile_name = None
        try:
            # 1. write template files into fp
            root_dir = write_files(temp_dir, files)

            # 2. parse answers.yaml to values
            values = self._make_answers_to_args(parameters)

            # 3. construct cmd and run
            base_cmd_args = self._get_cmd_args_for_template(root_dir, app_name, namespace, cluster_id)

            # 4.1 helm template
            template_cmd_args = base_cmd_args
            if values:
                template_cmd_args += values

            if valuefile:
                FILENAME = "__valuefile__.yaml"
                valuefile_x = {FILENAME: valuefile}
                write_files(temp_dir, valuefile_x)
                valuefile_name = os.path.join(temp_dir, FILENAME)
                template_cmd_args += ["--values", valuefile_name]

            template_out, _ = self._run_command_with_retry(max_retries=0, cmd_args=template_cmd_args)

            # 4.2 helm template --notes
            notes_out = ""
            # not be used currently, comment it for accelerate
            # notes_cmd_args = base_cmd_args + ["--notes"]
            # notes_out, _ = self._run_command_with_retry(max_retries=0, cmd_args=notes_cmd_args)

        except Exception as e:
            logger.exception(
                ("do helm template fail: namespace={namespace}, name={name}\n"
                 "parameters={parameters}\nvaluefile={valuefile}\nfiles={files}").format(
                    namespace=namespace,
                    name=name,
                    parameters=parameters,
                    valuefile=valuefile,
                    files=files,
                ))
            raise e
        finally:
            shutil.rmtree(temp_dir)

        return template_out, notes_out

    def install(self, name, namespace, tmpl_content, chart_name, chart_version, chart_values, chart_api_version):
        """install helm chart
        NOTE: 这里需要组装chart格式，才能使用helm install
        必要条件
        - Chart.yaml
        - templates/xxx.yaml
        步骤:
        - 写临时文件, 用于组装chart结构
        - 组装命令行参数
        - 执行命令
        """
        temp_dir = tempfile.mkdtemp()
        try:
            root_dir = write_chart_files(
                temp_dir, tmpl_content, chart_name, chart_version, chart_values, chart_api_version)
            install_cmd_args = [
                settings.HELM3_BIN,
                "install",
                name,
                root_dir,
                "--namespace",
                namespace
            ]
            cmd_out, cmd_err = self._run_command_with_retry(max_retries=0, cmd_args=install_cmd_args)
        except Exception as e:
            logger.exception(
                "实例化chart失败: name=%s, namespace=%s, content=%s", name, namespace, tmpl_content)
            raise e
        finally:
            shutil.rmtree(temp_dir)

        return cmd_out, cmd_err

    def upgrade(self, name, namespace, tmpl_content, chart_name, chart_version, chart_values, chart_api_version):
        """upgrade helm release
        NOTE: 这里需要组装chart格式，才能使用helm upgrade
        必要条件
        - Chart.yaml
        - templates/xxx.yaml
        步骤:
        - 写临时文件, 用于组装chart结构
        - 组装命令行参数
        - 执行命令
        """
        temp_dir = tempfile.mkdtemp()
        try:
            root_dir = write_chart_files(
                temp_dir, tmpl_content, chart_name, chart_version, chart_values, chart_api_version)
            upgrade_cmd_args = [
                settings.HELM3_BIN,
                "upgrade",
                name,
                root_dir,
                "--namespace",
                namespace
            ]
            cmd_out, cmd_err = self._run_command_with_retry(max_retries=0, cmd_args=upgrade_cmd_args)
        except Exception as e:
            logger.exception(
                "升级release失败: name=%s, namespace=%s, content=%s", name, namespace, tmpl_content)
            raise e
        finally:
            shutil.rmtree(temp_dir)

        return cmd_out, cmd_err

    def uninstall(self, name, namespace):
        """uninstall helm release"""
        try:
            uninstall_cmd_args = [
                settings.HELM3_BIN,
                "uninstall",
                name,
                "--namespace",
                namespace
            ]
            cmd_out, cmd_err = self._run_command_with_retry(max_retries=0, cmd_args=uninstall_cmd_args)
        except Exception as e:
            logger.exception("删除release失败: name=%s, namespace=%s", name, namespace)
            raise e

        return cmd_out, cmd_err

    def rollback(self, name, namespace, revision):
        """rollback helm release by revision"""
        try:
            rollback_cmd_args = [
                settings.HELM3_BIN,
                "rollback",
                name,
                str(revision),
                "--namespace",
                namespace
            ]
            cmd_out, cmd_err = self._run_command_with_retry(max_retries=0, cmd_args=rollback_cmd_args)
        except Exception as e:
            logger.exception("回滚release失败: name=%s, namespace=%s， revision=%s", name, namespace, revision)
            raise e

        return cmd_out, cmd_err

    def _run_command_with_retry(self, max_retries=1, *args, **kwargs):
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
            else:
                break

        raise ValueError(max_retries)

    def _run_command(self, cmd_args):
        """Run the helm command with wrapped exceptions
        """
        try:
            logger.info("Calling helm cmd, cmd: (%s)", " ".join(cmd_args))

            proc = subprocess.Popen(
                cmd_args, shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={"KUBECONFIG": self.kubeconfig}  # 添加连接集群信息
            )
            stdout, stderr = proc.communicate()

            if proc.returncode != 0:
                logger.exception("Unable to run helm command, return code: %s, output: %s",
                                 proc.returncode, stderr)
                raise HelmExecutionError(proc.returncode, stderr)

            return stdout, stderr
        except Exception as err:
            logger.exception("Unable to run helm command")
            raise HelmError("run helm command failed: {}".format(err))


def write_chart_files(temp_dir, tmpl_content, chart_name, chart_version, chart_values, chart_api_version):
    """创建chart结构
    - Chart.yaml
    - templates/xxx.yaml
    """
    chart_config_path = os.path.join(temp_dir, "Chart.yaml")
    # 写chart内容
    with open(chart_config_path, "w") as f:
        chart_config = f"apiVersion={chart_api_version}\nname={chart_name}\nversion={chart_version}"
        f.write(chart_config)

    tmpl_content_path = os.path.join(temp_dir, "templates/content.yaml")
    # 写templates下的内容
    with open(tmpl_content_path, "w") as f:
        f.write(tmpl_content)

    values_path = os.path.join(temp_dir, "values.yaml")
    # 写values是可选的，写入的目的主要是因为helm get values，获取线上的相关信息
    with open(values_path, "w") as f:
        f.write(chart_values)

    return temp_dir
