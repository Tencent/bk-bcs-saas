# -*- coding: utf-8 -*-
import pytest


@pytest.fixture
def username():
    return "admin"


@pytest.fixture
def biz_id():
    return 1
