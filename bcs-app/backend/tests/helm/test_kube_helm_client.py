# -*- coding: utf-8 -*-
import pytest

from backend.bcs_k8s.kubehelm.helm import KubeHelmClient


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


fake_init_cmd_args = ["helm3", "install", "name", "--namespace", "namespace"]
fake_chart_path = "/chart_path"
fake_values_path = "/values_path"
fake_post_renderer_config_path = "/config_path"
fake_cmd = fake_init_cmd_args + [fake_chart_path, "--post-renderer", f"{fake_post_renderer_config_path}/ytt_renderer"]
fake_cmd_with_values = fake_cmd + ["--values", fake_values_path]


@pytest.mark.parametrize(
    "cmd_flags, expect_args",
    [
        (["--set a=v1"], fake_cmd_with_values + ["--set a=v1"]),
        (["set a=v1"], fake_cmd_with_values + ["--set a=v1"]),
        (["--reuse-values"], fake_cmd + ["--reuse-values"]),
    ],
)
def test_compose_cmd_args(cmd_flags, expect_args):
    client = KubeHelmClient()
    init_cmd_args = fake_init_cmd_args.copy()
    composed_cmd_args = client._compose_cmd_args(
        init_cmd_args, fake_chart_path, fake_values_path, fake_post_renderer_config_path, cmd_flags
    )
    assert composed_cmd_args == expect_args
