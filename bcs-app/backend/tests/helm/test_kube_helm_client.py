# -*- coding: utf-8 -*-
import pytest

from backend.helm.toolkit.kubehelm.helm import KubeHelmClient


def test_do_install(settings, mock_run_command_with_retry):
    release_name = "test-example"
    namespace = "test"
    chart_url = "http://repo.example.com/charts/example-0.1.0.tgz"
    options = [
        {"--values": "bcs.yaml"},
        {"--values": "bcs-saas.yaml"},
        {"--username": "admin"},
        {"--password": "admin"},
        "--atomic",
    ]

    client = KubeHelmClient()
    client.do_install_or_upgrade("install", release_name, namespace, chart_url, options=options)
    mock_run_command_with_retry.assert_called_with(
        max_retries=0,
        cmd_args=[
            settings.HELM3_BIN,
            "install",
            release_name,
            "--namespace",
            namespace,
            chart_url,
            "--values",
            "bcs.yaml",
            "--values",
            "bcs-saas.yaml",
            "--username",
            "admin",
            "--password",
            "admin",
            "--atomic",
        ],
    )
