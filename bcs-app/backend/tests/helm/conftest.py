# -*- coding: utf-8 -*-
from unittest.mock import patch

import pytest

from backend.bcs_k8s.kubehelm.helm import KubeHelmClient


@pytest.fixture(scope="module", autouse=True)
def mock_run_command_with_retry():
    with patch.object(KubeHelmClient, "_run_command_with_retry", return_value=(None, None)) as mock_method:
        yield mock_method
