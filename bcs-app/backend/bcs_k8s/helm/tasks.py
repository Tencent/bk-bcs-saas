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

import datetime
import logging

from celery import shared_task
from natsort import natsorted

from .models.repo import Repository
from .models.chart import Chart, ChartVersion
from .utils.repo import (prepareRepoIndex, InProcessSign)

logger = logging.getLogger(__name__)


@shared_task
def sync_all_repo():
    for repo in Repository.objects.all():
        try:
            sync_helm_repo(repo.id, False)
        except Exception as e:
            logger.exception("sync_helm_repo %s failed %s" % (repo.id, e))


@shared_task
def force_sync_all_repo():
    for repo in Repository.objects.all():
        try:
            sync_helm_repo(repo.id, True)
        except Exception as e:
            logger.exception("force sync_helm_repo %s failed %s" % (repo.id, e))


@shared_task
def sync_helm_repo(repo_id, force=False):
    # if in processing, then do nothing
    sign = InProcessSign(repo_id)
    # TODO: FIXME: uncomment
    if sign.exists():
        logger.error("the helm repo %s if in processing, this task will not be started", repo_id)
        return

    repo = Repository.objects.get(id=repo_id)
    repo_name = repo.name
    repo_url = repo.url
    plain_auths = repo.plain_auths

    try:
        index, index_hash = prepareRepoIndex(repo_url, repo_name, plain_auths)
    except Exception as e:
        logger.exception("prepareRepoIndex fail: repo_url=%s, repo_name=%s, error: %s", repo_url, repo_name, e)
        return

    logger.debug("prepareRepoIndex repo_url=%s, index=%s", repo_url, index)

    if not index:
        logger.error("load index.yaml from repo fail![name=%s, url=%s]", repo_name, repo_url)
        sign.delete()
        return

    # if the index_hash is the same as the commit in db
    if not force and index_hash == repo.commit:
        logger.info("the index commit [%s] of repo %s not been update since last refresh: %s",
                    repo.commit, repo_id, repo.refreshed_at)
        return

    # apiVersion / generated / entries
    charts = index.get("entries")
    if not charts:
        logger.info("the index of repo %s get no field [entries], please check the %s's format",
                    repo_id, repo_url)
        return

    try:
        _do_helm_repo_charts_update(repo, sign, charts, index_hash, force)
    except Exception as e:
        logger.exception("_do_helm_repo_charts_update fail, error: %s", e)
        sign.delete()


def _update_default_chart_version(chart, full_chart_versions):
    # sort all chart version by field `version` return the latest one
    # ['1.0.1', '1.0.3', '1.0.2'] => '1.0.3'
    # if not versions, don't save chart
    if not full_chart_versions:
        return

    all_versions = [(cv.version, cv) for cv in full_chart_versions.values()]
    # sort reference: https://semver.org/lang/zh-CN/
    # https://stackoverflow.com/questions/2574080/sorting-a-list-of-dot-separated-numbers-like-software-versions
    all_versions = natsorted(all_versions, key=lambda x: x[0])
    _, cv = all_versions[-1]

    chart.defaultChartVersion = cv
    chart.description = cv.description
    chart.save()


def _sync_delete_chart_versions(chart, old_chart_versions, full_chart_versions, to_delete_ids):
    # 1. delete chart version
    for vid in to_delete_ids:
        try:
            old_chart_versions.get(vid).delete()
            # del old_chart_versions[vid]
        except Exception as e:
            logger.exception("sync_helm_repo: delete old chartVersion fail![ChartVersionID=%s], error: %s", vid, e)


def _sync_delete_charts(charts, old_charts):
    current_chart_names = charts.keys()
    to_delete_chart_names = set(old_charts.keys()) - set(current_chart_names)

    for chart_name in to_delete_chart_names:
        c = old_charts[chart_name]
        c.do_delete()


def _get_old_charts(repo):
    charts = Chart.objects.filter(repository=repo).all()
    old_charts_dict = {c.name: c for c in charts}

    return old_charts_dict


def _get_old_chart_version_data(chart, created):
    # if created, no old chart versions
    if created:
        return {}, {}

    versions = ChartVersion.objects.filter(chart=chart).all()

    # {key => id}
    old_chart_version_key_ids = {
        ChartVersion.gen_key(v.name, v.version, v.digest): v.id
        for v in versions
    }
    # {id => object}
    old_chart_versions = {v.id: v for v in versions}

    return old_chart_version_key_ids, old_chart_versions


def _do_helm_repo_charts_update(repo, sign, charts, index_hash, force=False):
    # for sync chart, some chart maybe delete
    old_charts = _get_old_charts(repo)

    for chart_name, versions in charts.items():
        chart, chart_created = Chart.objects.get_or_create(name=chart_name, repository=repo)
        chart.clean_deleted_status()

        # 1. prepare data
        old_chart_version_key_ids, old_chart_versions = _get_old_chart_version_data(chart, chart_created)

        # 2. add or update
        full_chart_versions = {}
        current_chart_version_ids = []
        chart_changed = False
        for version in versions:
            # 2.1 update sign every time
            sign.update()

            # 2.2 create chart version
            key = ChartVersion.gen_key(name=version.get("name"),
                                       version=version.get("version"),
                                       digest=version.get("digest"))
            # do add or update
            chart_version_id = old_chart_version_key_ids.get(key)
            if chart_version_id:
                chart_version = old_chart_versions.get(chart_version_id)
            else:
                chart_version = ChartVersion()

            # 2.3 do update
            try:
                version_changed = chart_version.update_from_import_version(chart, version, force)
            except Exception as e:
                logger.exception(
                    "_save_or_update_chart_version fail: chart=%s, version=%s, error: %s", chart, version, e)
                continue
            else:
                chart_changed = chart_changed or version_changed

            current_chart_version_ids.append(chart_version.id)
            full_chart_versions[chart_version.id] = chart_version

            # 2.4 update icon  NOTE: icon just add at the first time
            icon_url = version.get("icon")
            if not chart.icon and icon_url:
                chart.update_icon(icon_url)

        if chart_changed:
            chart.changed_at = datetime.datetime.now()  # update chart's updated_at whenever a chartversion changed
            chart.save(update_fields=["changed_at"])

        # 3. chartVersion sync delete
        to_delete_ids = set(old_chart_versions.keys()) - set(current_chart_version_ids)
        _sync_delete_chart_versions(chart, old_chart_versions, full_chart_versions, to_delete_ids)

        # update chart.DefaultChartVersion if the target cv been deleted
        _update_default_chart_version(chart, full_chart_versions)

    # sync chart
    _sync_delete_charts(charts, old_charts)

    # update refreshed_at and commit
    repo.refreshed(index_hash)

    # delete sign
    sign.delete()
