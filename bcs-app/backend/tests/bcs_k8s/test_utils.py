# -*- coding: utf-8 -*-
import mock

from backend.bcs_k8s.utils import batch_delete_chart_versions, get_chart_version_list
from backend.tests.bcs_mocks.fake_bk_repo import FakeBkRepoMod

fake_project_name = "projectname"
fake_repo_name = "reponame"
fake_chart_name = "demo"
fake_username = "admin"
fake_password = "adminpwd"


@mock.patch("backend.bcs_k8s.utils.BkRepoClient", new=FakeBkRepoMod)
def test_get_chart_version_list():
    version_list = get_chart_version_list(
        fake_project_name, fake_repo_name, fake_chart_name, fake_username, fake_password
    )
    assert isinstance(version_list, list)


@mock.patch("backend.bcs_k8s.utils.BkRepoClient", new=FakeBkRepoMod)
def test_batch_delete_chart_versions():
    batch_delete_chart_versions(
        fake_project_name, fake_repo_name, fake_chart_name, ["0.1.0", "0.1.1"], fake_username, fake_password
    )
