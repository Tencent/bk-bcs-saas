# -*- coding: utf-8 -*-
import pytest

from backend.bcs_k8s.kubehelm.options import Options

init_options1 = [{"--set": "a=1,b=2"}, {"--values": "data.yaml"}]
flag1 = "--debug"
expect_options1 = ["--set", "a=1,b=2", "--values", "data.yaml", "--debug"]

init_options2 = [{"--set": "a=1,b=2"}, {"--values": "data.yaml"}, {"--debug": False}]
flag2 = {"--reuse-values": True}
expect_options2 = ["--set", "a=1,b=2", "--values", "data.yaml", "--reuse-values"]

init_options3 = ["--set", "a=1,b=2", "--values", "data.yaml", "--debug"]
flag3 = "--reuse-values"
expect_options3 = ["--set", "a=1,b=2", "--values", "data.yaml", "--debug", "--reuse-values"]


@pytest.mark.parametrize(
    "init_options, flag, expect_options",
    [
        (init_options1, flag1, expect_options1),
        (init_options2, flag2, expect_options2),
        (init_options3, flag3, expect_options3),
    ],
)
def test_options_lines(init_options, flag, expect_options):
    opts = Options(init_options)
    opts.add(flag)
    assert opts.options() == expect_options
