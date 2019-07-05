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
import contextlib
import traceback
from dataclasses import dataclass
from rest_framework.exceptions import PermissionDenied

from backend.utils.client import make_kubectl_client, make_kubectl_client_from_kubeconfig
from backend.bcs_k8s.kubectl.exceptions import KubectlError, KubectlExecutionError

logger = logging.getLogger(__name__)


@dataclass
class AppDeployer:
    """ AppDeployEngine manages app's deploy operations
    """
    app: object
    access_token: str
    kubeconfig_content: str = None
    ignore_empty_access_token: bool = False
    extra_inject_source: dict = None

    @contextlib.contextmanager
    def make_kubectl_client(self):
        with make_kubectl_client(
                project_id=self.app.project_id,
                cluster_id=self.app.cluster_id,
                access_token=self.access_token) as (client, err):
            yield client, err

    def install_app(self):
        self.run_with_kubectl("install")

    def uninstall_app(self):
        self.run_with_kubectl("uninstall")

    def run_with_kubectl(self, operation):
        if operation == "uninstall":
            # just load content from release, so that avoid unnecessary render exceptions
            content = self.app.release.content
        else:
            content, _ = self.app.render_app(
                access_token=self.access_token,
                username=self.app.updator,
                ignore_empty_access_token=self.ignore_empty_access_token,
                extra_inject_source=self.extra_inject_source
            )

        if content is None:
            return

        self.update_app_release_content(content)

        if self.access_token:
            with self.make_kubectl_client() as (client, err):
                if err is not None:
                    transitioning_message = "make kubectl client failed, %s" % err
                    self.app.set_transitioning(False, transitioning_message)
                    return
                else:
                    self.run_with_kubectl_core(content, operation, client)
        elif self.ignore_empty_access_token:
            if self.kubeconfig_content:
                with make_kubectl_client_from_kubeconfig(self.kubeconfig_content) as client:
                    self.run_with_kubectl_core(content, operation, client)
            else:
                raise PermissionDenied("api access must supply valid kubeconfig")
        else:
            raise ValueError(self)

    def run_with_kubectl_core(self, content, operation, client):
        transitioning_result = True
        try:
            if operation == "install":
                client.ensure_namespace(self.app.namespace)
                client.apply(
                    template=content,
                    namespace=self.app.namespace
                )
            elif operation == "uninstall":
                client.ensure_namespace(self.app.namespace)
                client.delete_one_by_one(
                    self.app.release.extract_structure(self.app.namespace),
                    self.app.namespace
                )
                # client.delete(template=content, namespace=self.app.namespace)
            else:
                raise ValueError(operation)
        except KubectlExecutionError as e:
            transitioning_result = False
            transitioning_message = (
                "kubectl command execute failed.\n"
                "Error code: {error_no}\nOutput:\n{output}").format(
                error_no=e.error_no,
                output=e.output
            )
            logger.warn(transitioning_message)
        except KubectlError as e:
            transitioning_result = False
            logger.warn(e.message)
            transitioning_message = e.message
        except Exception as e:
            transitioning_result = False
            logger.warning(e.message)
            transitioning_message = self.collect_transitioning_error_message(e)
        else:
            transitioning_result = True
            transitioning_message = "app success %s" % operation

        self.app.set_transitioning(transitioning_result, transitioning_message)

    def collect_transitioning_error_message(self, error):
        return "{error}\n{stack}".format(
            error=error,
            stack=traceback.format_exc()
        )

    def update_app_release_content(self, content):
        release = self.app.release
        release.content = content
        release.save(update_fields=["content"])
        release.refresh_structure(self.app.namespace)
