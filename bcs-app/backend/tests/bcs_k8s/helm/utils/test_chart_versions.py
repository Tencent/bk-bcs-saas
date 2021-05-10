# -*- coding: utf-8 -*-
from datetime import datetime

import pytest

from backend.bcs_k8s.helm.models import chart, repo
from backend.bcs_k8s.helm.utils.chart_versions import update_bcs_chart_records

pytestmark = pytest.mark.django_db

fake_project_id = "project-id"
fake_project_code = "project-code"
fake_versions = ["0.1.0", "0.1.1"]
fake_name = "test"


@pytest.fixture
def create_chart_and_versions():
    repo_obj = repo.Repository.objects.create(name=fake_name)
    chart_obj = chart.Chart.objects.create(name=fake_name, repository=repo_obj)
    for version in fake_versions:
        chart.ChartVersion.objects.create(name=fake_name, version=version, created=datetime.now(), chart=chart_obj)


def test_update_bcs_chart_records(create_chart_and_versions):
    chart_obj = chart.Chart.objects.get(name=fake_name)
    # 删除其中一个版本
    update_bcs_chart_records(fake_project_id, fake_project_code, chart_obj, fake_versions[:1])
    assert chart.Chart.objects.filter(name=fake_name).exists()
    assert chart.ChartVersion.objects.filter(name=fake_name)[0].version == fake_versions[1]
    # 删除chart
    update_bcs_chart_records(fake_project_id, fake_project_code, chart_obj, fake_versions[-1:])
    assert not chart.Chart.objects.filter(name=fake_name).exists()
    assert not chart.ChartVersion.objects.filter(name=fake_name).exists()
