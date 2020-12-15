# -*- coding: utf-8 -*-
from unittest.mock import MagicMock

from django.conf import settings

from backend.bcs_k8s.kubehelm.helm import KubeHelmClient

RELEASE_NAME = "bcs-saas"
NAMESPACE = "test"
CHART_URL = "http://127.0.0.1:8080/charts/bcs-saas-0.1.0.tgz"
OPTIONS = {"--values": ["bcs.yaml", "bcs-saas.yaml"], "--username": "admin", "--password": "admin", "--atomic": None}

settings.HELM3_BIN = "/bin/helm3"


def mock_run_command_with_retry(max_retries, *args, **kwargs):
    assert (
        " ".join(kwargs.get("cmd_args"))
        == f"/bin/helm3 install {RELEASE_NAME} --namespace {NAMESPACE} {CHART_URL} --values bcs.yaml "
        f"--values bcs-saas.yaml --username admin --password admin --atomic"
    )
    return None, None


def test_do_install():
    KubeHelmClient._run_command_with_retry = MagicMock(side_effect=mock_run_command_with_retry)
    client = KubeHelmClient()
    client.do_install_or_upgrade("install", RELEASE_NAME, NAMESPACE, CHART_URL, options=OPTIONS)
