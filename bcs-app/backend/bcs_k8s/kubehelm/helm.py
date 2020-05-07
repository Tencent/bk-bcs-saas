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
import stat
import time
import subprocess
import logging
import tempfile
import shutil
import json
import contextlib
from dataclasses import asdict

from django.conf import settings
from django.template.loader import render_to_string

from .exceptions import HelmError, HelmExecutionError
from backend.apps.whitelist_bk import enable_helm_v3

logger = logging.getLogger(__name__)

YTT_RENDERER_NAME = "ytt_renderer"


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
    def template(self, files, name, namespace, parameters, valuefile, cluster_id=None):
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

    def template_with_ytt_renderer(self, files, name, namespace, parameters, valuefile, cluster_id, bcs_inject_data):
        """支持post renderer的helm template，并使用ytt(YAML Templating Tool)注入平台信息
        命令: helm template release_name chart -n namespace --post-renderer ytt-renderer
        """
        try:
            with write_chart_with_ytt(files, bcs_inject_data) as (temp_dir, ytt_config_dir):
                # 1. parse answers.yaml to values
                values = self._make_answers_to_args(parameters)

                # 2. construct cmd and run
                base_cmd_args = [
                    settings.HELM3_BIN,
                    "template",
                    name,
                    temp_dir,
                    "--namespace",
                    namespace
                ]

                # 3. helm template command params
                template_cmd_args = base_cmd_args
                if values:
                    template_cmd_args += values

                # 兼容先前逻辑
                if valuefile:
                    FILENAME = "__valuefile__.yaml"
                    valuefile_x = {FILENAME: valuefile}
                    write_files(temp_dir, valuefile_x)
                    valuefile_name = os.path.join(temp_dir, FILENAME)
                    template_cmd_args += ["--values", valuefile_name]

                # 4. add post render params
                template_cmd_args += ["--post-renderer", f"{ytt_config_dir}/{YTT_RENDERER_NAME}"]

                template_out, _ = self._run_command_with_retry(max_retries=0, cmd_args=template_cmd_args)
                # NOTE: 现阶段不需要helm notes输出
                notes_out = ""

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

        return template_out, notes_out

    def _install_or_upgrade(self, cmd_args, tmpl_content, chart_name, chart_version, chart_values, chart_api_version):
        try:
            with write_chart_dir(
                tmpl_content, chart_name, chart_version, chart_values, chart_api_version
            ) as temp_dir:
                cmd_args.append(temp_dir)
                cmd_out, cmd_err = self._run_command_with_retry(max_retries=0, cmd_args=cmd_args)
        except Exception as e:
            logger.exception("执行helm命令失败，命令参数: %s", json.dumps(cmd_args))
            raise e

        return cmd_out, cmd_err

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
        install_cmd_args = [settings.HELM3_BIN, "install", name, "--namespace", namespace]
        return self._install_or_upgrade(
            install_cmd_args,
            tmpl_content,
            chart_name,
            chart_version,
            chart_values,
            chart_api_version
        )

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
        upgrade_cmd_args = [settings.HELM3_BIN, "upgrade", name, "--namespace", namespace]
        return self._install_or_upgrade(
            upgrade_cmd_args,
            tmpl_content,
            chart_name,
            chart_version,
            chart_values,
            chart_api_version
        )

    def _uninstall_or_rollback(self, cmd_args):
        try:
            cmd_out, cmd_err = self._run_command_with_retry(max_retries=0, cmd_args=cmd_args)
        except Exception as e:
            logger.exception("执行helm命令失败，命令参数: %s", json.dumps(cmd_args))
            raise e

        return cmd_out, cmd_err

    def uninstall(self, name, namespace):
        """uninstall helm release"""
        uninstall_cmd_args = [settings.HELM3_BIN, "uninstall", name, "--namespace", namespace]
        return self._uninstall_or_rollback(uninstall_cmd_args)

    def rollback(self, name, namespace, revision):
        """rollback helm release by revision"""
        rollback_cmd_args = [settings.HELM3_BIN, "rollback", name, str(revision), "--namespace", namespace]
        return self._uninstall_or_rollback(rollback_cmd_args)

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


@contextlib.contextmanager
def write_chart_dir(tmpl_content, chart_name, chart_version, chart_values, chart_api_version):
    """创建chart结构
    - Chart.yaml
    - templates/xxx.yaml
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        chart_config_path = os.path.join(temp_dir, "Chart.yaml")
        # 写chart内容
        with open(chart_config_path, "w") as f:
            chart_config = f"apiVersion: {chart_api_version}\nname: {chart_name}\nversion: {chart_version}"
            f.write(chart_config)

        tmpl_path = os.path.join(temp_dir, "templates")
        if not os.path.exists(tmpl_path):
            os.makedirs(tmpl_path)
        tmpl_content_path = os.path.join(tmpl_path, "content.yaml")
        # 写templates下的内容
        with open(tmpl_content_path, "w") as f:
            f.write(tmpl_content)

        values_path = os.path.join(temp_dir, "values.yaml")
        # 写values是可选的，写入的目的主要是因为helm get values，获取线上的相关信息
        with open(values_path, "w") as f:
            f.write(chart_values)

        yield temp_dir


@contextlib.contextmanager
def write_chart_with_ytt(files, bcs_inject_data):
    """组装helm template功能需要的文件，并且使用ytt注入平台需要的信息
    主要包含以下两部分
    - chart部分
    - ytt配置部分
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        for name, content in files.items():
            path = os.path.join(temp_dir, name)
            base_path = os.path.dirname(path)
            if not os.path.exists(base_path):
                os.makedirs(base_path)

            with open(path, "w") as f:
                f.write(content)

        # 获取chart配置的目录
        chart_dir = temp_dir
        for name, _ in files.items():
            parts = name.split("/")
            if len(parts) > 0:
                chart_dir = os.path.join(temp_dir, parts[0])
                break

        # 获取ytt配置的目录
        ytt_config_dir = os.path.join(temp_dir, "ytt_config")
        if not os.path.exists(ytt_config_dir):
            os.makedirs(ytt_config_dir)
        inject_values_path = os.path.join(ytt_config_dir, "inject_bcs_info.yaml")
        with open(inject_values_path, "w") as f:
            f.write(render_to_string("inject_bcs_info.yaml", asdict(bcs_inject_data)))
        ytt_sh_path = os.path.join(ytt_config_dir, YTT_RENDERER_NAME)
        with open(ytt_sh_path, "w") as f:
            # helm post renderer依赖执行命令
            ytt_sh_content = f"#!/bin/bash\n{settings.YTT_BIN} --ignore-unknown-comments -f - -f {ytt_config_dir}/"
            f.write(ytt_sh_content)
        # 确保文件可执行
        os.chmod(ytt_sh_path, stat.S_IRWXU)

        yield chart_dir, ytt_config_dir
