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
import mock

from backend.bcs_k8s import utils
from backend.tests.bcs_mocks.fake_bk_repo import FakeBkRepoMod

fake_chart_data = utils.ChartData(project_name="projectname", repo_name="reponame", chart_name="demo")
fake_repo_auth = utils.RepoAuth(username="admin", password="adminpwd")


@mock.patch("backend.bcs_k8s.utils.BkRepoClient", new=FakeBkRepoMod)
def test_get_chart_version_list():
    version_list = utils.get_chart_version_list(fake_chart_data, fake_repo_auth)
    assert isinstance(version_list, list)


@mock.patch("backend.bcs_k8s.utils.BkRepoClient", new=FakeBkRepoMod)
def test_batch_delete_chart_versions():
    utils.batch_delete_chart_versions(fake_chart_data, fake_repo_auth, ["0.1.0", "0.1.1"])
