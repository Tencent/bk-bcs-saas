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
import traceback

from django.db import models
from picklefield.fields import PickledObjectField
from jsonfield import JSONField
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from backend.activity_log.client import get_log_client_by_activity_log_id
from backend.bcs_k8s.helm.models import (Chart, ChartRelease)
from backend.bcs_k8s.helm.constants import KEEP_TEMPLATE_UNCHANGED, DEFAULT_VALUES_FILE_NAME
from backend.bcs_k8s.diff.revision import AppRevisionDiffer
from .managers import AppManager
from .deployer import AppDeployer
from backend.activity_log import client
from . import bcs_info_injector
from backend.bcs_k8s.kubehelm import exceptions as helm_exceptions

logger = logging.getLogger(__name__)


class App(models.Model):
    """App is an instance of templateset
    """
    TRANSITIONING_ACTION_CHOICE = (
        ("noop", "Noop"),
        ("create", "Create"),
        ("update", "Update"),
        ("rollback", "Rollback"),
        ("delete", "Delete"),
    )

    creator = models.CharField(_("创建者"), max_length=32)
    updator = models.CharField(_("更新者"), max_length=32)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    project_id = models.CharField("Project ID", max_length=32)
    cluster_id = models.CharField("Cluster ID", max_length=32)
    chart = models.ForeignKey(Chart, db_constraint=False)
    release = models.ForeignKey(ChartRelease, db_constraint=False)
    name = models.CharField(max_length=128)  # same with namespace in common case
    namespace = models.CharField(max_length=32)
    # namespace_id is a full name of `ns_id`, they indicate the same thing
    namespace_id = models.IntegerField("Namespace ID", db_index=True)

    # design: 变更前设置transitioning_action为对应动作，变更完成设置变更结果
    transitioning_result = models.BooleanField("Transitioning Result", default=True, help_text="transitioning result")
    transitioning_message = models.TextField("Transitioning Messages", help_text="transitioning messages")
    transitioning_action = models.CharField(
        "Transitioning Action",
        max_length=10, default="noop",
        choices=TRANSITIONING_ACTION_CHOICE, help_text="now or latest transitioning action")
    transitioning_on = models.BooleanField("Transitioning On", default=False, help_text="is transitioning now?")

    version = models.CharField("Current Version", max_length=64, null=True, default="")
    # save inject configs as it first render, never update
    # as inject labels shouldn't change (other wise )
    inject_configs = PickledObjectField(null=True, default=None)
    sys_variables = JSONField(null=True, default={})

    # `unique_ns` is used to solve unique_together except cases
    # For example platform provided chartmuseum repo for user projects, it's will be many.
    # We give every chartmuseum repo app a indentified unique_ns, and a common forr the others.
    unique_ns = models.IntegerField(default=0)

    objects = AppManager()

    class Meta:
        db_table = 'bcs_k8s_app'
        unique_together = (("namespace_id", "name", "unique_ns"),)
        index_together = (("namespace_id", "name", "unique_ns"),)

    @property
    def chart_info(self):
        return self.release.chartVersionSnapshot.chart_info

    def get_current_version(self):
        return self.release.chartVersionSnapshot.version

    def get_answers(self):
        return self.release.answers

    def get_customs(self):
        return self.release.customs

    def get_valuefile(self):
        return self.release.valuefile

    def get_valuefile_name(self):
        return self.release.valuefile_name

    def render_context(self):
        return {
            "version": self.get_current_version()
        }

    def render_app(self, username, access_token, ignore_empty_access_token=False, extra_inject_source=None):
        """
        ignore_empty_access_token 用户支持从远程 API 部署, 这种情况无法提供一个有效的 access_token
        目前使用场景：
        1. 为各个项目提供的 chart repo部署
        2. CI/CD

        extra_inject_source 用于提供无 access_token 时, 提供注入需要的数据，不要用于有 access_token 的情况
        """
        try:
            content, notes = self.release.render(namespace=self.namespace)
            content = str(content, encoding="utf-8")
        except helm_exceptions.HelmBaseException as e:
            message = "helm render failed, {}".format(e)
            self.set_transitioning(False, message)
            return None, None
        except Exception as e:
            logger.exception("render app failed, {}".format(e))
            message = "render_app failed, {error}.\n{stack}".format(
                error=e,
                stack=traceback.format_exc()
            )
            self.set_transitioning(False, message)
            return None, None

        # 因为注入的内容中包含动态变化的内容，比如updator等的变动；因此更新后每次渲染
        configs = bcs_info_injector.inject_configs(
            extra_inject_source=extra_inject_source,
            ignore_empty_access_token=ignore_empty_access_token,
            access_token=access_token,
            project_id=self.project_id,
            cluster_id=self.cluster_id,
            namespace_id=self.namespace_id,
            namespace=self.namespace,
            creator=self.creator,
            updator=username,
            created_at=self.created,
            updated_at=self.updated,
            version=self.release.chartVersionSnapshot.version
        )

        # save inject config after update
        self.inject_configs = configs
        self.save(update_fields=["inject_configs"])

        resources_list = bcs_info_injector.parse_manifest(content)
        manager = bcs_info_injector.InjectManager(
            configs=configs,
            resources=resources_list,
            context=self.render_context()
        )
        resources_list = manager.do_inject()
        content = bcs_info_injector.join_manifest(resources_list)
        return content, notes

    def reset_transitioning(self, action):
        self.transitioning_on = True
        self.transitioning_action = action
        self.transitioning_result = True
        self.transitioning_message = ""
        self.updated = timezone.now()
        if not App.objects.filter(id=self.id, transitioning_on=False).update(
                transitioning_on=True,
                transitioning_action=action,
                transitioning_result=True,
                updated=timezone.now(),
                version=self.release.chartVersionSnapshot.version
        ):
            raise ValidationError(detail=_("Helm Release部署中，请稍后再试！"))

        """
        self.save(
            update_fields=[
                "transitioning_result",
                "transitioning_message",
                "transitioning_on",
                "transitioning_action"]
        )
        """

    def set_transitioning(self, result, message):
        self.transitioning_on = False
        self.transitioning_result = result
        self.transitioning_message = message
        self.save(update_fields=["transitioning_result", "transitioning_message", "transitioning_on", "updated"])

    def record_upgrade_app(self, chart_version_id, answers, customs, updator, access_token,
                           valuefile=None, sys_variables=None, valuefile_name=DEFAULT_VALUES_FILE_NAME):
        # operation record
        extra = json.dumps(dict(
            access_token=access_token,
            chart_version_id=chart_version_id,
            answers=answers,
            customs=customs,
            valuefile=valuefile,
            updator=updator,
            sys_variables=sys_variables,
            valuefile_name=valuefile_name,
        ))
        logger_client = client.UserActivityLogClient(
            project_id=self.project_id,
            user=updator,
            resource_type="helm_app",
            activity_type="modify",
            resource=self.name,
            resource_id=self.id,
            extra=extra,
            description="Helm App[{app_name}:{app_id}] upgrade, cluster[{cluster_id}], namespace[{namespace}]".format(
                app_id=self.id,
                app_name=self.name,
                namespace=self.namespace,
                cluster_id=self.cluster_id,
            )
        )
        logger_client.log(activity_status="busy")
        return logger_client

    def first_deploy(self, access_token, activity_log_id, deploy_options):
        from .tasks import first_deploy, sync_or_async

        # if self.transitioning_on:
        #    raise ValidationError("helm app is on transitioning, please try a later.")

        self.reset_transitioning("create")
        sync_or_async(first_deploy)(
            kwargs=dict(
                app_id=self.id,
                access_token=access_token,
                activity_log_id=activity_log_id,
                deploy_options=deploy_options
            )
        )
        return self

    def first_deploy_task(self, access_token, activity_log_id, deploy_options):
        log_client = get_log_client_by_activity_log_id(activity_log_id)
        try:
            AppDeployer(
                app=self,
                access_token=access_token,
                **deploy_options
            ).install_app()
        except Exception as e:
            logger.exception("first deploy app with unexpected error: %s", e)
            self.set_transitioning(False, "unexpected error: %s" % e)
            log_client.update_log(activity_status="failed")
        else:
            activity_status = "succeed" if self.transitioning_result else "failed"
            log_client.update_log(activity_status=activity_status)

    def upgrade_app(self, chart_version_id, answers, customs, updator, access_token, valuefile=None,
                    kubeconfig_content=None, ignore_empty_access_token=None, extra_inject_source=None,
                    sys_variables=None, valuefile_name=DEFAULT_VALUES_FILE_NAME):
        from .tasks import upgrade_app, sync_or_async

        # if self.transitioning_on:
        #    raise ValidationError("helm app is on transitioning, please try a later.")

        self.reset_transitioning("update")
        sync_or_async(upgrade_app)(kwargs={
            "app_id": self.id,
            "chart_version_id": chart_version_id,
            "answers": answers,
            "customs": customs,
            "updator": updator,
            "access_token": access_token,
            "valuefile": valuefile,
            "kubeconfig_content": kubeconfig_content,
            "ignore_empty_access_token": ignore_empty_access_token,
            "extra_inject_source": extra_inject_source,
            "sys_variables": sys_variables,
            "valuefile_name": valuefile_name,
        })
        return self

    def upgrade_app_task(self, chart_version_id, answers, customs, updator, access_token, valuefile=None,
                         kubeconfig_content=None, ignore_empty_access_token=None, extra_inject_source=None,
                         sys_variables=None, valuefile_name=DEFAULT_VALUES_FILE_NAME):
        # make upgrade
        # `chart_version_id` indicate the target chartverion for app,
        # it can also use KEEP_TEMPLATE_UNCHANGED to keep app template unchanged.

        # operation record
        log_client = self.record_upgrade_app(
            chart_version_id, answers, customs, updator, access_token, valuefile, sys_variables, valuefile_name)

        self.release = ChartRelease.objects.make_upgrade_release(
            self, chart_version_id, answers, customs, valuefile=valuefile, valuefile_name=valuefile_name)
        self.version = self.release.chartVersionSnapshot.version
        self.updator = updator
        if sys_variables:
            self.sys_variables = sys_variables
        self.save(update_fields=["release", "updator", "updated", "sys_variables", "version"])

        try:
            AppDeployer(
                app=self,
                access_token=access_token,
                kubeconfig_content=kubeconfig_content,
                ignore_empty_access_token=ignore_empty_access_token,
                extra_inject_source=extra_inject_source,
            ).install_app()
        except Exception as e:
            logger.exception("upgrade_task unexpected error: %s" % e)
            self.set_transitioning(False, "unexpected error: %s" % e)
            log_client.update_log(activity_status="failed")
        else:
            activity_status = "succeed" if self.transitioning_result else "failed"
            log_client.update_log(activity_status=activity_status)

        return self

    def record_rollback_app(self, username, release_id, access_token):
        # operation record
        extra = json.dumps(dict(
            access_token=access_token,
            release_id=release_id,
        ))
        logger_client = client.UserActivityLogClient(
            project_id=self.project_id,
            user=username,
            resource_type="helm_app",
            activity_type="rollback",
            resource=self.name,
            resource_id=self.id,
            extra=extra,
            description="Helm App[{app_name}:{app_id}] rollback, cluster[{cluster_id}], namespace[{namespace}]".format(
                app_id=self.id,
                app_name=self.name,
                namespace=self.namespace,
                cluster_id=self.cluster_id,
            )
        )
        logger_client.log(activity_status="busy")
        return logger_client

    def rollback_app(self, username, release_id, access_token):
        from .tasks import rollback_app, sync_or_async

        # if self.transitioning_on:
        #    raise ValidationError("helm app is on transitioning, please try a later.")

        self.reset_transitioning("rollback")
        sync_or_async(rollback_app)(kwargs={
            "app_id": self.id,
            "access_token": access_token,
            "username": username,
            "release_id": release_id,
        })
        return self

    def rollback_app_task(self, username, release_id, access_token):
        # simple make a copy of release, set release type, then install
        log_client = self.record_rollback_app(
            username=username,
            access_token=access_token,
            release_id=release_id,
        )
        try:
            release = ChartRelease.objects.get(id=release_id)
            self.release = ChartRelease.objects.make_rollback_release(self, release)
            self.version = self.release.chartVersionSnapshot.version
            self.save(update_fields=["release"])
            AppDeployer(app=self, access_token=access_token).install_app()
        except Exception as e:
            logger.exception("rollback_app_task unexpected error: %s", e)
            self.set_transitioning(self, False, "unexpected error: %s" % e)
            log_client.update_log(activity_status="failed")
        else:
            # no exception case app deployer run kubectl will set transitioning
            # no exception case doesn't means success, so don't set transitioning here
            activity_status = "succeed" if self.transitioning_result else "failed"
            log_client.update_log(activity_status=activity_status)

    def get_history_releases(self):
        releases = list(ChartRelease.objects.filter(app_id=self.id)
                        .exclude(id=self.release.id).order_by("-id")
                        .values("id", "chartVersionSnapshot__version", "short_name", "created_at"))
        releases = [dict(id=item["id"],
                         short_name=item["short_name"],
                         version=item["chartVersionSnapshot__version"],
                         created_at=item["created_at"]
                         ) for item in releases]
        return releases

    def get_upgrade_version_selections(self):
        options = list(self.chart.versions.values("id", "version").order_by("-created"))
        release = self.release
        current_version = [{
            "id": KEEP_TEMPLATE_UNCHANGED,
            "version": "(current-%s) %s" % (release.snapshot_state, release.version),
        }]
        options = current_version + options
        return options

    def diff_release(self, release_id):
        release = ChartRelease.objects.get(id=release_id)
        return AppRevisionDiffer(
            app=self,
            revisions=[release],
            suppressed_kinds=[],  # 所有资源类型都比较, 后期不需要的资源类型可以加到列表中
            output_context=-1,  # 显示 diff 完成上下文, 默认值，后期根据需求调整
        ).differentiate()

    def record_destroy(self, username, access_token):
        # operation record
        extra = json.dumps(dict(
            access_token=access_token,
        ))
        logger_client = client.UserActivityLogClient(
            project_id=self.project_id,
            user=username,
            resource_type="helm_app",
            activity_type="delete",
            resource=self.name,
            resource_id=self.id,
            extra=extra,
            description="Helm App[{app_name}:{app_id}] delete, cluster[{cluster_id}], namespace[{namespace}]".format(
                app_id=self.id,
                app_name=self.name,
                namespace=self.namespace,
                cluster_id=self.cluster_id,
            )
        )
        logger_client.log(activity_status="busy")
        return logger_client

    def destroy(self, username, access_token):
        from .tasks import destroy_app, sync_or_async

        # if self.transitioning_on:
        #    raise ValidationError("helm app is on transitioning, please try a later.")

        self.reset_transitioning("delete")
        sync_or_async(destroy_app)(kwargs={
            "app_id": self.id,
            "access_token": access_token,
            "username": username,
        })

    def destroy_app_task(self, username, access_token):
        """ destroy app in cluster, then remove record from db
        """
        # operation record
        log_client = self.record_destroy(username=username, access_token=access_token)

        try:
            AppDeployer(app=self, access_token=access_token).uninstall_app()
        except Exception as e:
            logger.exception("destroy_app_task unexpected result: %s", e)
            log_client.update_log(activity_status="failed")
            self.set_transitioning(False, "uninstall app failed, %s" % e)
            raise e

        activity_status = "succeed" if self.transitioning_result else "failed"
        log_client.update_log(activity_status=activity_status)

        # FIXME currently implementation is so rough,
        # it's better to set app's state to deleting before doing real delete
        if self.transitioning_result is True:
            self.delete()
